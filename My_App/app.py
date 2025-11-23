import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Free SAV - Analyse Tweets",
    page_icon="📊",
    layout="wide"
)

# ---- Gestion des chemins dynamiques ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "pages", "assets")

CSS_PATH = os.path.join(ASSETS_DIR, "style.css")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo_free.png")

# ---- CSS ----
if os.path.exists(CSS_PATH):
    with open(CSS_PATH) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.error(f"❌ CSS introuvable : {CSS_PATH}")

# ---- Logo ----
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=180)
else:
    st.error(f"❌ Logo introuvable : {LOGO_PATH}")

st.title("📥 Importation des Tweets")
st.subheader("Veuillez importer le fichier CSV contenant les tweets analysés.")

uploaded_file = st.file_uploader("Importer le fichier CSV", type=["csv"], key="upload_csv_main")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state["data"] = df

    st.success("Fichier bien importé !")
    st.write("Aperçu :")
    st.dataframe(df.head())

    st.markdown("### 👉 Accéder aux tableaux de bord")
    st.page_link("pages/Agent_SAV.py", label="🔧 Espace Agent SAV")
    st.page_link("pages/Manager.py", label="📈 Espace Manager")
    st.page_link("pages/Direction.py", label="🏛 Espace Direction")

else:
    st.warning("Veuillez importer votre fichier CSV pour continuer.")
