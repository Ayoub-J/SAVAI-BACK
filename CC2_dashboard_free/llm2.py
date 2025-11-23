from mistralai import Mistral
import pandas as pd
from dotenv import load_dotenv
import json, os, re, time, random
from typing import List, Dict, Any, Optional

# ============ CONFIG ============
load_dotenv()
api_key = os.getenv("API_KEY")   
INPUT_PATH = "tweets_cleaned_enriched.csv"                 
TEXT_COL = "clean_text"                                    
OUTPUT_PATH = "tweets_analyzed.csv"                        
MODEL = "mistral-small-latest"                            
N_ROWS: Optional[int] = 20                                 
SUCCESS_PAUSE_SEC = 0.8                                    

# Retry / Backoff
MAX_RETRIES = 4
BACKOFF_BASE_SEC = 3.0                                     
BACKOFF_JITTER_SEC = (0.0, 0.8)                           

# ============ PROMPTS ============
SYSTEM = {
    "role": "system",
    "content": (
        "Tu es un analyste télécom francophone. "
        "Réponds STRICTEMENT par UN SEUL objet JSON valide, sans texte autour. "
        'Schéma: {"tweet": str, "sentiment": "positif|neutre|negatif", '
        '"thème": "Panne Internet|Facturation|Débit Internet|Espace Client|Fibre|Résiliation|Remerciement|Autre", '
        '"urgence": 0|1|2|3}. '
        'Si hors-sujet: thème="Autre", urgence=0.'
    )
}

FEW_SHOT_USER_1 = {
    "role": "user",
    "content": (
        "Exemple 1\nTweet: Merci @Freebox pour l’intervention rapide, tout refonctionne.\n"
        'Réponse attendue (JSON unique): {"tweet":"<tweet>","sentiment":"positif","thème":"Remerciement","urgence":0}'
    )
}
FEW_SHOT_ASSISTANT_1 = {"role": "assistant", "content": '{"tweet":"<tweet>","sentiment":"positif","thème":"Remerciement","urgence":0}'}

FEW_SHOT_USER_2 = {
    "role": "user",
    "content": (
        "Exemple 2\nTweet: Plus d’internet depuis hier soir, la box clignote en rouge.\n"
        'Réponse attendue (JSON unique): {"tweet":"<tweet>","sentiment":"negatif","thème":"Panne Internet","urgence":3}'
    )
}
FEW_SHOT_ASSISTANT_2 = {"role": "assistant", "content": '{"tweet":"<tweet>","sentiment":"negatif","thème":"Panne Internet","urgence":3}'}

TASK_PREFIX = (
    "Analyse le tweet suivant et renvoie UNIQUEMENT l'objet JSON au format demandé.\n"
    "Tweet: "
)

def build_messages(tweet: str) -> List[Dict[str, str]]:
    return [
        SYSTEM,
        FEW_SHOT_USER_1, FEW_SHOT_ASSISTANT_1,
        FEW_SHOT_USER_2, FEW_SHOT_ASSISTANT_2,
        {"role": "user", "content": TASK_PREFIX + tweet},
    ]

# ============ UTILITAIRES ============
BRACES = re.compile(r"\{.*\}", re.DOTALL)

def parse_json_or_default(text: str, tweet: str) -> Dict[str, Any]:
    """Extrait l'objet { ... } si le modèle parle autour et parse le JSON.
       Si échec, renvoie un fallback neutre."""
    text = text.strip()
    m = BRACES.search(text)
    if m:
        text = m.group(0)
    try:
        data = json.loads(text)
    except Exception:
        data = {}
    # Compléter / fallback minimal
    data.setdefault("tweet", tweet)
    data.setdefault("sentiment", "neutre")
    data.setdefault("thème", "Autre")
    data.setdefault("urgence", 0)
    return data

def is_capacity_error(e: Exception) -> bool:
    s = str(e).lower()
    return ("429" in s) or ("capacity exceeded" in s) or ("service_tier_capacity_exceeded" in s)

def call_mistral_with_retry(client: Mistral, messages: List[Dict[str, str]]) -> str:
    """Appelle Mistral avec retry exponentiel sur erreurs de capacité/429."""
    for attempt in range(MAX_RETRIES):
        try:
            res = client.chat.complete(
                model=MODEL,
                messages=messages,
                temperature=0.1,
                max_tokens=200,
                stream=False,
            )
            return res.choices[0].message.content
        except Exception as e:
            if is_capacity_error(e) and attempt < MAX_RETRIES - 1:
                backoff = BACKOFF_BASE_SEC * (2 ** attempt) + random.uniform(*BACKOFF_JITTER_SEC)
                print(f"⏳ Capacité atteinte (429). Retry dans {backoff:.1f}s...")
                time.sleep(backoff)
                continue
           
            raise

# ============ MAIN ============
def main():
    if not api_key or api_key == "API_KEY":
        raise RuntimeError("⚠️ Renseignez votre clé API Mistral (variable MISTRAL_API_KEY ou remplacez VOTRE_CLE_ICI).")

    df = pd.read_csv(INPUT_PATH)
    if TEXT_COL not in df.columns:
        raise ValueError(f"Colonne '{TEXT_COL}' manquante dans {INPUT_PATH}.")

    if isinstance(N_ROWS, int) and N_ROWS > 0:
        df = df.head(N_ROWS).copy()

    rows: List[Dict[str, Any]] = []
    with Mistral(api_key=api_key) as mistral_client:
        total = len(df)
        for i, tweet in enumerate(df[TEXT_COL].astype(str), start=1):
            try:
                messages = build_messages(tweet)
                content = call_mistral_with_retry(mistral_client, messages)
                rec = parse_json_or_default(content, tweet)
                rows.append(rec)
                print(f"✅ {i}/{total} traité")
                time.sleep(SUCCESS_PAUSE_SEC)  # throttle doux pour éviter 429
            except Exception as e:
                print(f"⚠️ {i}/{total} erreur: {e}")
                rows.append({"tweet": tweet, "sentiment": "erreur", "thème": "Autre", "urgence": 0})
                # petite pause même en cas d'échec pour éviter d'enchaîner trop vite
                time.sleep(SUCCESS_PAUSE_SEC)

    pd.DataFrame(rows, columns=["tweet", "sentiment", "thème", "urgence"]).to_csv(
        OUTPUT_PATH, index=False, encoding="utf-8-sig"
    )
    print(f"\n✅ Sauvegardé -> {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
