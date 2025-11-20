# ui/conversation.py
"""
Vue détaillée d'une conversation / tweet sélectionné
Permet de voir les détails, générer une réponse IA, et traiter le ticket
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timezone

from core.config import AppConfig
from core.preprocessing import generate_reply_for_tweet
from ui.components import (
    render_back_button,
    render_status_badge,
    render_urgency_badge,
    render_sentiment_badge,
    render_category_badge,
    render_info_box
)


def render_conversation():
    """Affiche la vue détaillée d'un tweet sélectionné"""

    # Vérifier qu'un tweet est sélectionné
    selected_id = st.session_state.get("selected_tweet_id")

    if not selected_id:
        st.warning("Aucun tweet sélectionné")
        render_back_button("← Retour au Dashboard", "dashboard")
        return

    # Récupérer le DataFrame
    df = st.session_state.get("processed_df")

    if df is None:
        st.error("Aucune donnée analysée. Utilisez d'abord le Backoffice pour charger et analyser les tweets.")
        render_back_button("← Retour au Dashboard", "dashboard")
        return

    # Récupérer le tweet
    tweet_df = df[df["id"] == selected_id]

    if tweet_df.empty:
        st.error(f"Tweet avec ID {selected_id} introuvable")
        render_back_button("← Retour au Dashboard", "dashboard")
        return

    tweet = tweet_df.iloc[0]
    cfg: AppConfig = st.session_state["config"]
    agent_name = st.session_state.get("agent_name", "agent_1")

    # Bouton retour en haut
    render_back_button("← Retour à la liste", "dashboard")

    st.markdown("---")

    # Titre de la section
    st.markdown("## 📨 Détails de la Conversation")

    # Container principal pour le tweet
    with st.container():
        # En-tête du tweet
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"### Tweet ID: `{tweet.get('id')}`")

            # Date
            created_at = tweet.get("created_at")
            if created_at and not pd.isna(created_at):
                try:
                    date_obj = pd.to_datetime(created_at)
                    date_str = date_obj.strftime("%d %B %Y à %H:%M")
                except:
                    date_str = str(created_at)
            else:
                date_str = "Date inconnue"

            st.markdown(f"📅 **Date:** {date_str}")

            # Auteur
            screen_name = tweet.get("screen_name", "Inconnu")
            st.markdown(f"👤 **Auteur:** @{screen_name}")

        with col2:
            status = tweet.get("status", "pending")
            st.markdown("**Statut:**")
            st.markdown(render_status_badge(status), unsafe_allow_html=True)

    st.markdown("---")

    # Contenu du tweet
    st.markdown("### 💬 Contenu du Tweet")

    with st.container():
        full_text = tweet.get("full_text", "")

        st.markdown(
            f"""
            <div style="
                background-color: #f7f9fa;
                border-left: 4px solid #1DA1F2;
                padding: 20px;
                border-radius: 8px;
                margin: 10px 0;
            ">
                <p style="font-size: 16px; line-height: 1.6; margin: 0; color: #14171a;">
                    {full_text}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Texte nettoyé
        clean_text = tweet.get("clean_text", "")
        if clean_text and clean_text != full_text:
            with st.expander("🧹 Voir le texte nettoyé (pour analyse)"):
                st.code(clean_text, language=None)

    st.markdown("---")

    # Classification automatique
    st.markdown("### 🤖 Classification Automatique (IA)")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Urgence**")
        urgency = tweet.get("urgency")
        if urgency and not pd.isna(urgency):
            st.markdown(render_urgency_badge(str(urgency)), unsafe_allow_html=True)
            urgency_conf = tweet.get("urgency_confidence", 0.0)
            if urgency_conf:
                st.caption(f"Confiance: {int(float(urgency_conf) * 100)}%")
        else:
            st.caption("Non classifié")

    with col2:
        st.markdown("**Sentiment**")
        sentiment = tweet.get("sentiment")
        if sentiment and not pd.isna(sentiment):
            st.markdown(render_sentiment_badge(str(sentiment)), unsafe_allow_html=True)
            sentiment_conf = tweet.get("sentiment_confidence", 0.0)
            if sentiment_conf:
                st.caption(f"Confiance: {int(float(sentiment_conf) * 100)}%")
        else:
            st.caption("Non classifié")

    with col3:
        st.markdown("**Catégorie**")
        category = tweet.get("category")
        if category and not pd.isna(category):
            st.markdown(render_category_badge(str(category)), unsafe_allow_html=True)
            category_conf = tweet.get("category_confidence", 0.0)
            if category_conf:
                st.caption(f"Confiance: {int(float(category_conf) * 100)}%")
        else:
            st.caption("Non classifié")

    # Thème détecté
    theme = tweet.get("theme")
    if theme and not pd.isna(theme):
        st.markdown(f"**📝 Thème détecté:** {theme}")

    # Confiance globale
    overall_conf = tweet.get("overall_confidence", 0.0)
    if overall_conf and not pd.isna(overall_conf):
        conf_float = float(overall_conf)
        conf_percent = int(conf_float * 100)

        if conf_float < cfg.confidence_threshold:
            render_info_box(
                "Confiance Faible",
                f"La confiance globale de classification est de {conf_percent}% (seuil: {int(cfg.confidence_threshold * 100)}%). "
                "Une réponse IA suggérée pourrait être utile.",
                box_type="warning"
            )
        else:
            st.success(f"✅ Confiance globale: {conf_percent}%")

    st.markdown("---")

    # Génération de réponse IA
    st.markdown("### 💬 Génération de Réponse")

    suggested = tweet.get("suggested_reply") or ""
    reply_conf = float(tweet.get("reply_confidence") or 0.0)

    # Bouton pour générer une réponse
    if not suggested and st.button("🤖 Générer une proposition de réponse avec Mistral AI", type="primary", use_container_width=True):
        with st.spinner("🔄 Génération de la réponse en cours..."):
            try:
                rep = generate_reply_for_tweet(tweet, cfg)
                suggested = rep["reply_text"]
                reply_conf = rep["reply_confidence"]

                # Mise à jour du DataFrame global
                idx_global = st.session_state["processed_df"].index[
                    st.session_state["processed_df"]["id"] == selected_id
                ][0]
                st.session_state["processed_df"].at[idx_global, "suggested_reply"] = suggested
                st.session_state["processed_df"].at[idx_global, "reply_confidence"] = reply_conf
                st.session_state["processed_df"].at[idx_global, "reply_raw_llm"] = rep["raw_reply_llm_output"]

                st.success("✅ Réponse générée avec succès!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération: {str(e)}")

    # Zone de texte pour éditer/voir la réponse
    st.markdown("**Réponse à envoyer** (éditable)")
    reply_text = st.text_area(
        "Texte de la réponse",
        value=suggested,
        height=150,
        placeholder="Écrivez votre réponse ici ou générez-en une avec l'IA...",
        label_visibility="collapsed"
    )

    if reply_conf > 0:
        st.caption(f"📊 Confiance IA de la réponse générée: {int(reply_conf * 100)}%")

    st.markdown("---")

    # Actions sur le ticket
    st.markdown("### ⚙️ Actions")

    col_action1, col_action2 = st.columns(2)

    with col_action1:
        # Assigner le ticket
        assigned_to = tweet.get("assigned_to")

        if not assigned_to or pd.isna(assigned_to) or assigned_to != agent_name:
            if st.button("👤 M'assigner ce ticket", use_container_width=True):
                idx_global = st.session_state["processed_df"].index[
                    st.session_state["processed_df"]["id"] == selected_id
                ][0]
                st.session_state["processed_df"].at[idx_global, "assigned_to"] = agent_name
                st.session_state["processed_df"].at[idx_global, "status"] = "assigned"
                st.success(f"✅ Ticket assigné à {agent_name}")
                st.rerun()
        else:
            st.info(f"📌 Déjà assigné à: {assigned_to}")

    with col_action2:
        # Marquer comme traité
        if st.button("✅ Marquer comme traité et enregistrer la réponse", type="primary", use_container_width=True):
            if not reply_text.strip():
                st.warning("⚠️ Veuillez saisir une réponse avant de marquer comme traité")
            else:
                now = datetime.now(timezone.utc)
                idx_global = st.session_state["processed_df"].index[
                    st.session_state["processed_df"]["id"] == selected_id
                ][0]

                st.session_state["processed_df"].at[idx_global, "assigned_to"] = agent_name
                st.session_state["processed_df"].at[idx_global, "answered_by"] = agent_name
                st.session_state["processed_df"].at[idx_global, "answered_at"] = now
                st.session_state["processed_df"].at[idx_global, "status"] = "answered"
                st.session_state["processed_df"].at[idx_global, "agent_final_reply"] = reply_text

                st.success("✅ Tweet marqué comme traité!")
                st.balloons()

                # Rediriger vers le dashboard après 2 secondes
                import time
                time.sleep(1)
                st.session_state.current_view = "dashboard"
                st.session_state.selected_tweet_id = None
                st.rerun()

    st.markdown("---")

    # Informations complémentaires (debug/avancé)
    with st.expander("🔍 Informations techniques (pour debug)"):
        st.json({
            "id": str(tweet.get("id")),
            "direction": str(tweet.get("direction", "N/A")),
            "in_reply_to": str(tweet.get("in_reply_to", "N/A")),
            "created_at": str(tweet.get("created_at", "N/A")),
            "status": str(tweet.get("status", "N/A")),
            "assigned_to": str(tweet.get("assigned_to", "N/A")),
            "answered_by": str(tweet.get("answered_by", "N/A")),
            "answered_at": str(tweet.get("answered_at", "N/A")),
        })
