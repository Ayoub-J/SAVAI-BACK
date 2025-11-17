from mistralai import Mistral
import pandas as pd
import os, json, time, random, re
from dotenv import load_dotenv

# ============ CONFIG ============
load_dotenv()
API_KEY = os.getenv("API_KEY")
INPUT_PATH = "/Users/Nadou/Documents/RNCP Projet/SAVAI-BACK/venv/LLM-classified-data/LLM - DATA.csv"
TEXT_COL = "clean_text"    # colonne contenant le texte du tweet
ID_COL = "id"        # colonne contenant l'ID du tweet
OUTPUT_PATH = "LLM - mistral-small-latest.csv"
MODEL = "mistral-small-latest"
SUCCESS_PAUSE_SEC = 0.7
MAX_RETRIES = 4
BACKOFF_BASE_SEC = 3.0
BACKOFF_JITTER_SEC = (0.0, 0.8)

# ============ PROMPT ============
PROMPT_TEMPLATE = """
Tu es un analyste télécom francophone expert en analyse de tweets.

Classifie ces tweet et renvoie STRICTEMENT un objet JSON unique avec les colonnes :
- tweet_id (ID du tweet)
- tweet (texte complet)
- sentiment (positif | neutre | negatif)
- thème (Panne Internet | Facturation | Débit Internet | Espace Client | Fibre | Résiliation | Remerciement | Autre)
- urgence (0 | 1 | 2 | 3)
- confiance (score 0.0-1.0 basé sur probabilité : confiance = 0.4*P(sentiment)+0.4*P(thème)+0.2*P(urgence))

Si hors-sujet, thème="Autre", urgence=0, sentiment="neutre".

Tweet: "{tweet}"
"""

BRACES = re.compile(r"\{.*\}", re.DOTALL)

def parse_json_or_default(text, tweet_id, tweet):
    """
    Extrait proprement l'objet JSON renvoyé par le LLM.
    - Si JSON trouvé -> parse correctement.
    - Sinon -> fallback minimal.
    """
    # Cherche le premier objet JSON dans la réponse
    m = BRACES.search(text)
    if m:
        try:
            data = json.loads(m.group(0))
            # Assure que tweet_id et tweet sont corrects
            data["tweet_id"] = tweet_id
            data["tweet"] = tweet
            # Compléter si certaines clés manquent
            data.setdefault("sentiment", "neutre")
            data.setdefault("thème", "Autre")
            data.setdefault("urgence", 0)
            data.setdefault("confiance", 0.0)
            return data
        except Exception:
            pass

    # Si parsing échoue complètement
    return {"tweet_id": tweet_id, "tweet": tweet, "sentiment":"neutre", "thème":"Autre", "urgence":0, "confiance":0.0}

def is_capacity_error(e):
    s = str(e).lower()
    return "429" in s or "capacity exceeded" in s

def call_mistral_with_retry(client, prompt):
    for attempt in range(MAX_RETRIES):
        try:
            res = client.chat.complete(
                model=MODEL,
                messages=[{"role":"user","content":prompt}],
                temperature=0.1,
                max_tokens=250,
                stream=False,
            )
            return res.choices[0].message.content
        except Exception as e:
            if is_capacity_error(e) and attempt < MAX_RETRIES - 1:
                backoff = BACKOFF_BASE_SEC * (2 ** attempt) + random.uniform(*BACKOFF_JITTER_SEC)
                print(f"⏳ Capacité atteinte, retry dans {backoff:.1f}s...")
                time.sleep(backoff)
                continue
            raise

# ============ MAIN ============
def main():
    if not API_KEY:
        raise RuntimeError("⚠️ Renseignez votre clé API Mistral")

    df = pd.read_csv(INPUT_PATH)
    for col in [TEXT_COL, ID_COL]:
        if col not in df.columns:
            raise ValueError(f"Colonne '{col}' manquante dans {INPUT_PATH}")

    results = []
    with Mistral(api_key=API_KEY) as client:
        for i, row in df.iterrows():
            tweet_id = row[ID_COL]
            tweet = str(row[TEXT_COL])
            prompt = PROMPT_TEMPLATE.format(tweet=tweet)
            try:
                response = call_mistral_with_retry(client, prompt)
                data = parse_json_or_default(response, tweet_id, tweet)
            except Exception as e:
                print(f"⚠️ Erreur tweet {tweet_id}: {e}")
                data = {"tweet_id": tweet_id, "tweet": tweet, "sentiment": "neutre", "thème": "Autre", "urgence":0, "confiance":0.0}
            results.append(data)
            print(f"✅ {i+1}/{len(df)} traité")
            time.sleep(SUCCESS_PAUSE_SEC)

    pd.DataFrame(results).to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"\n✅ Sauvegardé -> {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
