import pandas as pd
import re
import os
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


# ============================================================
# 1. Chargement du dataset
# ============================================================

FILE_PATH = "LLM-classified-data/free tweet export.csv"
OUTPUT_DIR = "LLM-classified-data"

df = pd.read_csv(FILE_PATH)


# ============================================================
# 2. Sélection des colonnes utiles
# ============================================================

COLUMNS_TO_KEEP = ['id', 'created_at', 'full_text', 'screen_name', 'name', 'user_id', 'in_reply_to']
df = df[COLUMNS_TO_KEEP].copy()


# ============================================================
# 3. Catégorisation des tweets pour filtrage
# ============================================================

def categorize_tweet(text):
    if pd.isna(text):
        return "Vide"

    text = str(text).lower()

    patterns = {
        "RT/Partage": r"^rt @",
        "Message automatique Freebox": r"messagerie privée x n'est plus disponible|retrouvez-moi|messenger|fozuyqkg|via https://t\.co/3rzd3",
        "Plainte service": r"coupure|panne|problème|pas de connexion|bug|instable|service client|hs",
        "Demande d'aide": r"besoin d'aide|aidez-moi|help|svp|sos",
        "Question technique": r"comment|pourquoi|wifi|fibre|débit|installation",
        "Spam/Promotion": r"💩|@fingapp|@outagedetect|nouveau|offert",
        "Réclamation RDV": r"technicien|rdv|rendez-vous|créneau"
    }

    for category, pattern in patterns.items():
        if re.search(pattern, text):
            return category

    return "Autre"


df["categorie"] = df["full_text"].apply(categorize_tweet)


# ============================================================
# 4. Détection des tweets problématiques (à exclure)
# ============================================================

def is_problematic(row):
    issues = []
    text = str(row["full_text"]).lower()

    # messages auto
    if row["categorie"] == "Message automatique Freebox":
        issues.append("auto_reply")

    # retweets
    if row["categorie"] == "RT/Partage":
        issues.append("retweet")

    # spam
    if row["categorie"] == "Spam/Promotion":
        issues.append("spam")

    # trop court
    if len(text) < 20:
        issues.append("text_too_short")

    # sans contexte
    if row["in_reply_to"] == "null" and len(text) < 50 and "?" not in text and row["screen_name"].lower() != "freebox":
        issues.append("no_context")

    return len(issues) > 0


df_final = df[~df.apply(is_problematic, axis=1)].copy()


# ============================================================
# 5. Nettoyage léger pour LLM (colonne finale = "tweet")
# ============================================================

def clean_text_for_llm(text):
    """
    Nettoyage léger :
    - URLs → <URL>
    - mentions → <USER>
    - normalisation des espaces
    - garde emojis, hashtags, ponctuation
    """
    if pd.isna(text):
        return text

    text = str(text)

    text = re.sub(r"http\S+|www\.\S+", "<URL>", text)
    text = re.sub(r"@\w+", "<USER>", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


df_final["tweet"] = df_final["full_text"].apply(clean_text_for_llm)


# ============================================================
# 6. Export des fichiers
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Dataset complet nettoyé (inclut "tweet")
df_final.to_csv(f"{OUTPUT_DIR}/tweets_free_cleaned.csv", index=False)

# Fichier minimal pour LLM (id + tweet)
df_final[["id", "tweet"]].to_csv(
    f"{OUTPUT_DIR}/tweets_free_cleaned_tweet_only.csv",
    index=False
)

# Statistiques rapides
with open(f"{OUTPUT_DIR}/statistiques_analyse.txt", "w", encoding="utf-8") as f:
    f.write("STATISTIQUES DU NETTOYAGE DE TWEETS\n")
    f.write("=" * 60 + "\n")
    f.write(f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
    f.write(f"Tweets initiaux : {len(df)}\n")
    f.write(f"Tweets conservés : {len(df_final)}\n")
    f.write(f"Tweets supprimés : {len(df)-len(df_final)}\n\n")


print("✅ Nettoyage terminé.")
print("➡ tweets_free_cleaned.csv généré (dataset complet).")
print("➡ tweets_free_cleaned_tweet_only.csv généré (id + tweet).")
print("➡ statistiques_analyse.txt généré.")