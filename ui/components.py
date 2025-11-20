# ui/components.py
"""
Composants UI réutilisables pour l'application Twitter SAV
Style moderne inspiré de Twitter/React
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional, Callable


def render_status_badge(status: str) -> str:
    """Retourne un badge HTML coloré pour le statut du tweet"""
    badges = {
        "pending": '<span style="background-color: #FFC107; color: #000; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">🟡 En attente</span>',
        "assigned": '<span style="background-color: #2196F3; color: #fff; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">🔵 Assigné</span>',
        "answered": '<span style="background-color: #4CAF50; color: #fff; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">🟢 Traité</span>',
    }
    return badges.get(status, f'<span style="background-color: #999; color: #fff; padding: 4px 12px; border-radius: 12px; font-size: 12px;">{status}</span>')


def render_urgency_badge(urgency: str) -> str:
    """Retourne un badge HTML coloré pour l'urgence"""
    badges = {
        "critique": '<span style="background-color: #D32F2F; color: #fff; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">🔴 Critique</span>',
        "haute": '<span style="background-color: #F57C00; color: #fff; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">🟠 Haute</span>',
        "normale": '<span style="background-color: #FBC02D; color: #000; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">🟡 Normale</span>',
        "basse": '<span style="background-color: #9E9E9E; color: #fff; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">⚪ Basse</span>',
    }
    return badges.get(urgency, '<span style="background-color: #999; color: #fff; padding: 4px 12px; border-radius: 12px; font-size: 12px;">-</span>')


def render_sentiment_badge(sentiment: str) -> str:
    """Retourne un badge HTML coloré pour le sentiment"""
    badges = {
        "positive": '<span style="background-color: #4CAF50; color: #fff; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">😊 Positif</span>',
        "neutral": '<span style="background-color: #9E9E9E; color: #fff; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">😐 Neutre</span>',
        "negative": '<span style="background-color: #F44336; color: #fff; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">😞 Négatif</span>',
        "mixed": '<span style="background-color: #FF9800; color: #fff; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">🤔 Mixte</span>',
    }
    return badges.get(sentiment, '<span style="background-color: #999; color: #fff; padding: 4px 12px; border-radius: 12px; font-size: 12px;">-</span>')


def render_category_badge(category: str) -> str:
    """Retourne un badge HTML pour la catégorie"""
    if not category or pd.isna(category):
        return ""

    category_clean = str(category).replace("_", " ").title()
    return f'<span style="background-color: #E3F2FD; color: #1976D2; padding: 4px 10px; border-radius: 10px; font-size: 11px; font-weight: 500;">📁 {category_clean}</span>'


def render_tweet_card(tweet: pd.Series, index: int, on_select_key: str):
    """
    Affiche une carte tweet cliquable style Twitter

    Args:
        tweet: Série pandas contenant les données du tweet
        index: Index pour générer une clé unique
        on_select_key: Clé unique pour le bouton de sélection
    """
    with st.container():
        # Bordure et padding
        st.markdown(
            f"""
            <div style="
                border: 1px solid #e1e8ed;
                border-radius: 16px;
                padding: 16px;
                margin-bottom: 16px;
                background-color: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                transition: box-shadow 0.2s;
            ">
            """,
            unsafe_allow_html=True
        )

        # Header: date + badges status
        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            created_at = tweet.get("created_at", "")
            if created_at and not pd.isna(created_at):
                try:
                    date_obj = pd.to_datetime(created_at)
                    date_str = date_obj.strftime("%d %b %Y %H:%M")
                except:
                    date_str = str(created_at)[:16]
            else:
                date_str = "Date inconnue"

            st.markdown(f'<p style="color: #657786; font-size: 13px; margin: 0;">📅 {date_str}</p>', unsafe_allow_html=True)

        with col_header2:
            status = tweet.get("status", "pending")
            st.markdown(render_status_badge(status), unsafe_allow_html=True)

        # Texte du tweet
        full_text = tweet.get("full_text", "")
        if len(full_text) > 200:
            display_text = full_text[:200] + "..."
        else:
            display_text = full_text

        st.markdown(f'<p style="font-size: 15px; line-height: 1.5; margin: 12px 0; color: #14171a;">{display_text}</p>', unsafe_allow_html=True)

        # Badges: urgence, sentiment, catégorie
        col_badge1, col_badge2, col_badge3 = st.columns(3)
        with col_badge1:
            urgency = tweet.get("urgency")
            if urgency and not pd.isna(urgency):
                st.markdown(render_urgency_badge(str(urgency)), unsafe_allow_html=True)

        with col_badge2:
            sentiment = tweet.get("sentiment")
            if sentiment and not pd.isna(sentiment):
                st.markdown(render_sentiment_badge(str(sentiment)), unsafe_allow_html=True)

        with col_badge3:
            category = tweet.get("category")
            if category and not pd.isna(category):
                st.markdown(render_category_badge(str(category)), unsafe_allow_html=True)

        # Confiance globale et indicateur de réponse IA
        col_info1, col_info2 = st.columns(2)

        with col_info1:
            confidence = tweet.get("overall_confidence", 0.0)
            if confidence and not pd.isna(confidence):
                conf_float = float(confidence)
                conf_percent = int(conf_float * 100)
                conf_color = "#4CAF50" if conf_float >= 0.7 else "#FF9800" if conf_float >= 0.5 else "#F44336"
                st.markdown(
                    f'<p style="font-size: 12px; color: {conf_color}; margin: 8px 0 0 0;">📊 Confiance: {conf_percent}%</p>',
                    unsafe_allow_html=True
                )

        with col_info2:
            # Indicateur si une réponse IA existe déjà
            suggested_reply = tweet.get("suggested_reply")
            if suggested_reply and not pd.isna(suggested_reply) and str(suggested_reply).strip():
                st.markdown(
                    '<p style="font-size: 12px; color: #9C27B0; margin: 8px 0 0 0;">🤖 Réponse IA disponible</p>',
                    unsafe_allow_html=True
                )

        # Boutons d'action
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

        with col_btn1:
            if st.button("👁️ Ouvrir", key=f"open_{on_select_key}", use_container_width=True):
                st.session_state.selected_tweet_id = tweet.get("id")
                st.session_state.current_view = "conversation"
                st.rerun()

        with col_btn2:
            assigned_to = tweet.get("assigned_to")
            agent_name = st.session_state.get("agent_name", "agent_1")

            if not assigned_to or pd.isna(assigned_to):
                if st.button("👤 M'assigner", key=f"assign_{on_select_key}", use_container_width=True):
                    idx_global = st.session_state["processed_df"].index[
                        st.session_state["processed_df"]["id"] == tweet.get("id")
                    ][0]
                    st.session_state["processed_df"].at[idx_global, "assigned_to"] = agent_name
                    st.session_state["processed_df"].at[idx_global, "status"] = "assigned"
                    st.rerun()

        with col_btn3:
            # Bouton pour générer une réponse IA
            if st.button("🤖 Générer IA", key=f"gen_ai_{on_select_key}", use_container_width=True):
                # Importer la fonction de génération
                from core.preprocessing import generate_reply_for_tweet

                cfg = st.session_state.get("config")
                if cfg:
                    with st.spinner("🤖 Génération de la réponse IA..."):
                        # Générer la réponse
                        result = generate_reply_for_tweet(tweet, cfg)

                        # Mettre à jour le DataFrame
                        idx_global = st.session_state["processed_df"].index[
                            st.session_state["processed_df"]["id"] == tweet.get("id")
                        ][0]

                        st.session_state["processed_df"].at[idx_global, "suggested_reply"] = result.get("reply_text", "")
                        st.session_state["processed_df"].at[idx_global, "reply_confidence"] = result.get("reply_confidence", 0.0)
                        st.session_state["processed_df"].at[idx_global, "reply_raw_llm"] = result.get("raw_reply_llm_output", "")

                        st.success("✅ Réponse générée ! Ouvrez le tweet pour la voir.")
                        st.rerun()
                else:
                    st.error("Configuration non disponible")

        # Fermeture du div
        st.markdown("</div>", unsafe_allow_html=True)


def render_back_button(label: str = "← Retour", view_to_return: str = "dashboard"):
    """Bouton de retour standard"""
    if st.button(label, key=f"back_to_{view_to_return}"):
        st.session_state.current_view = view_to_return
        st.session_state.selected_tweet_id = None
        st.rerun()


def render_role_selector():
    """Sélecteur de rôle dans le header"""
    roles = {
        "agent": "👤 Agent SAV",
        "manager": "📊 Manager",
        "director": "🎯 Direction"
    }

    current_role = st.session_state.get("current_role", "agent")

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    for idx, (role_key, role_label) in enumerate(roles.items()):
        with [col1, col2, col3][idx]:
            if st.button(
                role_label,
                key=f"role_switch_{role_key}",
                use_container_width=True,
                type="primary" if current_role == role_key else "secondary"
            ):
                st.session_state.current_role = role_key
                st.session_state.current_view = "dashboard"
                st.session_state.selected_tweet_id = None
                st.rerun()


def render_header():
    """Header principal de l'application avec navigation"""
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            <h1 style="color: white; margin: 0; font-size: 28px;">🐦 Twitter SAV - Free</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 14px;">
                Plateforme d'analyse et de gestion du service client Twitter
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Sélecteur de rôle
    st.markdown("### Navigation")
    render_role_selector()

    st.markdown("---")


def render_kpi_card(title, value, subtitle="", color="#4A90E2", icon="📊", trend=""):
    """
    Affiche une KPI card colorée style dashboard moderne (inspiré de l'image)

    Args:
        title: Titre de la métrique
        value: Valeur principale (nombre ou texte)
        subtitle: Texte secondaire optionnel
        color: Couleur de fond (#hex)
        icon: Emoji ou icône
        trend: Texte de tendance (ex: "+12.4% vs mois dernier")
    """
    card_html = f"""
    <div style="
        background: {color};
        border-radius: 12px;
        padding: 20px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div style="font-size: 14px; opacity: 0.9; font-weight: 500;">
                {title}
            </div>
            <div style="font-size: 32px;">
                {icon}
            </div>
        </div>
        <div>
            <div style="font-size: 32px; font-weight: bold; margin: 8px 0;">
                {value}
            </div>
            <div style="font-size: 12px; opacity: 0.85;">
                {subtitle if subtitle else trend}
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_kpi_cards_row(kpis: list):
    """
    Affiche une ligne de KPI cards colorées

    Args:
        kpis: Liste de dicts avec keys: title, value, subtitle, color, icon, trend
    """
    cols = st.columns(len(kpis))

    for idx, kpi in enumerate(kpis):
        with cols[idx]:
            render_kpi_card(
                title=kpi.get("title", ""),
                value=kpi.get("value", ""),
                subtitle=kpi.get("subtitle", ""),
                color=kpi.get("color", "#4A90E2"),
                icon=kpi.get("icon", "📊"),
                trend=kpi.get("trend", "")
            )


def render_metrics_row(metrics: list):
    """
    Affiche une ligne de métriques

    Args:
        metrics: Liste de tuples (label, value, delta=None, delta_color="normal")
    """
    cols = st.columns(len(metrics))

    for idx, metric_data in enumerate(metrics):
        with cols[idx]:
            if len(metric_data) == 2:
                label, value = metric_data
                st.metric(label, value)
            elif len(metric_data) == 3:
                label, value, delta = metric_data
                st.metric(label, value, delta)
            elif len(metric_data) == 4:
                label, value, delta, delta_color = metric_data
                st.metric(label, value, delta, delta_color=delta_color)


def render_info_box(title: str, content: str, box_type: str = "info"):
    """
    Affiche une boîte d'information stylisée

    Args:
        title: Titre de la boîte
        content: Contenu texte
        box_type: "info", "success", "warning", "error"
    """
    colors = {
        "info": {"bg": "#E3F2FD", "border": "#2196F3", "icon": "ℹ️"},
        "success": {"bg": "#E8F5E9", "border": "#4CAF50", "icon": "✅"},
        "warning": {"bg": "#FFF3E0", "border": "#FF9800", "icon": "⚠️"},
        "error": {"bg": "#FFEBEE", "border": "#F44336", "icon": "❌"},
    }

    style = colors.get(box_type, colors["info"])

    st.markdown(
        f"""
        <div style="
            background-color: {style['bg']};
            border-left: 4px solid {style['border']};
            padding: 16px;
            border-radius: 8px;
            margin: 16px 0;
        ">
            <p style="margin: 0; font-weight: 600; color: #333;">
                {style['icon']} {title}
            </p>
            <p style="margin: 8px 0 0 0; color: #555; font-size: 14px;">
                {content}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def format_relative_time(timestamp) -> str:
    """Formate un timestamp en temps relatif (ex: il y a 2h)"""
    if pd.isna(timestamp):
        return "Date inconnue"

    try:
        if isinstance(timestamp, str):
            dt = pd.to_datetime(timestamp)
        else:
            dt = timestamp

        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        delta = now - dt

        seconds = delta.total_seconds()

        if seconds < 60:
            return "à l'instant"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"il y a {minutes}min"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"il y a {hours}h"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"il y a {days}j"
        else:
            return dt.strftime("%d %b %Y")
    except:
        return str(timestamp)[:16]
