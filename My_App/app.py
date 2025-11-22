import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Analyse Tweets SAV Free",
    page_icon="📊",
    layout="wide"
)

st.title("📥 Importer le fichier de tweets analysés")
st.write("Veuillez importer le fichier CSV contenant les tweets classifiés (sentiment, thème, urgence, réponses IA).")

uploaded_file = st.file_uploader("Choisir un fichier CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state["df"] = df  # accessible dans toutes les pages 👌

    st.success("Fichier chargé avec succès ! 🎉")

    st.subheader("Aperçu du fichier")
    st.dataframe(df.head())

    st.info("👉 Vous pouvez maintenant naviguer dans les pages *Agent SAV*, *Manager* et *Direction* via le menu à gauche.")
else:
    st.warning("Veuillez importer un fichier pour continuer.")
