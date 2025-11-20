# ui/agent_sav.py
"""
Dashboard Agent SAV - Vue liste de tweets style feed Twitter
"""
import streamlit as st
import pandas as pd

from ui.components import (
    render_tweet_card,
    render_metrics_row,
    render_info_box
)


def render_agent_sav():
    """Dashboard principal pour les agents SAV"""

    st.markdown("## 👤 Dashboard Agent SAV")

    # Vérifier les données
    df = st.session_state.get("processed_df")
    if df is None:
        render_info_box(
            "Aucune donnée",
            "Aucune analyse n'a été effectuée. Utilisez le Backoffice (accessible via Settings ⚙️) "
            "pour charger et analyser des tweets.",
            box_type="warning"
        )

        # Bouton d'accès rapide au backoffice
        if st.button("🚀 Ouvrir le Backoffice", type="primary"):
            st.session_state.current_view = "backoffice"
            st.rerun()
        return

    df = df.copy()
    agent_name = st.session_state.get("agent_name", "agent_1")

    # Filtre sur les tweets inbound uniquement
    df_inbound = df[df["direction"] == "inbound"].copy()

    if df_inbound.empty:
        st.info("Aucun tweet client (inbound) trouvé dans les données analysées.")
        return

    # S'assurer que created_at_dt existe
    if "created_at_dt" not in df_inbound.columns:
        df_inbound["created_at_dt"] = pd.to_datetime(df_inbound["created_at"], errors="coerce", utc=True)

    st.markdown("---")

    # Métriques principales
    st.markdown("### 📊 Mes Métriques")

    pending = df_inbound[df_inbound["status"] == "pending"]
    assigned_to_me = df_inbound[df_inbound["assigned_to"] == agent_name]
    answered_by_me = df_inbound[df_inbound["answered_by"] == agent_name]

    render_metrics_row([
        ("🟡 En attente", len(pending)),
        ("🔵 Assignés à moi", len(assigned_to_me)),
        ("🟢 Traités par moi", len(answered_by_me))
    ])

    st.markdown("---")

    # Filtres
    st.markdown("### 🔍 Filtres")

    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)

    with col_filter1:
        filter_status = st.selectbox(
            "Statut",
            options=["Tous", "En attente", "Assignés", "Traités"],
            key="filter_status_select"
        )

    with col_filter2:
        urgencies = df_inbound["urgency"].dropna().unique().tolist()
        filter_urgency = st.selectbox(
            "Urgence",
            options=["Toutes"] + sorted(urgencies),
            key="filter_urgency_select"
        )

    with col_filter3:
        sentiments = df_inbound["sentiment"].dropna().unique().tolist()
        filter_sentiment = st.selectbox(
            "Sentiment",
            options=["Tous"] + sorted(sentiments),
            key="filter_sentiment_select"
        )

    with col_filter4:
        categories = df_inbound["category"].dropna().unique().tolist()
        filter_category = st.selectbox(
            "Catégorie",
            options=["Toutes"] + sorted(categories),
            key="filter_category_select"
        )

    # Filtre par date
    st.markdown("**Période**")
    if df_inbound["created_at_dt"].notna().any():
        min_date = df_inbound["created_at_dt"].min().date()
        max_date = df_inbound["created_at_dt"].max().date()

        date_range = st.date_input(
            "Sélectionner une période",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            label_visibility="collapsed"
        )

        if len(date_range) == 2:
            start_date, end_date = date_range
            mask_date = (df_inbound["created_at_dt"].dt.date >= start_date) & (
                df_inbound["created_at_dt"].dt.date <= end_date
            )
            df_inbound = df_inbound[mask_date]

    # Appliquer les filtres
    df_filtered = df_inbound.copy()

    if filter_status != "Tous":
        status_map = {
            "En attente": "pending",
            "Assignés": "assigned",
            "Traités": "answered"
        }
        df_filtered = df_filtered[df_filtered["status"] == status_map[filter_status]]

    if filter_urgency != "Toutes":
        df_filtered = df_filtered[df_filtered["urgency"] == filter_urgency]

    if filter_sentiment != "Tous":
        df_filtered = df_filtered[df_filtered["sentiment"] == filter_sentiment]

    if filter_category != "Toutes":
        df_filtered = df_filtered[df_filtered["category"] == filter_category]

    st.markdown("---")

    # Liste des tweets
    st.markdown(f"### 📋 File d'Attente ({len(df_filtered)} tweets)")

    # Tri par date (plus récents en premier)
    df_filtered = df_filtered.sort_values("created_at_dt", ascending=False)

    if df_filtered.empty:
        st.info("Aucun tweet ne correspond aux filtres sélectionnés.")
        return

    # Options d'affichage
    col_display1, col_display2 = st.columns([3, 1])
    with col_display1:
        show_limit = st.slider(
            "Nombre de tweets à afficher",
            min_value=5,
            max_value=min(100, len(df_filtered)),
            value=min(20, len(df_filtered)),
            step=5
        )
    with col_display2:
        if st.button("🔄 Rafraîchir", use_container_width=True):
            st.rerun()

    st.markdown("---")

    # Afficher les tweets sous forme de cards
    tweets_to_show = df_filtered.head(show_limit)

    for idx, (_, tweet) in enumerate(tweets_to_show.iterrows()):
        render_tweet_card(
            tweet=tweet,
            index=idx,
            on_select_key=f"tweet_{tweet.get('id')}_{idx}"
        )

    # Pagination info
    if len(df_filtered) > show_limit:
        st.info(f"📄 Affichage de {show_limit} tweets sur {len(df_filtered)} au total. "
                f"Augmentez le curseur pour en voir plus.")

    st.markdown("---")

    # Boutons d'accès rapides
    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if st.button("⚙️ Paramètres", use_container_width=True):
            st.session_state.current_view = "settings"
            st.rerun()

    with col_btn2:
        if st.button("🚀 Backoffice", use_container_width=True):
            st.session_state.current_view = "backoffice"
            st.rerun()
