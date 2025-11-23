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
MODEL = os.getenv("MODEL", "mistral-large-2411")
API_KEY = os.getenv("API_KEY")

# Pour aller vite mais rester un minimum safe
MAX_RETRIES = 2
SUCCESS_PAUSE_SEC = 0.3   # petite pause entre tweets
BACKOFF_BASE_SEC = 1
BACKOFF_JITTER_SEC = (0, 0.5)

# Regex JSON NON-GOURMANDE
BRACES = re.compile(r"\{.*?\}", re.DOTALL)

# ========= UTILS ==========

def load_prompt(path: str) -> str:
    """Charge un prompt texte."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def extract_json(text: str):
    """
    Essaye de parser la réponse du LLM comme JSON :
    - enlève les éventuelles balises ```json
    - tente json.loads sur le texte complet
    - fallback sur le premier bloc {...}
    """
    if not text:
        return None

    text = text.strip()

    # Enlever ```json ... ``` si présent
    if text.startswith("```"):
        lines = text.splitlines()
        if lines:
            if lines[0].startswith("```"):
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
                max_tokens=200,
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
# FONCTION : CLASSIFIER UN SEUL TWEET (3 APPELS LLM)
# ============================================================================

def classify_single_tweet(client, tweet: str,
                          sentiment_prompt: str,
                          theme_prompt: str,
                          urgence_prompt: str):
    """
    Utilise 3 prompts distincts (sentiment / thème / urgence),
    chacun renvoyant un JSON du type : { "label": "...", "score": 0.x }
    """

    # Pour garantir que le tweet est TOUJOURS dans le prompt
    def build_prompt(base_prompt: str, tweet: str) -> str:
        if "{tweet}" in base_prompt:
            return base_prompt.replace("{tweet}", tweet)
        return f"{base_prompt}\n\nTweet à analyser : {tweet}"

    def normalize(parsed, default_label, default_score=0.0):
        """Normalise en {label, score} avec valeurs par défaut."""
        if not isinstance(parsed, dict):
            return {"label": default_label, "score": default_score}

        label = parsed.get("label", default_label)
        score_raw = parsed.get("score", default_score)

        try:
            score = float(score_raw)
        except Exception:
            score = default_score

        return {"label": label, "score": score}

    # --- Sentiment ---
    sent_prompt_f = build_prompt(sentiment_prompt, tweet)
    sent_raw = call_llm_with_retry(client, sent_prompt_f)
    sent_json = normalize(extract_json(sent_raw), default_label="neutre")

    # --- Thème ---
    theme_prompt_f = build_prompt(theme_prompt, tweet)
    theme_raw = call_llm_with_retry(client, theme_prompt_f)
    theme_json = normalize(extract_json(theme_raw), default_label="Autre")

    # --- Urgence ---
    urg_prompt_f = build_prompt(urgence_prompt, tweet)
    urg_raw = call_llm_with_retry(client, urg_prompt_f)
    urg_json = normalize(extract_json(urg_raw), default_label=0)

    # --- Confiance globale ---
    global_conf = round(
        0.333 * sent_json["score"] +
        0.333 * theme_json["score"] +
        0.333 * urg_json["score"],
        4
    )

    return {
        "tweet": tweet,
        "sentiment": sent_json["label"],
        "sentiment_score": sent_json["score"],
        "theme": theme_json["label"],
        "theme_score": theme_json["score"],
        "urgence": urg_json["label"],
        "urgence_score": urg_json["score"],
        "confiance": global_conf
    }


# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def classify_tweet_file(csv_path: str, output_path: str, api_key: str):

    print(f"📂 Chargement du CSV : {csv_path}")
    df = pd.read_csv(csv_path)

    if "id" not in df.columns or "tweet" not in df.columns:
        raise ValueError("❌ Le CSV doit contenir les colonnes 'id' et 'tweet'")

    print(f"✅ {len(df)} lignes chargées.")

    # Chargement des 3 prompts
    sentiment_prompt = load_prompt("Prompt-files/prompt-sentiment.txt")
    theme_prompt = load_prompt("Prompt-files/prompt-theme.txt")
    urgence_prompt = load_prompt("Prompt-files/prompt-urgence.txt")

    results = []

    with Mistral(api_key=api_key) as client:
        for i, row in enumerate(df.itertuples(index=False), start=1):
            tweet_id = row.id
            tweet_text = str(row.tweet)

            print(f"▶ [{i}/{len(df)}] Analyse tweet {tweet_id} ...")

            try:
                r = classify_single_tweet(
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

    INPUT_CSV = "LLM-classified-data/LLM - DATA.csv"
    OUTPUT_CSV = "LLM-classified-data/tweets_classified.csv"

    print("🚀 Lancement de la classification...")
    classify_tweet_file(INPUT_CSV, OUTPUT_CSV, API_KEY)
    print("🎉 Terminé ! Fichier généré :", OUTPUT_CSV)
    print("🎉 Terminé ! Fichier généré :", OUTPUT_CSV)
