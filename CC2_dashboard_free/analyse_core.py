import pandas as pd
import re


# ============================
# 1. Fonction de catégorisation (copiée de ton script)
# ============================
def categorize_tweet(text):
    """
    Catégorise un tweet selon son contenu.
    """
    if pd.isna(text):
        return "Vide"
    
    text = str(text).lower()
    
    patterns = {
        "RT/Partage": r'^rt @',
        "Message automatique Freebox": r"messagerie privée x n'est plus disponible|retrouvez-moi|messenger|https://t\.co/fozuyqkg|via https://t\.co/3rzd3",
        "Plainte service": r"coupure|panne|problème|pas de connexion|ne fonctionne pas|bug|instable|service client|pire opérateur|hs",
        "Demande d'aide": r"besoin d'aide|j'ai besoin|aidez-moi|help|svp|s'il vous plaît|sos",
        "Question technique": r"comment|pourquoi|qu'est-ce|fibre|débit|wifi|connexion|installation",
        "Spam/Promotion": r"💩|via @fingapp|@outagedetect|disponible sur le canal|nouveau|offert",
        "Réclamation RDV": r"technicien|rdv|rendez-vous|pas venu|attendre|créneau",
        "Info/Annonce": r"retrouvez|nouvelle|découvrez",
    }
    
    for category, pattern in patterns.items():
        if re.search(pattern, text):
            return category
    
    return "Autre"


# ============================
# 2. Détection des tweets problématiques (copié de ton script)
# ============================
def is_unnecessary_or_erroneous(row):
    """
    Identifie si un tweet est non nécessaire ou erroné.
    Retourne (is_problematic: bool, issues: [str]).
    """
    issues = []
    
    if pd.isna(row["full_text"]):
        issues.append("Texte vide")
        return True, issues
    
    text = str(row["full_text"]).lower()
    
    if row["categorie"] == "Message automatique Freebox":
        issues.append("Réponse automatique répétitive")
    
    if row["categorie"] == "RT/Partage":
        issues.append("Retweet (pas une demande directe)")
    
    if row["categorie"] == "Spam/Promotion":
        issues.append("Spam ou promotion non pertinente")
    
    if len(str(row["full_text"])) < 20:
        issues.append("Tweet trop court (<20 caractères)")
    
    if "la messagerie privée x n'est plus disponible" in text and row.get("screen_name", None) == "Freebox":
        issues.append("Message standard répétitif de Freebox")
    
    if (
        row.get("in_reply_to", None) == "null"
        and len(text) < 50
        and "?" not in text
        and row.get("screen_name", None) != "Freebox"
    ):
        issues.append("Message court sans contexte ni question")
    
    return len(issues) > 0, issues


# ============================
# 3. Fonction principale d'analyse
# ============================
def run_analysis(df_raw: pd.DataFrame):
    """
    Prend un DataFrame brut (free tweet export.csv) et renvoie :
    - df_final : tweets nettoyés et catégorisés
    - df_problematic : tweets non pertinents / problématiques
    """
    df = df_raw.copy()

    # Colonnes que tu utilisais déjà dans ton script
    colonnes_a_garder = ["id", "created_at", "full_text", "screen_name", "name", "user_id", "in_reply_to"]
    colonnes_existantes = [col for col in colonnes_a_garder if col in df.columns]

    df_clean = df[colonnes_existantes].copy()

    # Catégorisation
    df_clean["categorie"] = df_clean["full_text"].apply(categorize_tweet)

    # Détection des tweets problématiques
    problematic_tweets = []
    for idx, row in df_clean.iterrows():
        is_problematic, issues = is_unnecessary_or_erroneous(row)
        if is_problematic:
            problematic_tweets.append(
                {
                    "index": idx,
                    "id": row.get("id"),
                    "screen_name": row.get("screen_name"),
                    "categorie": row.get("categorie"),
                    "issues": ", ".join(issues),
                    "extrait": (
                        str(row["full_text"])[:100] + "..."
                        if len(str(row["full_text"])) > 100
                        else str(row["full_text"])
                    ),
                }
            )

    df_problematic = pd.DataFrame(problematic_tweets)

    # Dataset final nettoyé
    if not df_problematic.empty:
        df_final = df_clean[~df_clean.index.isin(df_problematic["index"])].copy()
    else:
        df_final = df_clean.copy()

    # Enrichissement temporel comme dans ton script
    if "created_at" in df_final.columns:
        df_final["created_at"] = pd.to_datetime(df_final["created_at"], utc=True, errors="coerce")
        df_final["year"] = df_final["created_at"].dt.year
        df_final["month"] = df_final["created_at"].dt.month
        df_final["hour"] = df_final["created_at"].dt.hour
        df_final["day_of_week"] = df_final["created_at"].dt.dayofweek

    return df_final, df_problematic
