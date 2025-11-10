# ui/settings.py
"""
Vue paramètres et accès au backoffice
"""
import streamlit as st
from ui.components import render_back_button, render_info_box


def render_settings():
    """Affiche la vue paramètres"""

    render_back_button("← Retour au Dashboard", "dashboard")

    st.markdown("---")

    st.markdown("## ⚙️ Paramètres")

    # Paramètres agent
    st.markdown("### 👤 Paramètres Agent")

    with st.container():
        current_agent = st.session_state.get("agent_name", "agent_1")

        new_agent_name = st.text_input(
            "Identifiant Agent",
            value=current_agent,
            help="Votre identifiant utilisateur pour le suivi des actions"
        )

        if new_agent_name != current_agent:
            if st.button("💾 Sauvegarder l'identifiant", type="primary"):
                st.session_state["agent_name"] = new_agent_name
                st.success(f"✅ Identifiant changé pour: {new_agent_name}")
                st.rerun()

    st.markdown("---")

    # Accès Backoffice
    st.markdown("### 🔧 Configuration Système")

    render_info_box(
        "Accès Backoffice",
        "Le backoffice permet de charger des données, configurer les modèles LLM, "
        "paramétrer les prompts et gérer la documentation RAG.",
        box_type="info"
    )

    if st.button("🚀 Ouvrir le Backoffice", use_container_width=True, type="primary"):
        st.session_state.current_view = "backoffice"
        st.rerun()

    st.markdown("---")

    # Informations système
    st.markdown("### 📊 Informations Système")

    with st.expander("Voir les informations"):
        config = st.session_state.get("config")
        raw_df = st.session_state.get("raw_df")
        processed_df = st.session_state.get("processed_df")
        rag_engine = st.session_state.get("rag_engine")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Données:**")
            if raw_df is not None:
                st.write(f"✅ CSV brut chargé ({len(raw_df)} lignes)")
            else:
                st.write("❌ Aucun CSV chargé")

            if processed_df is not None:
                inbound_count = len(processed_df[processed_df["direction"] == "inbound"])
                st.write(f"✅ Analyse effectuée ({inbound_count} tweets inbound)")
            else:
                st.write("❌ Aucune analyse effectuée")

        with col2:
            st.markdown("**Configuration:**")
            if config:
                st.write(f"🤖 Modèle classification: {config.classify_model}")
                st.write(f"🤖 Modèle réponse: {config.reply_model}")
                st.write(f"📊 Seuil confiance: {config.confidence_threshold}")
            else:
                st.write("❌ Configuration non initialisée")

            if rag_engine:
                st.write("✅ RAG activé")
            else:
                st.write("⚪ RAG non configuré")

    st.markdown("---")

    # Statistiques session
    st.markdown("### 📈 Statistiques de Session")

    if processed_df is not None:
        df_inbound = processed_df[processed_df["direction"] == "inbound"].copy()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Tweets", len(df_inbound))

        with col2:
            pending = len(df_inbound[df_inbound["status"] == "pending"])
            st.metric("En attente", pending)

        with col3:
            assigned = len(df_inbound[df_inbound["status"] == "assigned"])
            st.metric("Assignés", assigned)

        with col4:
            answered = len(df_inbound[df_inbound["status"] == "answered"])
            st.metric("Traités", answered)

    else:
        render_info_box(
            "Aucune donnée",
            "Aucune analyse n'a été effectuée. Utilisez le Backoffice pour charger et analyser des tweets.",
            box_type="warning"
        )

    st.markdown("---")

    # Footer
    st.markdown(
        """
        <div style="text-align: center; color: #999; padding: 20px;">
            <p>Twitter SAV POC v1.1</p>
            <p style="font-size: 12px;">Powered by Mistral AI • Streamlit</p>
        </div>
        """,
        unsafe_allow_html=True
    )
