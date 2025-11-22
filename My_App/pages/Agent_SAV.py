import streamlit as st
import pandas as pd

st.title("🧑‍💼 Agent SAV – Traitement des tweets urgents")

if "df" not in st.session_state:
    st.error("Veuillez d'abord importer un fichier CSV dans la page d’accueil.")
    st.stop()

df = st.session_state["df"]

# Filtrer les urgences
urgent_df = df[df["urgence"] >= 1]

st.subheader("🔥 Tweets urgents à traiter")
st.write("Tweets classés comme prioritaires par le modèle :")

for i, row in urgent_df.iterrows():
    with st.container(border=True):
        st.markdown(f"**Tweet :** {row['tweet']}")
        st.markdown(f"**Sentiment :** {row['sentiment']} ({row['sentiment_score']})")
        st.markdown(f"**Thème :** {row['theme']} ({row['theme_score']})")
        st.markdown(f"**Urgence :** {row['urgence']} ({row['urgence_score']})")
        st.markdown(f"**Confiance globale :** {row['confiance']}")
        
        st.markdown("### 💬 Proposition de réponse IA :")
        st.info(row["reponse_free"])

        st.button("Valider", key=f"valider_{i}")
        st.button("Modifier la réponse", key=f"modifier_{i}")
        st.button("Ignorer", key=f"ignorer_{i}")
