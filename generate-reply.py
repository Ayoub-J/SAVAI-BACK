import time
import random
import pandas as pd
import os
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("MODEL", "mistral-large-2411")
API_KEY = os.getenv("API_KEY")

MAX_RETRIES = 2
BACKOFF_BASE_SEC = 1
BACKOFF_JITTER_SEC = (0, 0.5)


def load_prompt(path: str) -> str:
    """Charge un prompt texte depuis un fichier."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def call_llm_with_retry(client, prompt: str) -> str:
    """Appel LLM robuste mais léger avec retry."""
    for attempt in range(MAX_RETRIES):
        try:
            res = client.chat.complete(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,   # un peu de créativité dans la réponse
                max_tokens=200,
                stream=False
            )
            return res.choices[0].message.content

        except Exception as e:
            s = str(e).lower()
            if ("429" in s or "too many" in s) and attempt < MAX_RETRIES - 1:
                delay = BACKOFF_BASE_SEC * (2**attempt) + random.uniform(*BACKOFF_JITTER_SEC)
                print(f"⏳ Retry dans {delay:.1f}s...")
                time.sleep(delay)
                continue
            raise


def build_reply_prompt(base_prompt: str,
                       tweet: str,
                       sentiment: str,
                       theme: str,
                       urgence) -> str:
    """
    Injecte toutes les variables nécessaires dans le prompt de réponse.
    """
    return (
        base_prompt
        .replace("{tweet}", str(tweet))
        .replace("{sentiment}", str(sentiment))
        .replace("{theme}", str(theme))
        .replace("{urgence}", str(urgence))
    )


# ============================================================
#   ✨ NOUVELLE FONCTION demandée : generate_reply_for_tweet ✨
# ============================================================

def generate_reply_for_tweet(client, reply_prompt_base: str, row) -> str:
    """
    Construit le prompt final et génère la réponse Free pour un tweet.
    (Ancien nom : generate_reply_for_row)
    """
    prompt = build_reply_prompt(
        reply_prompt_base,
        row.tweet,
        row.sentiment,
        row.theme,
        row.urgence,
    )

    raw = call_llm_with_retry(client, prompt)
    return raw.strip()


# ============================================================
#        GENERATION DES RÉPONSES POUR UN FICHIER COMPLET
# ============================================================

def generate_replies_for_file(classified_csv: str, output_csv: str, api_key: str):
    print(f"📂 Chargement du CSV classifié : {classified_csv}")
    df = pd.read_csv(classified_csv)

    required = ["tweet_id", "tweet", "sentiment", "theme", "urgence"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"❌ Le CSV doit contenir les colonnes {required}. Colonnes manquantes : {missing}"
        )

    reply_prompt = load_prompt("Prompt-files/prompt-response.txt")

    rows_out = []

    with Mistral(api_key=api_key) as client:
        for i, row in enumerate(df.itertuples(index=False), start=1):
            print(f"▶ Génération réponse pour tweet {row.tweet_id} ({i}/{len(df)})")

            try:
                reply_text = generate_reply_for_tweet(client, reply_prompt, row)
            except Exception as e:
                print(f"⚠️ Erreur génération réponse pour tweet {row.tweet_id}: {e}")
                reply_text = ""

            rows_out.append({
                "tweet_id": row.tweet_id,
                "tweet": row.tweet,
                "sentiment": row.sentiment,
                "sentiment_score": row.sentiment_score,
                "theme": row.theme,
                "theme_score": row.theme_score,
                "urgence": row.urgence,
                "urgence_score": row.urgence_score,
                "confiance": row.confiance,
                "reponse_free": reply_text,
            })

    out_df = pd.DataFrame(rows_out)
    print(f"\n💾 Sauvegarde dans : {output_csv}")
    out_df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"✅ Fichier généré avec {len(out_df)} lignes.")


# ============================================================
#                        MAIN
# ============================================================

if __name__ == "__main__":
    INPUT_CSV = "LLM-classified-data/tweets_classified.csv"
    OUTPUT_CSV = "LLM-classified-data/tweets_with_replies.csv"

    print("🚀 Génération des réponses Free...")
    generate_replies_for_file(INPUT_CSV, OUTPUT_CSV, API_KEY)
    print("🎉 Terminé ! Réponses générées dans :", OUTPUT_CSV)
