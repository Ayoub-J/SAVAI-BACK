import json
import time
import random
import pandas as pd
import re,os
from mistralai import Mistral



from dotenv import load_dotenv
load_dotenv()


# ========= PARAMÈTRES ==========
MODEL = os.getenv("MODEL", "mistral-small-latest")
MAX_RETRIES = 3
SUCCESS_PAUSE_SEC = 0.5
BACKOFF_BASE_SEC = 1
BACKOFF_JITTER_SEC = (0, 1)
API_KEY = os.getenv("API_KEY")
BRACES = re.compile(r"\{.*\}", re.DOTALL)

# ========= UTILS ==========

def load_prompt(path):
    """Charge un prompt depuis un fichier texte."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def extract_json(text):
    """Extrait un objet JSON depuis la réponse du LLM."""
    m = BRACES.search(text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except:
        return None
    

def call_llm_with_retry(client, prompt):
    """Appel API Mistral robuste avec retry + backoff."""
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

            # ❌ Cas particulier : capacité tier dépassée -> on NE RETENTE PAS
            if "service tier capacity exceeded" in s or "3505" in s:
                print("❌ Capacité du service atteinte pour ce modèle (code 3505).")
                raise

            # ✅ Cas rate-limit / 429 générique -> on peut retenter
            if ("capacity" in s or "429" in s) and attempt < MAX_RETRIES - 1:
                delay = BACKOFF_BASE_SEC * (2 ** attempt) + random.uniform(*BACKOFF_JITTER_SEC)
                print(f"⏳ Retry dans {delay:.1f}s...")
                time.sleep(delay)
                continue

            # Autres erreurs : on remonte
            raise

# ============================================================================
# SOUS-FONCTION : CLASSIFIER UN SEUL TWEET AVEC 3 PROMPTS
# ============================================================================

def classify_single_tweet(client, tweet, sentiment_prompt, theme_prompt, urgence_prompt):
    """
    Analyse un tweet avec 3 prompts différents (sentiment / thème / urgence).
    Chaque prompt DOIT renvoyer un JSON :
        { "label": "...", "score": 0.x }
    """

    # --- Sentiment ---
    sent_prompt_f = sentiment_prompt.replace("{tweet}", tweet)
    sent_raw = call_llm_with_retry(client, sent_prompt_f+" le tweet que tu dois classifier est : "+tweet)
    sent_json = extract_json(sent_raw)
    #print("DEBUG SENTIMENT RAW:", sent_raw, "\nPARSED:", sent_json)

    # --- Thème ---
    theme_prompt_f = theme_prompt.replace("{tweet}", tweet)
    theme_raw = call_llm_with_retry(client, theme_prompt_f+" le tweet que tu dois classifier est : "+tweet)
    theme_json = extract_json(theme_raw)
    #print("DEBUG THEME RAW:", theme_raw, "\nPARSED:", theme_json)

    # --- Urgence ---
    urg_prompt = urgence_prompt.replace("{tweet}", tweet)
    urg_raw = call_llm_with_retry(client, urg_prompt+" le tweet que tu dois classifier est : "+tweet)
    urg_json = extract_json(urg_raw)
    #print("DEBUG URGENCE RAW:", urg_raw, "\nPARSED:", urg_json)


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
# FONCTION PRINCIPALE : CLASSIFIER UN FICHIER CSV COMPLET
# ============================================================================

def classify_tweet_file(csv_path, output_path, api_key):
    """
    Prend un CSV contenant :
        - tweet_id
        - tweet
    Classifie chaque ligne et écrit un CSV avec TOUS les résultats.
    """

    df = pd.read_csv(csv_path)
    if "id" not in df.columns or "tweet" not in df.columns:
        raise ValueError("Le CSV doit contenir les colonnes 'tweet_id' et 'tweet'")

    # --- Chargement des prompts ---
    sentiment_prompt = load_prompt("Prompt-files/prompt-sentiment.txt")
    theme_prompt = load_prompt("Prompt-files/prompt-theme.txt")
    urgence_prompt = load_prompt("Prompt-files/prompt-urgence.txt")

    results = []

    with Mistral(api_key=api_key) as client:
        for i, row in df.iterrows():
            tweet_id = row["id"]
            tweet_text = str(row["tweet"])

            print(f"▶ Analyse tweet {tweet_id} ...")

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

    # Sauvegarde
    pd.DataFrame(results).to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n✅ Résultats enregistrés dans : {output_path}")


if __name__ == "__main__":

    # --- Paramètres de test ---
    INPUT_CSV = "LLM-classified-data/LLM - DATA.csv"
    OUTPUT_CSV = "LLM-classified-data/tweets_classified.csv"

    # Lancement du test
    print("🚀 Lancement de la classification...")
    classify_tweet_file(INPUT_CSV, OUTPUT_CSV, API_KEY)
    print("🎉 Terminé ! Fichier généré :", OUTPUT_CSV)

