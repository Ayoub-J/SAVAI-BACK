import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Manager - Free SAV", layout="wide")

if "data" not in st.session_state:
    st.error("⚠️ Aucun fichier importé.")
    st.stop()

df = st.session_state["data"].copy()

st.markdown("<h1>📈 Tableau de Bord Manager</h1>", unsafe_allow_html=True)

# ---------------- KPIs ----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Tweets importés", df.shape[0])

with col2:
    st.metric("Tweets urgents", df[df["urgence"] == "élevée"].shape[0])

with col3:
    st.metric("Faible confiance", df[df["confiance"] < 0.9].shape[0])

st.write("---")

# ---------------- Répartition des thèmes ----------------
st.subheader("🎯 Répartition des thèmes")

fig_theme = px.bar(
    df["theme"].value_counts(),
    title="Thèmes les plus fréquents",
    labels={"value": "Occurences", "index": "Thème"},
)

st.plotly_chart(fig_theme, use_container_width=True)

st.write("---")

# ---------------- Urgences ----------------
st.subheader("🚨 Urgences")

fig_urg = px.pie(
    df,
    names="urgence",
    title="Répartition des niveaux d'urgence",
)

st.plotly_chart(fig_urg, use_container_width=True)

st.write("---")

# ---------------- Performance agents (pas dans CSV) ----------------
st.subheader("📊 Performance Agents (non disponible dans ce fichier)")

st.info("Aucune donnée 'agent' dans le CSV. Tableau non disponible.")

