"""
Tests unitaires et d'intégration pour le pipeline d'analyse de tweets SAV.

Pré-requis :
- ton script principal est dans un fichier `tweets_pipeline.py`
  contenant au moins :
    - extract_json
    - call_llm_with_retry
    - classify_single_tweet
    - classify_tweet_file
    - BATCH_SIZE (optionnel)

Commandes :
    pytest -q
"""

import json
import os
import pandas as pd
import pytest
import classify_tweets as ct 
# ============================================================
# TESTS UNITAIRES : extract_json
# ============================================================

def test_extract_json_valid_simple():
    text = '{"label": "positif", "score": 0.9}'
    parsed = ct.extract_json(text)
    assert isinstance(parsed, dict)
    assert parsed["label"] == "positif"
    assert parsed["score"] == 0.9


def test_extract_json_with_code_block():
    text = """```json
{
  "label": "neutre",
  "score": 0.5
}
```"""
    parsed = ct.extract_json(text)
    assert isinstance(parsed, dict)
    assert parsed["label"] == "neutre"
    assert parsed["score"] == 0.5


def test_extract_json_invalid_returns_none():
    text = "ceci n'est pas du JSON"
    parsed = ct.extract_json(text)
    assert parsed is None


def test_extract_json_empty_returns_none():
    assert ct.extract_json("") is None
    assert ct.extract_json(None) is None


# ============================================================
# TESTS UNITAIRES : call_llm_with_retry
# (on mock le client et time.sleep)
# ============================================================

class FakeChatSuccessful:
    def __init__(self, content="OK"):
        self._content = content

    class _Message:
        def __init__(self, content):
            self.content = content

    class _Choice:
        def __init__(self, content):
            self.message = FakeChatSuccessful._Message(content)

    def complete(self, *args, **kwargs):
        # Simule une réponse minimale de l'API Mistral
        return type("Resp", (), {"choices": [FakeChatSuccessful._Choice(self._content)]})


class FakeClientSuccessful:
    def __init__(self, content="OK"):
        self.chat = FakeChatSuccessful(content=content)


def test_call_llm_with_retry_success(monkeypatch):
    client = FakeClientSuccessful(content="YOLO")
    # on s'assure qu'aucune pause ne ralentit les tests
    monkeypatch.setattr(ct.time, "sleep", lambda s: None)

    out = ct.call_llm_with_retry(client, "prompt quelconque")
    assert out == "YOLO"


class FakeClientRetry429:
    def __init__(self):
        self.chat = self
        self.call_count = 0

    def complete(self, *args, **kwargs):
        self.call_count += 1
        if self.call_count == 1:
            raise Exception("429 Too Many Requests")
        return type(
            "Resp", (),
            {"choices": [type("Choice", (), {"message": type("Msg", (), {"content": "OK_RETRY"})})]}
        )


def test_call_llm_with_retry_429_then_success(monkeypatch):
    client = FakeClientRetry429()
    monkeypatch.setattr(ct.time, "sleep", lambda s: None)

    out = ct.call_llm_with_retry(client, "prompt 429")
    assert out == "OK_RETRY"
    # on vérifie qu'il y a bien eu deux appels
    assert client.call_count == 2


class FakeClientCapacityError:
    def __init__(self):
        self.chat = self
        self.call_count = 0

    def complete(self, *args, **kwargs):
        self.call_count += 1
        raise Exception("service tier capacity exceeded: code 3505")


def test_call_llm_with_retry_capacity_error_no_retry(monkeypatch):
    client = FakeClientCapacityError()
    monkeypatch.setattr(ct.time, "sleep", lambda s: None)

    with pytest.raises(Exception):
        ct.call_llm_with_retry(client, "prompt capacity")

    # devrait s'arrêter au premier appel
    assert client.call_count == 1


# ============================================================
# TESTS UNITAIRES : classify_single_tweet
# (on monkeypatch ct.call_llm_with_retry)
# ============================================================

def test_classify_single_tweet_happy_path(monkeypatch):
    """
    On simule 3 réponses LLM JSON correctes
    pour sentiment / thème / urgence.
    """

    def fake_call_llm(client, prompt: str):
        # on discrimine en fonction du contenu du prompt
        if "SENTIMENT" in prompt:
            return json.dumps({"label": "positif", "score": 0.9})
        if "THEME" in prompt:
            return json.dumps({"label": "facturation", "score": 0.8})
        if "URGENCE" in prompt:
            return json.dumps({"label": 2, "score": 0.7})
        return json.dumps({"label": "neutre", "score": 0.0})

    monkeypatch.setattr(ct, "call_llm_with_retry", fake_call_llm)

    client = object()  # pas utilisé par fake_call_llm
    tweet = "Super service, merci Free 😄"

    res = ct.classify_single_tweet(
        client,
        tweet,
        sentiment_prompt="SENTIMENT PROMPT",
        theme_prompt="THEME PROMPT",
        urgence_prompt="URGENCE PROMPT",
    )

    assert res["tweet"] == tweet
    assert res["sentiment"] == "positif"
    assert res["theme"] == "facturation"
    assert res["urgence"] == 2
    assert 0.0 <= res["confiance"] <= 1.0


def test_classify_single_tweet_default_values_on_bad_json(monkeypatch):
    """
    Si extract_json renvoie None, on doit retomber
    sur les valeurs par défaut définies dans classify_single_tweet.
    """

    def fake_call_llm(client, prompt: str):
        return "ceci n'est pas du JSON"

    monkeypatch.setattr(ct, "call_llm_with_retry", fake_call_llm)
    monkeypatch.setattr(ct, "extract_json", lambda text: None)

    client = object()
    tweet = "Je ne comprends pas la facture"

    res = ct.classify_single_tweet(
        client,
        tweet,
        sentiment_prompt="SENTIMENT PROMPT",
        theme_prompt="THEME PROMPT",
        urgence_prompt="URGENCE PROMPT",
    )

    assert res["sentiment"] == "neutre"
    assert res["sentiment_score"] == 0.0
    assert res["theme"] == "Autre"
    assert res["theme_score"] == 0.0
    assert res["urgence"] == 0
    assert res["urgence_score"] == 0.0
    assert res["confiance"] == 0.0


# ============================================================
# TEST D'INTÉGRATION : pipeline complet sur mini CSV
# (traitement par batch, mock Mistral, fichiers réels)
# ============================================================

class FakeMistralClientCtx:
    """
    Fake du client Mistral pour être utilisé dans :
        with Mistral(api_key=...) as client:
    On ne l'utilise pas vraiment car call_llm_with_retry est mocké.
    """
    def __init__(self, api_key=None):
        self.api_key = api_key

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass


def test_classify_tweet_file_integration(tmp_path, monkeypatch):
    """
    Test d'intégration :
    - crée un petit CSV en entrée
    - mock load_prompt + call_llm_with_retry + Mistral
    - vérifie que le fichier de sortie est généré avec le bon nombre de lignes.
    """

    # 1) Création d'un mini CSV d'entrée
    input_csv = tmp_path / "input.csv"
    df_in = pd.DataFrame(
        [
            {"id": 1, "tweet": "Free ça marche super, merci 😄"},
            {"id": 2, "tweet": "Encore une panne fibre, j'en peux plus 😡"},
            {"id": 3, "tweet": "help"},
        ]
    )
    df_in.to_csv(input_csv, index=False)

    output_csv = tmp_path / "output.csv"

    # 2) Mock des prompts (on évite d'ouvrir de vrais fichiers)
    monkeypatch.setattr(ct, "load_prompt", lambda path: "PROMPT")

    # 3) Mock de call_llm_with_retry pour renvoyer un JSON constant
    def fake_call_llm(client, prompt: str):
        # On renvoie toujours un JSON neutre pour simplifier
        if "URGENCE" in prompt:
            return json.dumps({"label": 1, "score": 0.5})
        return json.dumps({"label": "neutre", "score": 0.5})

    monkeypatch.setattr(ct, "call_llm_with_retry", fake_call_llm)

    # 4) Mock du client Mistral pour éviter tout appel réseau
    monkeypatch.setattr(ct, "Mistral", FakeMistralClientCtx)

    # 5) On désactive les sleep pour accélérer les tests
    monkeypatch.setattr(ct.time, "sleep", lambda s: None)

    # 6) Exécution du pipeline
    ct.classify_tweet_file(str(input_csv), str(output_csv), api_key="DUMMY")

    # 7) Vérifications
    assert output_csv.exists()

    df_out = pd.read_csv(output_csv)
    # 3 tweets -> 3 lignes dans les résultats (même si certains sont peu informatifs)
    assert len(df_out) == 3

    expected_cols = {
        "tweet_id",
        "tweet",
        "sentiment",
        "sentiment_score",
        "theme",
        "theme_score",
        "urgence",
        "urgence_score",
        "confiance",
    }
    assert expected_cols.issubset(df_out.columns)


# ============================================================
# TEST FONCTIONNEL : vérification du BATCH_SIZE
# ============================================================

def test_batch_processing_respects_batch_size(tmp_path, monkeypatch):
    """
    Vérifie que classify_tweet_file traite tous les tweets
    même quand le nombre total n'est pas multiple de BATCH_SIZE.
    """

    # On force un BATCH_SIZE de 4 pour ce test
    monkeypatch.setattr(ct, "BATCH_SIZE", 4)

    # Dataset de 10 tweets
    input_csv = tmp_path / "input_batch.csv"
    df_in = pd.DataFrame(
        [{"id": i, "tweet": f"tweet {i}"} for i in range(10)]
    )
    df_in.to_csv(input_csv, index=False)

    output_csv = tmp_path / "output_batch.csv"

    # Mock des prompts + client + call_llm_with_retry
    monkeypatch.setattr(ct, "load_prompt", lambda path: "PROMPT")

    def fake_call_llm(client, prompt: str):
        return json.dumps({"label": "test", "score": 0.5})

    monkeypatch.setattr(ct, "call_llm_with_retry", fake_call_llm)
    monkeypatch.setattr(ct, "Mistral", FakeMistralClientCtx)
    monkeypatch.setattr(ct.time, "sleep", lambda s: None)

    ct.classify_tweet_file(str(input_csv), str(output_csv), api_key="DUMMY")

    assert output_csv.exists()
    df_out = pd.read_csv(output_csv)
    assert len(df_out) == 10
