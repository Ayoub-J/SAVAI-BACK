import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from datetime import datetime
import os
import requests

# ================================
# CONFIG GLOBALE
# ================================
st.set_page_config(
    page_title="Dashboard SAV Free - Tweets",
    page_icon="",
    layout="wide"
)

st.title("Dashboard SAV Free – Analyse des Tweets")


# ================================
# CONFIG BACKEND & SESSION
# ================================
BACKEND_URL = "http://127.0.0.1:8000/process"

if "df_final" not in st.session_state:
    st.session_state["df_final"] = None
    st.session_state["df_problematic"] = None
    st.session_state["summary"] = None

# ================================
# UPLOAD DU CSV BRUT + APPEL BACKEND
# ================================
st.sidebar.header("Données")

uploaded_file = st.sidebar.file_uploader(
    "Dépose ici le fichier CSV brut (free tweet export.csv)",
    type=["csv"]
)

if uploaded_file is not None and st.sidebar.button("Lancer l'analyse"):
    try:
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")
        }
        resp = requests.post(BACKEND_URL, files=files, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        df_final = pd.DataFrame(data.get("cleaned", []))
        df_problematic = pd.DataFrame(data.get("problematic", [])) if data.get("problematic") else None

        st.session_state["df_final"] = df_final
        st.session_state["df_problematic"] = df_problematic
        st.session_state["summary"] = data.get("summary", {})

        st.success("Analyse terminée. Vous pouvez naviguer dans le dashboard avec le menu ci-dessous.")
    except Exception as e:
        st.error(f"Erreur lors de l'appel au backend : {e}")


# ================================
# FONCTIONS D'AIDE TEMPORELLES
# ================================
def prepare_time_columns(df):
    df = df.copy()
    df["year"] = df["created_at"].dt.year
    df["month"] = df["created_at"].dt.month
    df["hour"] = df["created_at"].dt.hour
    df["day_of_week"] = df["created_at"].dt.dayofweek
    return df


# ================================
# CHARGEMENT EFFECTIF DEPUIS LA SESSION
# ================================
df_final = st.session_state.get("df_final")
df_problematic = st.session_state.get("df_problematic")
summary = st.session_state.get("summary") or {}

if df_final is None or df_final.empty:
    st.warning(
        "Aucune donnée analysée pour le moment.\n"
        "Merci d'uploader un CSV dans le menu de gauche puis de cliquer sur 'Lancer l'analyse'."
    )
    st.stop()

VOLUME_INITIAL = summary.get(
    "volume_initial",
    len(df_final) + (len(df_problematic) if df_problematic is not None else 0),
)
VOLUME_NETTOYE = summary.get("volume_final", len(df_final))
TWEETS_PROBLEM = summary.get(
    "volume_problematic",
    len(df_problematic) if df_problematic is not None else 0,
)
TAUX_REDUCTION = (1 - VOLUME_NETTOYE / VOLUME_INITIAL) * 100 if VOLUME_INITIAL else 0

# Préparation colonnes temporelles
df_time = None
if "created_at" in df_final.columns:
    df_final["created_at"] = pd.to_datetime(df_final["created_at"], errors="coerce", utc=True)
    if df_final["created_at"].notna().any():
        df_time = prepare_time_columns(df_final)


# ================================
# NAVIGATION LATERALE
# ================================
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Choisissez une vue :",
    [
        "Vue d'ensemble",
        "Analyse temporelle",
        "Catégories et problèmes",
        "Exploration des tweets",
        "Tweets problématiques",
        "Impact et ROI"
    ]
)

st.sidebar.write("---")
st.sidebar.write("Session :", datetime.now().strftime("%d/%m/%Y %H:%M"))


# ================================
# PAGE 1 : VUE D'ENSEMBLE
# ================================
if page == "Vue d'ensemble":
    st.subheader("Vue d'ensemble du dataset SAV Free")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Volume initial de tweets", f"{VOLUME_INITIAL:,}".replace(",", " "))
    col2.metric("Volume après nettoyage", f"{VOLUME_NETTOYE:,}".replace(",", " "))
    col3.metric("Tweets supprimés (non pertinents)", f"{TWEETS_PROBLEM:,}".replace(",", " "))
    col4.metric("Taux de réduction", f"{TAUX_REDUCTION:.1f}%")

    st.markdown("---")

    st.markdown("Répartition des catégories (tweets conservés)")
    if "categorie" in df_final.columns:
        cat_counts = df_final["categorie"].value_counts()
        rep_df = pd.DataFrame({
            "Catégorie": cat_counts.index,
            "Nombre": cat_counts.values,
            "Pourcentage": (cat_counts.values / len(df_final) * 100).round(1)
        })

        colA, colB = st.columns(2)
        with colA:
            st.dataframe(rep_df)

        with colB:
            fig, ax = plt.subplots()
            ax.pie(cat_counts.values, labels=cat_counts.index, autopct="%1.1f%%", startangle=90)
            ax.set_title("Répartition des catégories")
            st.pyplot(fig)

    st.markdown("Aperçu des tweets nettoyés")
    colonnes_affichage = ["created_at", "screen_name", "categorie", "full_text"]
    colonnes_existantes = [c for c in colonnes_affichage if c in df_final.columns]

    st.dataframe(df_final[colonnes_existantes].head(20).reset_index(drop=True))


# ================================
# PAGE 2 : ANALYSE TEMPORELLE
# ================================
elif page == "Analyse temporelle":
    st.subheader("Analyse temporelle des tweets")

    if df_time is None:
        st.warning("Impossible d'afficher l'analyse temporelle : colonne 'created_at' manquante ou invalide.")
    else:
        colY, colM = st.columns(2)

        # Année
        with colY:
            yearly_stats = df_time["year"].value_counts().sort_index()
            fig, ax = plt.subplots()
            ax.bar(yearly_stats.index, yearly_stats.values)
            ax.set_xlabel("Année")
            ax.set_ylabel("Nombre de tweets")
            ax.set_title("Tweets par année")
            st.pyplot(fig)

        # Mois
        with colM:
            monthly_stats = df_time["month"].value_counts().sort_index()
            fig, ax = plt.subplots()
            ax.plot(monthly_stats.index, monthly_stats.values, marker="o")
            ax.set_xlabel("Mois")
            ax.set_ylabel("Nombre de tweets")
            ax.set_title("Tweets par mois")
            ax.set_xticks(range(1, 13))
            st.pyplot(fig)

        colH, colD = st.columns(2)

        # Heure
        with colH:
            hourly_stats = df_time["hour"].value_counts().sort_index()
            fig, ax = plt.subplots()
            ax.bar(hourly_stats.index, hourly_stats.values)
            ax.set_xlabel("Heure")
            ax.set_title("Tweets par heure")
            st.pyplot(fig)

        # Jour
        with colD:
            daily_stats = df_time["day_of_week"].value_counts().sort_index()
            fig, ax = plt.subplots()
            labels = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
            ax.bar(range(7), daily_stats.values)
            ax.set_xticks(range(7))
            ax.set_xticklabels(labels)
            ax.set_title("Tweets par jour de la semaine")
            st.pyplot(fig)


# ================================
# PAGE 3 : CATEGORIES ET PROBLEMES
# ================================
elif page == "Catégories et problèmes":
    st.subheader("Analyse des catégories et problèmes")

    if "categorie" in df_final.columns:
        st.markdown("Distribution des catégories")
        cat_counts = df_final["categorie"].value_counts()

        colA, colB = st.columns(2)

        with colA:
            dist_df = pd.DataFrame({
                "Catégorie": cat_counts.index,
                "Nombre": cat_counts.values,
                "Pourcentage": (cat_counts.values / len(df_final) * 100).round(1)
            })
            st.dataframe(dist_df)

        with colB:
            fig, ax = plt.subplots()
            ax.barh(cat_counts.index, cat_counts.values)
            ax.set_title("Nombre de tweets par catégorie")
            st.pyplot(fig)

    st.markdown("---")

    # WordCloud
    st.markdown("Nuage de mots (tweets clients hors Freebox)")

    if "screen_name" in df_final.columns and "full_text" in df_final.columns:
        mask_non_freebox = df_final["screen_name"].str.lower() != "freebox"
        user_tweets = df_final[mask_non_freebox]["full_text"]

        if user_tweets.dropna().empty:
            st.info("Pas assez de texte pour générer un wordcloud.")
        else:
            stopwords = {
                "free", "freebox", "https", "co", "rt", "de", "la", "le", "et", "un", "une",
                "les", "des", "pour", "pas", "sur", "est", "que", "qui", "dans", "avec", "par",
                "en", "vous", "bonjour", "c'est", "mais", "plus", "ma", "au", "cette", "ce",
                "chez", "mon", "me", "toujours", "je", "merci", "suis", "car", "rien", "svp",
                "meme", "jour", "moi", "j'ai", "sans", "sont", "ça", "tout", "tous", "toute",
                "toutes", "on", "alors", "j", "ai"
            }

            all_text = " ".join(user_tweets.dropna().astype(str))
            wc = WordCloud(
                width=1600,
                height=800,
                background_color="white",
                stopwords=stopwords,
                max_words=100
            ).generate(all_text)

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)

# ================================
# PAGE 4 : EXPLORATION DES TWEETS
# ================================
elif page == "Exploration des tweets":
    st.subheader("Exploration détaillée des tweets")

    if "full_text" not in df_final.columns:
        st.error("La colonne 'full_text' est absente.")
    else:
        col1, col2, col3 = st.columns(3)

        # Catégorie
        if "categorie" in df_final.columns:
            categories = ["(Toutes)"] + sorted(df_final["categorie"].dropna().unique().tolist())
            selected_cat = col1.selectbox("Catégorie", categories)
        else:
            selected_cat = "(Toutes)"

        # Utilisateur
        if "screen_name" in df_final.columns:
            users = ["(Tous)"] + sorted(df_final["screen_name"].dropna().unique().tolist())
            selected_user = col2.selectbox("Compte utilisateur", users)
        else:
            selected_user = "(Tous)"

        keyword = col3.text_input("Recherche mot-clé")

        df_filtered = df_final.copy()

        if selected_cat != "(Toutes)":
            df_filtered = df_filtered[df_filtered["categorie"] == selected_cat]

        if selected_user != "(Tous)":
            df_filtered = df_filtered[df_filtered["screen_name"] == selected_user]

        if keyword:
            df_filtered = df_filtered[df_filtered["full_text"].str.contains(keyword, case=False, na=False)]

        st.markdown("---")
        st.write(f"{len(df_filtered):,} tweets trouvés.".replace(",", " "))

        colonnes_affichage = ["created_at", "screen_name", "categorie", "full_text"]
        colonnes_existantes = [c for c in colonnes_affichage if c in df_filtered.columns]

        st.dataframe(df_filtered[colonnes_existantes].reset_index(drop=True))


# ================================
# PAGE 5 : TWEETS PROBLEMATIQUES
# ================================
elif page == "Tweets problématiques":
    st.subheader("Tweets problématiques")

    st.markdown("""
Voici les tweets considérés comme non pertinents pour l'analyse :
- réponses automatiques de Freebox  
- retweets  
- spam / promotions  
- tweets trop courts  
""")

    if df_problematic is None or df_problematic.empty:
        st.info("Aucun tweet problématique détecté.")
    else:
        st.write(f"Nombre total : {len(df_problematic):,}".replace(",", " "))

        if "issues" in df_problematic.columns:
            issue_counts = df_problematic["issues"].value_counts()

            colA, colB = st.columns(2)
            with colA:
                issue_df = pd.DataFrame({
                    "Problème": issue_counts.index,
                    "Occurrences": issue_counts.values,
                    "Pourcentage": (issue_counts.values / len(df_problematic) * 100).round(1)
                })
                st.dataframe(issue_df)

            with colB:
                fig, ax = plt.subplots()
                top_issues = issue_counts.head(10)
                ax.barh(top_issues.index, top_issues.values)
                ax.set_title("Top 10 des problèmes détectés")
                st.pyplot(fig)

        selected_issue = st.selectbox(
            "Filtrer par type de problème",
            ["(Tous)"] + df_problematic["issues"].dropna().unique().tolist()
        )

        df_prob_filtered = df_problematic.copy()

        if selected_issue != "(Tous)":
            df_prob_filtered = df_prob_filtered[df_prob_filtered["issues"] == selected_issue]

        colonnes_affichage_prob = ["screen_name", "categorie", "issues", "extrait"]
        colonnes_existantes_prob = [
            c for c in colonnes_affichage_prob if c in df_prob_filtered.columns
        ]

        st.dataframe(df_prob_filtered[colonnes_existantes_prob].reset_index(drop=True))


# ================================
# PAGE 6 : IMPACT ET ROI
# ================================
elif page == "Impact et ROI":
    st.subheader("Impact et Retour sur Investissement")

    temps_par_tweet = 0.5  # minutes
    temps_gagne_min = (VOLUME_INITIAL - VOLUME_NETTOYE) * temps_par_tweet
    temps_gagne_h = temps_gagne_min / 60

    col1, col2, col3 = st.columns(3)
    col1.metric("Volume initial", f"{VOLUME_INITIAL:,}".replace(",", " "))
    col2.metric("Volume nettoyé", f"{VOLUME_NETTOYE:,}".replace(",", " "))
    col3.metric("Taux de réduction", f"{TAUX_REDUCTION:.1f}%")

    st.markdown("---")

    colA, colB = st.columns(2)

    with colA:
        volumes = [VOLUME_INITIAL, VOLUME_NETTOYE]
        labels = ["Initial", "Après nettoyage"]

        fig, ax = plt.subplots()
        ax.bar(labels, volumes)
        ax.set_title("Réduction du volume total")
        for i, v in enumerate(volumes):
            ax.text(i, v + 50, f"{v:,}".replace(",", " "), ha="center")
        st.pyplot(fig)

    with colB:
        st.write(f"Tweets supprimés : {(VOLUME_INITIAL - VOLUME_NETTOYE):,}".replace(",", " "))
        st.write(f"Temps gagné : {temps_gagne_min:.0f} minutes ({temps_gagne_h:.1f} heures)")

        st.info(
            "L'élimination du bruit permet de concentrer l'effort humain sur les tweets réellement importants."
        )
