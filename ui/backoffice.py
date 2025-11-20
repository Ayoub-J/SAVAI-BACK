# ui/backoffice.py
"""
Backoffice - Configuration système et lancement d'analyse
"""
import streamlit as st
import pandas as pd

from core.config import AppConfig
from core.preprocessing import preprocess_and_analyse
from core.rag import SimpleRAG
from ui.components import render_back_button


def render_backoffice():
    """Interface backoffice pour configuration et analyse"""

    # Bouton retour
    render_back_button("← Retour au Dashboard", "dashboard")

    st.markdown("---")

    st.markdown("## 🔧 Backoffice – Configuration & Analyse")

    cfg: AppConfig = st.session_state["config"]

    # 1) Chargement CSV
    st.subheader("1. Chargement du CSV")

    uploaded = st.file_uploader(
        "Télécharger un fichier CSV similaire à free_tweet_export.csv",
        type=["csv"],
    )

    if st.button("Charger le CSV par défaut (data/free_tweet_export.csv)"):
        try:
            df_default = pd.read_csv("data/free_tweet_export.csv")
            st.session_state["raw_df"] = df_default
            st.success("CSV par défaut chargé depuis data/free_tweet_export.csv")
            st.dataframe(df_default.head())
        except Exception as e:
            st.error(f"Impossible de charger le CSV par défaut : {e}")

    if uploaded is not None:
        df = pd.read_csv(uploaded)
        st.session_state["raw_df"] = df
        st.success("CSV uploadé chargé.")
        st.dataframe(df.head())

    # 2) Paramètres
    st.markdown("---")
    st.subheader("2. Paramètres LLM et métier")

    with st.form("config_form"):
        col1, col2 = st.columns(2)
        with col1:
            confidence_threshold = st.slider(
                "Seuil de confiance global minimal (overall_confidence)",
                min_value=0.0,
                max_value=1.0,
                value=float(cfg.confidence_threshold),
                step=0.05,
            )
            classify_model = st.text_input(
                "Modèle Mistral pour la classification",
                value=cfg.classify_model,
            )
            reply_model = st.text_input(
                "Modèle Mistral pour la génération de réponse",
                value=cfg.reply_model,
            )
        with col2:
            categories_text = st.text_input(
                "Liste des catégories possibles (séparées par des virgules)",
                value=", ".join(cfg.categories),
            )
            rag_text = st.text_area(
                "Documentation technique (RAG simple) – texte brut",
                value=cfg.rag_text,
                height=150,
            )

        classify_prompt = st.text_area(
            "Prompt de classification LLM",
            value=cfg.classify_prompt,
            height=220,
        )
        reply_prompt = st.text_area(
            "Prompt de génération de réponse LLM",
            value=cfg.reply_prompt,
            height=220,
        )

        submitted = st.form_submit_button("✅ Enregistrer la configuration")
        if submitted:
            cfg.confidence_threshold = confidence_threshold
            cfg.classify_model = classify_model
            cfg.reply_model = reply_model
            cfg.categories = [c.strip() for c in categories_text.split(",") if c.strip()]
            cfg.classify_prompt = classify_prompt
            cfg.reply_prompt = reply_prompt
            cfg.rag_text = rag_text
            st.session_state["config"] = cfg
            st.success("Configuration mise à jour.")

    # 3) RAG : construire un index simple
    st.markdown("---")
    st.subheader("3. Index RAG simple (optionnel)")

    if st.button("Construire l'index RAG à partir de la documentation"):
        rag_engine = SimpleRAG()
        rag_engine.build_from_text(st.session_state["config"].rag_text)
        st.session_state["rag_engine"] = rag_engine
        st.success("Index RAG construit en mémoire.")

    # 4) Lancement de l'analyse
    st.markdown("---")
    st.subheader("4. Lancer l'analyse & le nettoyage")

    if st.session_state.get("raw_df") is None:
        st.info("Veuillez d'abord charger un fichier CSV (upload ou fichier par défaut).")
        return

    max_tweets = st.number_input(
        "Nombre maximum de tweets inbound à analyser (pour le POC)",
        min_value=10,
        max_value=5000,
        value=200,
        step=10,
    )

    if st.button("🚀 Lancer l'analyse et le nettoyage"):
        with st.spinner("Traitement en cours..."):
            df_processed = preprocess_and_analyse(
                st.session_state["raw_df"],
                st.session_state["config"],
                max_inbound_tweets=max_tweets,
            )
            st.session_state["processed_df"] = df_processed
        st.success("Analyse terminée. Les résultats sont disponibles dans les autres onglets.")
        st.dataframe(st.session_state["processed_df"].head())
