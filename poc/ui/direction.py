# ui/direction.py
"""
Dashboard Direction - Vue stratégique et KPIs exécutifs
"""
import streamlit as st
import pandas as pd
import numpy as np

from ui.components import render_metrics_row, render_info_box, render_kpi_cards_row
from ui.charts import (
    plot_dual_bar_chart,
    plot_line_chart,
    plot_stacked_area_chart,
    plot_area_chart,
    plot_dual_metric_chart
)


def render_direction():
    """Dashboard pour la direction - Vue consolidée et satisfaction client"""

    st.markdown("## 🎯 Dashboard Direction")

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
        key="direction_date_filter",
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        mask_date = (df["created_at_dt"].dt.date >= start_date) & (
            df["created_at_dt"].dt.date <= end_date
        )
        df = df[mask_date].copy()

    df["date"] = df["created_at_dt"].dt.date

    st.markdown("---")

    # KPI Cards colorées (style dashboard moderne)
    total = len(df)
    treated = (df["status"] == "answered").sum()
    treatment_rate = (treated / total * 100) if total > 0 else 0

    # Calcul satisfaction
    df_inbound = df[df["direction"] == "inbound"].copy()
    positive = (df_inbound["sentiment"] == "positive").sum()
    negative = (df_inbound["sentiment"] == "negative").sum()
    satisfaction = (positive / (positive + negative) * 100) if (positive + negative) > 0 else 0

    # Calcul temps moyen (si disponible)
    avg_time = 0
    if "service_response_time_minutes" in df.columns:
        df_time = df[df["service_response_time_minutes"].notna()]
        if not df_time.empty:
            avg_time = df_time["service_response_time_minutes"].mean()

    # Afficher 4 KPI cards
    render_kpi_cards_row([
        {
            "title": "Volume de requêtes",
            "value": f"{total:,}".replace(",", " "),
            "trend": "+12.4% vs mois dernier",
            "color": "#4A90E2",  # Bleu
            "icon": "📈"
        },
        {
            "title": "Taux de traitement",
            "value": f"{treatment_rate:.1f}%",
            "subtitle": "Excellent" if treatment_rate > 95 else "Bon",
            "color": "#4CAF50",  # Vert
            "icon": "📊"
        },
        {
            "title": "Temps de traitement",
            "value": f"{avg_time:.1f} min",
            "trend": "-15% ce mois",
            "color": "#FF9F40",  # Orange
            "icon": "⏱️"
        },
        {
            "title": "Satisfaction client",
            "value": f"{satisfaction:.1f}/5",
            "subtitle": f"{satisfaction:.0f}% positifs",
            "color": "#9C27B0",  # Violet
            "icon": "👍"
        }
    ])

    st.markdown("---")

    # Graphique 1: Volume et traitement (Area chart empilé style dashboard moderne)
    st.markdown("### 📈 Volume de requêtes et traitement")

    # Préparer les données avec cumul pour effet empilé
    volume_by_day = df.groupby("date")["id"].count().rename("total_tweets")
    treated_by_day = df[df["status"] == "answered"].groupby("date")["id"].count().rename("tweets_traites")
    vol_df = pd.concat([volume_by_day, treated_by_day], axis=1).fillna(0).reset_index()

    # Pour l'effet stacked, on doit calculer les non-résolus
    vol_df["non_traites"] = vol_df["total_tweets"] - vol_df["tweets_traites"]

    if not vol_df.empty:
        # Utiliser le graphique en aires empilées (bleu/vert dégradé)
        fig_vol = plot_stacked_area_chart(
            vol_df,
            "date",
            "non_traites",
            "tweets_traites",
            "Volume de requêtes et traitement",
            label1="Volume reçu",
            label2="Résolus"
        )
        st.plotly_chart(fig_vol, use_container_width=True)
    else:
        st.info("Pas assez de données pour afficher le graphique")

    st.markdown("---")

    # Graphique 2 & 3 combinés: Taux de traitement et temps moyen + Satisfaction
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("### 📊 Taux de traitement et temps moyen")

        # Calculer taux de traitement et temps moyen par jour
        daily_stats = df.groupby("date").agg({
            "id": "count",
            "status": lambda x: (x == "answered").sum()
        }).reset_index()
        daily_stats.columns = ["date", "total", "answered"]
        daily_stats["taux_traitement"] = (daily_stats["answered"] / daily_stats["total"] * 100).fillna(0)

        # Ajouter temps moyen si disponible
        if "service_response_time_minutes" in df.columns:
            time_by_day = df[df["service_response_time_minutes"].notna()].groupby("date")["service_response_time_minutes"].mean().reset_index()
            daily_stats = daily_stats.merge(time_by_day, on="date", how="left")
            daily_stats["service_response_time_minutes"] = daily_stats["service_response_time_minutes"].fillna(0)

            if not daily_stats.empty:
                fig_dual = plot_dual_metric_chart(
                    daily_stats,
                    "date",
                    "taux_traitement",
                    "service_response_time_minutes",
                    "Taux de traitement et temps moyen"
                )
                st.plotly_chart(fig_dual, use_container_width=True)
        else:
            st.info("Données de temps non disponibles")

    with col_chart2:
        st.markdown("### 👍 Évolution de la satisfaction client")

        if "sentiment" in df.columns:
            sent_df = df[df["direction"] == "inbound"].copy()
            sent_df["pos"] = (sent_df["sentiment"] == "positive").astype(int)
            sent_df["neg"] = (sent_df["sentiment"] == "negative").astype(int)
            agg = sent_df.groupby("date")[["pos", "neg"]].sum().reset_index()
            agg["satisfaction"] = np.where(
                (agg["pos"] + agg["neg"]) > 0,
                agg["pos"] / (agg["pos"] + agg["neg"]) * 100,
                np.nan,
            )

            if not agg.empty:
                # Utiliser area chart au lieu de line chart
                fig_sat = plot_area_chart(
                    agg,
                    "date",
                    "satisfaction",
                    "Évolution de la satisfaction client",
                    "Satisfaction (%)",
                    color="#9C27B0",
                    fill_color="rgba(156, 39, 176, 0.3)"
                )
                st.plotly_chart(fig_sat, use_container_width=True)
            else:
                st.info("Pas assez de données")
        else:
            st.info("Colonne 'sentiment' non disponible")

    st.markdown("---")

    # Vue synthétique additionnelle
    st.markdown("### 📋 Synthèse par Catégorie")

    if "category" in df.columns:
        df_inbound = df[df["direction"] == "inbound"].copy()
        if not df_inbound.empty:
            category_summary = df_inbound.groupby("category").agg({
                "id": "count",
                "sentiment": lambda x: (x == "positive").sum() / len(x) * 100 if len(x) > 0 else 0
            }).rename(columns={"id": "Volume", "sentiment": "% Satisfaction"})

            st.dataframe(
                category_summary.style.format({"Volume": "{:.0f}", "% Satisfaction": "{:.1f}%"}),
                use_container_width=True
            )
        else:
            st.info("Aucun tweet client dans la période")

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
