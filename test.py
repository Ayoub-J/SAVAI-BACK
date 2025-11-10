# %% [markdown]
# # Analyse des réponses et temps de réponse
# 
# Objectifs :
# - Savoir combien de tweets répondent à un autre tweet
# - Savoir combien de réponses ont leur tweet parent dans le dataset
# - Calculer le temps de réponse entre le tweet parent et la réponse
#
# ⚠️ Hypothèse : 
# - La colonne de l'identifiant du tweet s'appelle `id`
# - La colonne de référence s'appelle `in_reply_to`
# - La date du tweet est dans `created_at`

# %%
import pandas as pd

# Affiche toutes les colonnes sans troncature (optionnel)
pd.set_option("display.max_columns", None)

# %%
# 1. Chargement du fichier CSV
# Mets le notebook dans le même dossier que le CSV ou adapte le chemin.
file_path = "free_tweet_export.csv"

df = pd.read_csv(
    file_path,
    dtype={
        "id": "string",
        "in_reply_to": "string",
        "created_at": "string"
    }
)

print("Nombre total de tweets dans le fichier :", len(df))
df.head()

# %% 
# 2. Nettoyage minimal des colonnes utiles

# On s'assure que les colonnes existent
required_cols = ["id", "in_reply_to", "created_at"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Colonnes manquantes dans le CSV : {missing}")

# On supprime les espaces autour de in_reply_to (au cas où)
df["in_reply_to"] = df["in_reply_to"].str.strip()

# Conversion de created_at en datetime (avec timezone si présente)
df["created_at_dt"] = pd.to_datetime(df["created_at"], utc=True, errors="coerce")

# Petit check
print(df[["id", "in_reply_to", "created_at"]].head())

# %%
# 3. Identifier les tweets qui répondent à un autre tweet (in_reply_to non vide)

mask_replies = df["in_reply_to"].notna() & (df["in_reply_to"] != "")
df_replies = df[mask_replies].copy()

nb_replies_any = len(df_replies)

print("Nombre de tweets qui répondent à quelque chose (in_reply_to non vide) :", nb_replies_any)
df_replies.head()

# %%
# 4. Parmi ces réponses, quelles sont celles dont le parent est dans le dataset ?
#    (c'est nécessaire pour calculer un temps de réponse parent -> réponse)

all_ids = set(df["id"].dropna())

df_replies["has_parent_in_dataset"] = df_replies["in_reply_to"].isin(all_ids)
df_replies_internal = df_replies[df_replies["has_parent_in_dataset"]].copy()
df_replies_external = df_replies[~df_replies["has_parent_in_dataset"]].copy()

print("Nombre de réponses total (in_reply_to non vide) :", nb_replies_any)
print("Nombre de réponses dont le parent est dans le dataset :", len(df_replies_internal))
print("Nombre de réponses dont le parent n'est PAS dans le dataset :", len(df_replies_external))

# %%
# 5. Jointure avec le tweet parent pour calculer le temps de réponse

# On prépare un petit DataFrame avec l'heure du tweet parent
parents = df[["id", "created_at_dt"]].rename(
    columns={"id": "parent_id", "created_at_dt": "parent_created_at_dt"}
)

# Jointure : chaque réponse récupère la date du tweet parent
df_replies_internal = df_replies_internal.merge(
    parents,
    left_on="in_reply_to",
    right_on="parent_id",
    how="left",
    validate="m:1"   # plusieurs réponses possibles pour un même parent
)

# Calcul du delta de temps entre parent et réponse
df_replies_internal["response_time"] = (
    df_replies_internal["created_at_dt"] - df_replies_internal["parent_created_at_dt"]
)

df_replies_internal["response_time_seconds"] = (
    df_replies_internal["response_time"].dt.total_seconds()
)

# On peut enlever les cas bizarres (delta négatif ou NaN)
df_valid = df_replies_internal[
    df_replies_internal["response_time_seconds"].notna()
    & (df_replies_internal["response_time_seconds"] >= 0)
].copy()

print("Nombre de réponses avec un temps de réponse exploitable :", len(df_valid))
df_valid[["id", "in_reply_to", "created_at", "parent_created_at_dt", "response_time"]].head()

# %%
# 6. Quelques stats globales sur les temps de réponse

if not df_valid.empty:
    desc = df_valid["response_time"].describe()
    print("Statistiques sur les temps de réponse :")
    print(desc)

    # Exemple : temps de réponse moyen et médian en heures
    mean_seconds = df_valid["response_time_seconds"].mean()
    median_seconds = df_valid["response_time_seconds"].median()

    mean_hours = mean_seconds / 3600
    median_hours = median_seconds / 3600

    print(f"\nTemps de réponse moyen : {mean_hours:.2f} heures")
    print(f"Temps de réponse médian : {median_hours:.2f} heures")
else:
    print("Aucun temps de réponse exploitable (aucun parent trouvé ou dates manquantes).")

# %%
# 7. (Optionnel) Sauvegarder le détail dans un CSV pour exploitation ultérieure

output_file = "tweets_reponses_avec_temps.csv"
df_valid.to_csv(output_file, index=False, encoding="utf-8")
print(f"Fichier détaillé écrit dans : {output_file}")


# %% 
# 6.1. Statistiques des temps de réponse pour les comptes de Free uniquement

# Liste des comptes "officiels" Free dans le dataset
# 👉 adapte cette liste si besoin (par ex. ajoute d'autres comptes SAV)
free_accounts = ["free", "Freebox", "freebox", "Free_1337", "GroupeIliad", "FreeMobile", "free_mobile"]

# On filtre df_valid (réponses avec parent + temps de réponse >= 0)
df_free = df_valid[df_valid["screen_name"].isin(free_accounts)].copy()

print("Nombre de réponses des comptes Free avec un temps de réponse exploitable :", len(df_free))

if not df_free.empty:
    # Stats globales
    print("\nStatistiques globales (tous comptes Free confondus) :")
    print(df_free["response_time"].describe())

    mean_seconds_free = df_free["response_time_seconds"].mean()
    median_seconds_free = df_free["response_time_seconds"].median()

    mean_hours_free = mean_seconds_free / 3600
    median_hours_free = median_seconds_free / 3600

    print(f"\nTemps de réponse moyen (comptes Free)  : {mean_hours_free:.2f} heures")
    print(f"Temps de réponse médian (comptes Free) : {median_hours_free:.2f} heures")

    # Détail par compte (si plusieurs comptes Free dans le dataset)
    print("\nDétail par compte Free :")
    stats_par_compte = (
        df_free
        .groupby("screen_name")["response_time"]
        .agg(["count", "mean", "median"])
    )
    print(stats_par_compte)

else:
    print("Aucune réponse des comptes Free trouvée dans df_valid.")
    print("➡ Vérifie le nom de la colonne (screen_name) ou la liste free_accounts.")

# %%

# %% 
# 6.2. Messages de réponse "automatiques" des comptes Free
#
# Un message est considéré comme "automatique" si :
# - il s'agit d'une réponse (in_reply_to non vide)
# - envoyée par un compte Free (liste free_accounts)
# - et dont le corps du message (sans le @pseudo en début de tweet)
#   est réutilisé au moins THRESHOLD_AUTO fois.

import re

# 1) On définit les comptes Free que l'on considère comme SAV / officiels
free_accounts = ["free", "Freebox", "freebox", "Free_1337", "GroupeIliad", "FreeMobile", "free_mobile"]

# 2) On filtre les réponses envoyées par ces comptes
df["in_reply_to"] = df["in_reply_to"].astype("string")

mask_reply = df["in_reply_to"].notna() & (df["in_reply_to"] != "")
mask_free  = df["screen_name"].isin(free_accounts)

df_free_replies_all = df[mask_reply & mask_free].copy()

print("Nombre total de réponses envoyées par les comptes Free :", len(df_free_replies_all))

# 3) On enlève la mention @client au début pour isoler le texte modèle
def strip_mention(text: str) -> str:
    if not isinstance(text, str):
        return ""
    # Supprime le @pseudo en début de message + les espaces
    return re.sub(r"^@\S+\s*", "", text).strip()

df_free_replies_all["template_body"] = df_free_replies_all["full_text"].astype("string").apply(strip_mention)

# 4) On compte la fréquence de chaque "corps" de message
body_counts = df_free_replies_all["template_body"].value_counts()

# Seuil à partir duquel un message est considéré comme automatique
THRESHOLD_AUTO = 1  # tu peux jouer avec cette valeur (5, 10, 20...)

df_free_replies_all["is_auto_reply"] = df_free_replies_all["template_body"].map(
    lambda t: body_counts.get(t, 0) >= THRESHOLD_AUTO
)

# 5) Statistiques globales
total_free_replies = len(df_free_replies_all)
nb_auto = int(df_free_replies_all["is_auto_reply"].sum())
share_auto = (nb_auto / total_free_replies * 100) if total_free_replies else 0

print(f"\n▶ Nombre total de réponses Free            : {total_free_replies}")
print(f"▶ Nombre de réponses 'automatiques'       : {nb_auto}")
print(f"▶ Part des réponses automatiques          : {share_auto:.1f} % ")
    #   f"(corps de message réutilisé ≥ {THRESHOLD_AUTO} fois)")

# 6) Pour voir les principaux modèles de messages automatiques
print("\nTop 10 modèles de messages les plus fréquents :")
print(body_counts.head(10))

# %%
