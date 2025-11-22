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

MAX_RETRIES = 5
SUCCESS_PAUSE_SEC = 1.0
BACKOFF_BASE_SEC = 2
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))

# Regex JSON robuste
JSON_BLOCK = re.compile(r"\{[\s\S]*?\}", re.MULTILINE)

# ========= UTILS ==========

def load_prompt(path: str) -> str:
    """Charge un prompt texte."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def extract_json(text: str):
    """
    Extraction JSON robuste :
    - essai direct
    - fallback sur blocs {...}
    """
    if not text:
        return None

    text = text.strip()

    # Tentative directe
    try:
        return json.loads(text)
    except:
        pass

    # Recherche de tous les blocs JSON
    blocks = JSON_BLOCK.findall(text)
    for b in blocks:
        try:
            return json.loads(b)
        except:
            pass

    return None


def call_llm_with_retry(client, prompt: str) -> str:
    """Appel LLM avec retry + rôle system pour forcer JSON."""

    for attempt in range(MAX_RETRIES):
        try:
            res = client.chat.complete(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Tu es un modèle strict. "
                            "Tu dois répondre EXCLUSIVEMENT en JSON valide. "
                            "Aucun texte autour."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200,
                stream=False
            )
            return res.choices[0].message.content

        except Exception as e:
            s = str(e).lower()

            # Rate limit
            if ("429" in s or "too many" in s) and attempt < MAX_RETRIES - 1:
                delay = BACKOFF_BASE_SEC * (2 ** attempt)
                print(f"⏳ Retry dans {delay:.1f}s... (429 reçu)")
                time.sleep(delay)
                continue

            raise


# =====================================================================
# CLASSIFICATION D’UN TWEET (3 appels)
# =====================================================================

def classify_single_tweet(client, tweet: str,
                          sentiment_prompt: str,
                          theme_prompt: str,
                          urgence_prompt: str):

    def normalize(parsed, default_label, default_score=0.0):
        """Sécurise le parsing JSON."""
        if not isinstance(parsed, dict):
            return {"label": default_label, "score": default_score}

        label = parsed.get("label", default_label)

        try:
            score = float(parsed.get("score", default_score))
        except:
            score = default_score

        return {"label": label, "score": score}

    # SENTIMENT
    sent_prompt_full = sentiment_prompt.replace("{tweet}", tweet)
    sent_raw = call_llm_with_retry(client, sent_prompt_full)
    sent_json = normalize(extract_json(sent_raw), "neutre")

    # THEME
    theme_prompt_full = theme_prompt.replace("{tweet}", tweet)
    theme_raw = call_llm_with_retry(client, theme_prompt_full)
    theme_json = normalize(extract_json(theme_raw), "autre")

    # URGENCE
    urg_prompt_full = urgence_prompt.replace("{tweet}", tweet)
    urg_raw = call_llm_with_retry(client, urg_prompt_full)
    urg_json = normalize(extract_json(urg_raw), 0)

    # SCORE GLOBAL
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


# =====================================================================
# TRAITEMENT PAR BATCH
# =====================================================================

def classify_tweet_file(csv_path: str, output_path: str, api_key: str):

    print(f"📂 Chargement du CSV : {csv_path}")
    df = pd.read_csv(csv_path)

    if "id" not in df.columns or "tweet" not in df.columns:
        raise ValueError("❌ Le CSV doit contenir les colonnes 'id' et 'tweet'")

    total = len(df)
    print(f"✅ {total} lignes chargées.")
    print(f"🔄 Traitement par batch de {BATCH_SIZE} tweets.")

    # Chargement des prompts
    sentiment_prompt = load_prompt("Prompt-files/prompt-sentiment.txt")
    theme_prompt = load_prompt("Prompt-files/prompt-theme.txt")
    urgence_prompt = load_prompt("Prompt-files/prompt-urgence.txt")

    # Suppression de l'ancien fichier
    if os.path.exists(output_path):
        os.remove(output_path)

    with Mistral(api_key=api_key) as client:
        batch_index = 0

        for start in range(0, total, BATCH_SIZE):
            end = min(start + BATCH_SIZE, total)
            batch_index += 1

            print(f"\n📦 Batch {batch_index} : lignes {start+1} à {end} / {total}")

            batch_df = df.iloc[start:end]
            batch_results = []

            for i, row in enumerate(batch_df.itertuples(index=False), start=start+1):
                tweet_id = row.id
                tweet_text = str(row.tweet)

                print(f"▶ [{i}/{total}] Analyse tweet {tweet_id} ...")

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
                    print(f"⚠ Erreur tweet {tweet_id}: {e}")
                    r = {
                        "tweet_id": tweet_id,
                        "tweet": tweet_text,
                        "sentiment": "neutre",
                        "sentiment_score": 0.0,
                        "theme": "autre",
                        "theme_score": 0.0,
                        "urgence": 0,
                        "urgence_score": 0.0,
                        "confiance": 0.0
                    }

                batch_results.append(r)
                time.sleep(SUCCESS_PAUSE_SEC)

            df_batch_res = pd.DataFrame(batch_results)

            write_header = not os.path.exists(output_path)
            df_batch_res.to_csv(
                output_path,
                mode="a",
                index=False,
                encoding="utf-8-sig",
                header=write_header
            )

            print(f"💾 Batch {batch_index} sauvegardé ({len(batch_results)} lignes).")

    print(f"\n✅ Tous les batches sont traités.")
    print(f"💾 Résultats finaux dans : {output_path}")


# =====================================================================
# MAIN
# =====================================================================

if __name__ == "__main__":

    INPUT_CSV = "LLM-classified-data/tweets_free_cleaned.csv"
    OUTPUT_CSV = "LLM-classified-data/tweets_classified.csv"

    print("🚀 Lancement de la classification...")
    classify_tweet_file(INPUT_CSV, OUTPUT_CSV, API_KEY)
    print("🎉 Terminé ! Fichier généré :", OUTPUT_CSV)
