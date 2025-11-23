import streamlit as st
import pandas as pd

st.set_page_config(page_title="Agent SAV", layout="wide")

if "data" not in st.session_state:
    st.error("⚠️ Aucun fichier importé. Retournez à la page d’accueil.")
    st.stop()

df = st.session_state["data"].copy()

st.markdown("<h1>👨‍💻 Espace Agent SAV</h1>", unsafe_allow_html=True)

# ---------------- KPIs ----------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Confiance < 90%", df[df["confiance"] < 0.90].shape[0])

with col2:
    st.metric("Tweets restants", df.shape[0])

with col3:
    st.metric("Urgence élevée", df[df["urgence"] == "élevée"].shape[0])

with col4:
    st.metric("Tweets traités", df[df["reponse_free"].notna()].shape[0])


st.write("---")

# ---------------- Tweets à faible confiance ----------------
st.subheader("⚠️ Tweets nécessitant une vérification (< 90% confiance)")

low_conf = df[df["confiance"] < 0.90]

st.dataframe(
    low_conf[["tweet", "sentiment", "theme", "urgence", "confiance", "reponse_free"]],
    use_container_width=True
)

st.write("---")

# ---------------- Tous les tweets ----------------
st.subheader("📋 Tous les tweets")

st.dataframe(
    df[["tweet", "sentiment", "theme", "urgence", "confiance", "reponse_free"]],
    use_container_width=True
)
