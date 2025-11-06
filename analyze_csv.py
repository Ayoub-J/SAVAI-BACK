# analyze_csv.py
import os, time
import pandas as pd
from dotenv import load_dotenv
from telecom_analyzer import analyze_tweets

# === CONFIG PAR DÉFAUT (modifie ici pour éviter de taper des arguments) ===
INPUT_PATH = "tweets_cleaned_enriched.csv"
TEXT_COL = "clean_text"
OUTPUT_PATH = "tweets_analyzed.csv"
N_ROWS = 20  # None = tout

def main():
    load_dotenv()
    df = pd.read_csv(INPUT_PATH)
    if TEXT_COL not in df.columns:
        raise ValueError(f"Colonne '{TEXT_COL}' absente de {INPUT_PATH}.")
    if N_ROWS:
        df = df.head(N_ROWS).copy()

    tweets = df[TEXT_COL].astype(str).tolist()
    print(f"🚀 Analyse de {len(tweets)} tweets…")

    t0 = time.time()
    results = analyze_tweets(tweets)
    t1 = time.time()

    elapsed = t1 - t0
    avg = elapsed / max(len(tweets), 1)

    pd.DataFrame(results, columns=["tweet","sentiment","thème","urgence"]).to_csv(
        OUTPUT_PATH, index=False, encoding="utf-8-sig"
    )
    print(f"\n✅ Résultats -> {OUTPUT_PATH}")
    print(f"⏱️ Temps total : {elapsed:.2f}s")
    print(f"⚡ Temps moyen : {avg:.2f}s / tweet")
    print(f"🧠 Modèle : {os.getenv('MISTRAL_MODEL','mistral-small-latest')} | Workers: {os.getenv('MAX_WORKERS','4')}")

if __name__ == "__main__":
    main()
