import json
import time
import random
import pandas as pd
import re
import os
from mistralai import Mistral

from dotenv import load_dotenv
load_dotenv()

# ========= PARAMÈTRES ==========
MODEL = os.getenv("MODEL", "mistral-small-latest")
API_KEY = os.getenv("API_KEY")

MAX_RETRIES = 2
SUCCESS_PAUSE_SEC = 0.1
BACKOFF_BASE_SEC = 1
BACKOFF_JITTER_SEC = (0, 0.5)

# Regex JSON NON-GOURMANDE (fallback)
BRACES = re.compile(r"\{.*?\}", re.DOTALL)

# ========= UTILS ==========

def load_prompt(path: str) -> str:
    """Charge un prompt texte brut."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def extract_json(text: str):
    """
    Essaye de parser la réponse du LLM comme JSON :
    - enlève les éventuelles balises ```json
    - tente json.loads sur le texte complet
    - sinon, fallback sur le premier bloc {...}
    """
    if not text:
        return None

    text = text.strip()

    # Enlever ```json ... ``` si présent
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # Tentative 1 : JSON direct
    try:
        return json.loads(text)
    except Exception:
        pass

    # Tentative 2 : premier bloc {...}
    m = BRACES.search(text)
    if not m:
        return None
    candidate = m.group(0)
    try:
        return json.loads(candidate)
    except Exception:
        return None

def call_llm_with_retry(client, prompt: str) -> str:
    """Appel LLM avec retry léger + backoff."""
    for attempt in range(MAX_RETRIES):
        try:
            res = client.chat.complete(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=256,
                stream=False
            )
            return res.choices[0].message.content

        except Exception as e:
            s = str(e).lower()

            # Capacité max du modèle — inutile de retenter
            if "service tier capacity exceeded" in s or "3505" in s:
                print("❌ Capacité du service atteinte pour ce modèle. Pas de retry.")
                raise

            # Rate limit — on retente légèrement
            if ("429" in s or "too many" in s) and attempt < MAX_RETRIES - 1:
                delay = BACKOFF_BASE_SEC * (2 ** attempt) + random.uniform(*BACKOFF_JITTER_SEC)
                print(f"⏳ Retry dans {delay:.1f}s... (429 reçu)")
                time.sleep(delay)
                continue

            raise

# ============================================================================
# CONSTRUCTION DU PROMPT COMBINÉ (1 APPEL LLM)
# ============================================================================

def build_master_prompt(sentiment_prompt: str,
                        theme_prompt: str,
                        urgence_prompt: str,
                        tweet: str) -> str:
    """
    Combine les 3 prompts + le tweet, et impose un format JSON unique.
    IMPORTANT : les fichiers .txt ne doivent PAS contenir {tweet}, le tweet est ajouté ici.
    """
    return f"""
Tu es un modèle d'analyse de tweets pour un opérateur télécom.

Tu dois analyser le tweet ci-dessous selon trois axes :
1) Sentiment
2) Thème
3) Niveau d'urgence

Consignes pour chaque axe :

[SENTIMENT]
{sentiment_prompt}

[THÈME]
{theme_prompt}

[URGENCE]
{urgence_prompt}

Tweet à analyser :
\"\"\"{tweet}\"\"\"

Réponds STRICTEMENT au format JSON suivant, sans texte avant ni après, sans balises ``` :

{{
  "sentiment": {{
    "label": "<valeur du sentiment>",
    "score": <un nombre entre 0 et 1>
  }},
  "theme": {{
    "label": "<valeur du thème>",
    "score": <un nombre entre 0 et 1>
  }},
  "urgence": {{
    "label": <entier 0, 1 ou 2>,
    "score": <un nombre entre 0 et 1>
  }}
}}
""".strip()

# ============================================================================
# CLASSIFICATION D'UN SEUL TWEET (1 APPEL LLM)
# ============================================================================

def classify_single_tweet_one_call(client,
                                   tweet: str,
                                   sentiment_prompt: str,
                                   theme_prompt: str,
                                   urgence_prompt: str):
    """
    Un seul appel LLM qui renvoie un JSON de la forme :
    {
      "sentiment": {"label": "...", "score": 0.x},
      "theme":     {"label": "...", "score": 0.x},
      "urgence":   {"label": 0/1/2, "score": 0.x}
    }
    """

    master_prompt = build_master_prompt(
        sentiment_prompt,
        theme_prompt,
        urgence_prompt,
        tweet
    )

    raw = call_llm_with_retry(client, master_prompt)
    parsed = extract_json(raw)

    # Valeurs par défaut
    sentiment = {"label": "neutre", "score": 0.0}
    theme = {"label": "Autre", "score": 0.0}
    urgence = {"label": 0, "score": 0.0}

    if isinstance(parsed, dict):
        # Sentiment
        if isinstance(parsed.get("sentiment"), dict):
            s = parsed["sentiment"]
            sentiment["label"] = s.get("label", sentiment["label"])
            try:
                sentiment["score"] = float(s.get("score", sentiment["score"]))
            except Exception:
                pass

        # Thème
        if isinstance(parsed.get("theme"), dict):
            t = parsed["theme"]
            theme["label"] = t.get("label", theme["label"])
            try:
                theme["score"] = float(t.get("score", theme["score"]))
            except Exception:
                pass

        # Urgence
        if isinstance(parsed.get("urgence"), dict):
            u = parsed["urgence"]
            urgence["label"] = u.get("label", urgence["label"])
            try:
                urgence["score"] = float(u.get("score", urgence["score"]))
            except Exception:
                pass

    # Confiance globale
    global_conf = round(
        0.333 * sentiment["score"] +
        0.333 * theme["score"] +
        0.333 * urgence["score"],
        4
    )

    return {
        "tweet": tweet,
        "sentiment": sentiment["label"],
        "sentiment_score": sentiment["score"],
        "theme": theme["label"],
        "theme_score": theme["score"],
        "urgence": urgence["label"],
        "urgence_score": urgence["score"],
        "confiance": global_conf
    }

# ============================================================================
# FONCTION PRINCIPALE : CLASSIFIER UN FICHIER COMPLET
# ============================================================================

def classify_tweet_file_one_call(csv_path: str, output_path: str, api_key: str):

    print(f"📂 Chargement du CSV : {csv_path}")
    df = pd.read_csv(csv_path)

    if "id" not in df.columns or "tweet" not in df.columns:
        raise ValueError("❌ Le CSV doit contenir les colonnes 'id' et 'tweet'")

    print(f"✅ {len(df)} lignes chargées.")

    # Chargement des 3 prompts (SANS {tweet} dedans)
    sentiment_prompt = load_prompt("Prompt-files/prompt-sentiment.txt")
    theme_prompt = load_prompt("Prompt-files/prompt-theme.txt")
    urgence_prompt = load_prompt("Prompt-files/prompt-urgence.txt")

    results = []

    with Mistral(api_key=api_key) as client:
        for i, row in enumerate(df.itertuples(index=False), start=1):
            tweet_id = row.id
            tweet_text = str(row.tweet)

            print(f"▶ [{i}/{len(df)}] Analyse (1 appel) tweet {tweet_id} ...")

            try:
                r = classify_single_tweet_one_call(
                    client,
                    tweet_text,
                    sentiment_prompt,
                    theme_prompt,
                    urgence_prompt
                )
                r["tweet_id"] = tweet_id

            except Exception as e:
                print(f"⚠️ Erreur tweet {tweet_id}: {e}")
                r = {
                    "tweet_id": tweet_id,
                    "tweet": tweet_text,
                    "sentiment": "neutre",
                    "sentiment_score": 0.0,
                    "theme": "Autre",
                    "theme_score": 0.0,
                    "urgence": 0,
                    "urgence_score": 0.0,
                    "confiance": 0.0
                }

            results.append(r)
            time.sleep(SUCCESS_PAUSE_SEC)

    print(f"\n💾 Sauvegarde des résultats dans : {output_path}")
    pd.DataFrame(results).to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✅ Fichier écrit avec {len(results)} lignes.")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    INPUT_CSV = "LLM-classified-data/LLM - DATA copy.csv"
    OUTPUT_CSV = "LLM-classified-data/tweets_classified_one_call.csv"

    print("🚀 Lancement de la classification (1 appel LLM / tweet)...")
    classify_tweet_file_one_call(INPUT_CSV, OUTPUT_CSV, API_KEY)
    print("🎉 Terminé ! Fichier généré :", OUTPUT_CSV)
