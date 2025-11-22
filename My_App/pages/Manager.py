import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Manager – Vue analytique globale")

if "df" not in st.session_state:
    st.error("Veuillez d'abord importer un fichier CSV dans la page d’accueil.")
    st.stop()

df = st.session_state["df"]

col1, col2, col3 = st.columns(3)
col1.metric("Tweets analysés", len(df))
col2.metric("Tweets urgents", (df["urgence"] >= 1).sum())
col3.metric("Sentiment positif", (df["sentiment"] == "positif").sum())

st.subheader("Répartition des thèmes")
fig = px.bar(df["theme"].value_counts(), title="Top thèmes")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Répartition des sentiments")
fig2 = px.pie(df, names="sentiment", title="Sentiments")
st.plotly_chart(fig2, use_container_width=True)
