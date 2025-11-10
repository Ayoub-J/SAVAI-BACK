# ui/manager.py
"""
Dashboard Manager - Analytics et pilotage d'équipe
"""
import streamlit as st
import pandas as pd
import numpy as np

from ui.components import render_metrics_row, render_info_box
from ui.charts import (
    plot_pie_chart,
    plot_simple_bar_chart,
    plot_horizontal_bar_chart,
    plot_line_chart,
    plot_performance_chart,
    plot_stacked_bar_sentiment_category
)


def render_manager():
    """Dashboard pour les managers - Analytics et gestion d'équipe"""

    st.markdown("## 📊 Dashboard Manager")

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
    if "created_at_dt" not in df.columns:
        df["created_at_dt"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)

    st.markdown("---")

    # Filtre période
    st.markdown("### 📅 Filtre Période")
    min_date = df["created_at_dt"].min().date()
    max_date = df["created_at_dt"].max().date()

    date_range = st.date_input(
        "Période d'analyse",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        mask_date = (df["created_at_dt"].dt.date >= start_date) & (
            df["created_at_dt"].dt.date <= end_date
        )
        df = df[mask_date]

    st.markdown("---")

    # Métriques principales
    st.markdown("### 📊 Métriques Globales")

    total = len(df)
    treated = (df["status"] == "answered").sum()
    assigned = (df["status"] == "assigned").sum()
    pending = (df["status"] == "pending").sum()

    render_metrics_row([
        ("📝 Total (période)", total),
        ("🟢 Traités", treated),
        ("🔵 Assignés", assigned),
        ("🟡 En attente", pending)
    ])

    st.markdown("---")
    st.markdown("### 📊 Distribution des Catégories & Sentiments")

    if "category" in df.columns:
        cat_counts = df["category"].value_counts().rename_axis("category").reset_index(name="count")
        st.write("Répartition des catégories :")
        fig_cat = plot_pie_chart(cat_counts, "count", "category", "Distribution des Catégories")
        st.plotly_chart(fig_cat, use_container_width=True)

    if "sentiment" in df.columns:
        sent_counts = df["sentiment"].value_counts().rename_axis("sentiment").reset_index(name="count")
        st.write("Répartition des sentiments :")
        fig_sent = plot_simple_bar_chart(sent_counts, "sentiment", "count", "Distribution des Sentiments")
        st.plotly_chart(fig_sent, use_container_width=True)

    if {"category", "sentiment"}.issubset(df.columns):
        st.write("Croisement catégories × sentiments :")
        cross = pd.crosstab(df["category"], df["sentiment"])

        # Graphique en barres empilées 100%
        fig_cross = plot_stacked_bar_sentiment_category(cross, "Analyse de Sentiment par Catégorie")
        st.plotly_chart(fig_cross, use_container_width=True)

        # Tableau détaillé en dessous
        st.dataframe(cross, use_container_width=True)

    st.markdown("---")
    st.subheader("Mots les plus fréquents (tweets inbound)")

    df_inbound = df[df["direction"] == "inbound"].copy()
    if "clean_text" in df_inbound.columns:
        from collections import Counter

        words = " ".join(df_inbound["clean_text"].dropna().astype(str)).split()
        counts = Counter(words)
        common = counts.most_common(30)
        if common:
            words_df = pd.DataFrame(common, columns=["word", "count"])
            fig_words = plot_horizontal_bar_chart(words_df, "count", "word", "Top 30 Mots Fréquents")
            st.plotly_chart(fig_words, use_container_width=True)
        else:
            st.info("Pas assez de texte pour calculer les mots fréquents.")

    st.markdown("---")
    st.subheader("Assignation des tweets non traités aux agents")

    pending_df = df[df["status"] == "pending"].copy()
    if pending_df.empty:
        st.info("Pas de tweets en attente à assigner.")
    else:
        st.dataframe(
            pending_df[["id", "created_at", "full_text", "category", "urgency", "sentiment"]]
            .rename(columns={"id": "tweet_id"})
            .head(100)
        )

        tweet_ids = pending_df["id"].tolist()
        selected_ids = st.multiselect("Sélectionner des tweets à assigner", tweet_ids)
        agent_target = st.text_input("Assigner à l'agent :", value="agent_1")

        if st.button("📌 Assigner les tweets sélectionnés"):
            for tid in selected_ids:
                idx_global = st.session_state["processed_df"].index[st.session_state["processed_df"]["id"] == tid][0]
                st.session_state["processed_df"].at[idx_global, "assigned_to"] = agent_target
                st.session_state["processed_df"].at[idx_global, "status"] = "assigned"
            st.success(f"{len(selected_ids)} tweets assignés à {agent_target}.")
            st.rerun()

    st.markdown("---")
    st.subheader("Temps moyen de réponse (dataset) & rendement des agents")

    if "service_response_time_minutes" in df.columns:
        df_resp = df[df["service_response_time_minutes"].notna()].copy()
        if not df_resp.empty:
            df_resp["date"] = df_resp["created_at_dt"].dt.date
            mean_by_day = df_resp.groupby("date")["service_response_time_minutes"].mean().reset_index()
            st.write("Évolution du temps moyen de réponse (calculé sur le dataset) :")
            fig_time = plot_line_chart(
                mean_by_day,
                "date",
                "service_response_time_minutes",
                "Temps Moyen de Réponse par Jour",
                "Minutes",
                color="#FF9F40"
            )
            st.plotly_chart(fig_time, use_container_width=True)

    answered_df = df[df["status"] == "answered"].copy()
    if "answered_by" in answered_df.columns and not answered_df.empty:
        perf = (
            answered_df.groupby("answered_by")["id"]
            .count()
            .rename("tweets_traite")
            .reset_index()
        )
        st.write("Tweets traités par agent (via l'application) :")
        st.dataframe(perf)
        fig_perf = plot_performance_chart(perf, "answered_by", "tweets_traite", "Performance des Agents")
        st.plotly_chart(fig_perf, use_container_width=True)

    st.markdown("---")

    # Boutons de navigation
    col_nav1, col_nav2 = st.columns(2)

    with col_nav1:
        if st.button("⚙️ Paramètres", use_container_width=True):
            st.session_state.current_view = "settings"
            st.rerun()

    with col_nav2:
        if st.button("🚀 Backoffice", use_container_width=True):
            st.session_state.current_view = "backoffice"
            st.rerun()
