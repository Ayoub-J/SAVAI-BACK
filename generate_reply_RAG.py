import os
import csv
import time
import random

from dotenv import load_dotenv
from mistralai import Mistral

from rag_utils import load_rag_index, retrieve_context

# -------------------------------
# ⚙️ Config générale
# -------------------------------
load_dotenv()

API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL", "mistral-tiny")

if API_KEY is None:
    raise ValueError("⚠️ API_KEY n'est pas défini dans .env")

# Limites API
MAX_RETRIES = 4
BACKOFF_BASE_SEC = 2
BACKOFF_JITTER_SEC = (0, 1)
PAUSE_BETWEEN_CALLS = 0.5  # pause entre deux tweets (en secondes)

# -------------------------------
# 🔧 Chargement RAG
# -------------------------------
print("📦 Chargement de l'index RAG...")
RAG_TEXTS, RAG_EMBEDDINGS = load_rag_index("rag_index.pkl")
print(f"🧠 Index chargé : {len(RAG_TEXTS)} passages.\n")


# -------------------------------
# 🔧 Prompt de base
# -------------------------------
def load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


BASE_PROMPT = load_prompt("Prompt-files/prompt-response.txt")


# -------------------------------
# 🧠 Appel Mistral avec retry
# -------------------------------
def call_llm_with_retry(client: Mistral, prompt: str) -> str:
    for attempt in range(MAX_RETRIES):
        try:
            res = client.chat.complete(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200,
                stream=False,
            )
            return res.choices[0].message.content.strip()

        except Exception as e:
            s = str(e).lower()

            # Rate limit → on attend et on retente
            if ("429" in s or "rate limit" in s) and attempt < MAX_RETRIES - 1:
                delay = BACKOFF_BASE_SEC * (2 ** attempt) + random.uniform(
                    *BACKOFF_JITTER_SEC
                )
                print(f"⏳ Rate limit (429). Retry dans {delay:.1f}s...")
                time.sleep(delay)
                continue

            # autre erreur → on remonte
            print("❌ Erreur LLM définitive :", e)
            raise

    raise RuntimeError("❌ Impossible d'obtenir une réponse après plusieurs retries.")


# -------------------------------
# 🧠 Génération d'une réponse
# -------------------------------
def generate_reply(client: Mistral, tweet: str, sentiment: str,
                   theme: str, urgence: str, faq_context: str) -> str:

    prompt = BASE_PROMPT.format(
        tweet=tweet,
        sentiment=sentiment,
        theme=theme,
        urgence=urgence,
        faq=faq_context,
    )

    return call_llm_with_retry(client, prompt)


# -------------------------------
# 🔁 Traitement complet CSV
# -------------------------------
def process_csv(input_file: str, output_file: str):
    print(f"📂 Lecture de : {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("⚠️ CSV vide, rien à traiter.")
        return

    # On s'assure que le dossier de sortie existe
    out_dir = os.path.dirname(output_file)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    output_rows = []

    with Mistral(api_key=API_KEY) as client:
        for i, row in enumerate(rows, start=1):
            tweet = row.get("tweet", "")
            sentiment = row.get("sentiment", "")
            theme = row.get("theme", "")
            urgence = row.get("urgence", "")

            print(f"\n🔍 Traitement tweet {i}/{len(rows)} : {tweet[:60]}...")

            # ---- Recherche RAG : top 3 passages les plus proches ----
            faq_contexts = retrieve_context(
                query=tweet,
                texts=RAG_TEXTS,
                embeddings=RAG_EMBEDDINGS,
                k=3,
            )
            faq_text = "\n\n".join(faq_contexts)

            # ---- Génération réponse ----
            try:
                reply = generate_reply(
                    client=client,
                    tweet=tweet,
                    sentiment=sentiment,
                    theme=theme,
                    urgence=urgence,
                    faq_context=faq_text,
                )
            except Exception:
                reply = ""

            print(f"➡️ Réponse générée : {reply[:120]}")

            row["reponse_free"] = reply
            output_rows.append(row)

            time.sleep(PAUSE_BETWEEN_CALLS)

    # ---- Sauvegarde ----
    print(f"\n💾 Sauvegarde vers : {output_file}")
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_rows[0].keys())
        writer.writeheader()
        writer.writerows(output_rows)

    print("🎉 CSV final généré avec succès !")


# -------------------------------
# ▶️ Main
# -------------------------------
if __name__ == "__main__":
    INPUT = "LLM-classified-data/tweets_classified.csv"
    OUTPUT = "LLM-classified-data/tweets_with_rag.csv"

    print("🚀 Génération des réponses RAG + Mistral embeddings...")
    process_csv(INPUT, OUTPUT)
