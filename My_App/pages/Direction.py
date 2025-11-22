import streamlit as st
import pandas as pd

st.title("🏛 Direction – Synthèse stratégique")

if "df" not in st.session_state:
    st.error("Veuillez d'abord importer un fichier CSV dans la page d’accueil.")
    st.stop()

df = st.session_state["df"]

st.header("📌 Synthèse générale")

st.write(f"**Volume total analysé :** {len(df)}")
st.write(f"**Taux d'urgence global :** {round(df['urgence'].mean()*100, 2)} %")
st.write(f"**Sentiment général :** {df['sentiment'].mode()[0]}")

st.header("📈 Détection de risques et crises émergentes")

crises = df[df["urgence"] >= 2]
st.dataframe(crises[["tweet", "theme", "urgence"]].head(20))
