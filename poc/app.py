# app.py
import streamlit as st

from core.config import AppConfig
from ui.components import render_header
from ui.backoffice import render_backoffice
from ui.agent_sav import render_agent_sav
from ui.manager import render_manager
from ui.direction import render_direction


def init_session_state():
    """Initialise tous les états de session nécessaires"""
    # Configuration et données
    if "config" not in st.session_state:
        st.session_state["config"] = AppConfig()

    if "raw_df" not in st.session_state:
        st.session_state["raw_df"] = None

    if "processed_df" not in st.session_state:
        st.session_state["processed_df"] = None

    if "rag_engine" not in st.session_state:
        st.session_state["rag_engine"] = None

    # Navigation
    if "current_view" not in st.session_state:
        st.session_state["current_view"] = "dashboard"

    if "current_role" not in st.session_state:
        st.session_state["current_role"] = "agent"

    if "previous_view" not in st.session_state:
        st.session_state["previous_view"] = None

    # Sélection et filtres
    if "selected_tweet_id" not in st.session_state:
        st.session_state["selected_tweet_id"] = None

    if "agent_name" not in st.session_state:
        st.session_state["agent_name"] = "agent_1"

    if "filter_urgency" not in st.session_state:
        st.session_state["filter_urgency"] = None

    if "filter_sentiment" not in st.session_state:
        st.session_state["filter_sentiment"] = None

    if "filter_status" not in st.session_state:
        st.session_state["filter_status"] = None


def render_view():
    """Router principal - Affiche la vue appropriée selon l'état de navigation"""
    current_view = st.session_state.get("current_view", "dashboard")
    current_role = st.session_state.get("current_role", "agent")

    # Vue Dashboard selon le rôle
    if current_view == "dashboard":
        if current_role == "agent":
            render_agent_sav()
        elif current_role == "manager":
            render_manager()
        elif current_role == "director":
            render_direction()

    # Vue Conversation (détail tweet) - uniquement pour Agent
    elif current_view == "conversation":
        # Import dynamique pour éviter les imports circulaires
        from ui.conversation import render_conversation
        render_conversation()

    # Vue Settings
    elif current_view == "settings":
        from ui.settings import render_settings
        render_settings()

    # Vue Backoffice (configuration système)
    elif current_view == "backoffice":
        render_backoffice()

    # Vue par défaut si état invalide
    else:
        st.error(f"Vue inconnue: {current_view}")
        if st.button("← Retour au Dashboard"):
            st.session_state.current_view = "dashboard"
            st.rerun()


def main():
    st.set_page_config(
        page_title="Twitter SAV – Free + Mistral AI",
        page_icon="🐦",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Initialiser les états de session
    init_session_state()

    # Header avec navigation par rôles
    render_header()

    # Afficher la vue appropriée
    render_view()

    # Footer (optionnel)
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #999; font-size: 12px;">'
        'POC Twitter SAV © 2024 | Powered by Mistral AI'
        '</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
