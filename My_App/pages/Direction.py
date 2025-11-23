import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Direction - Free SAV", layout="wide")

# -------------------------------------------------------
# 🔒 Vérification des données importées
# -------------------------------------------------------
if "data" not in st.session_state:
    st.error("⚠️ Aucun fichier CSV importé. Retournez à la page d’accueil.")
    st.stop()

df = st.session_state["data"].copy()

# Nettoyage minimal (au cas où)
df["sentiment"] = df["sentiment"].astype(str).str.lower()
df["theme"] = df["theme"].astype(str)
df["urgence"] = df["urgence"].astype(str)

# -------------------------------------------------------
# 🟥 TITRE FIGMA
# -------------------------------------------------------
st.markdown("""
<h1 style="margin-bottom:5px;">🏛 Tableau de Bord Direction</h1>
<p style="font-size:18px; color:#666;">Vue stratégique & KPIs</p>
""", unsafe_allow_html=True)


# -------------------------------------------------------
# 🟦 TOP KPIs (Figma)
# -------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Volume total", df.shape[0])

with col2:
    treated_rate = f"{round(df['confiance'].mean() * 100, 1)}%"
    st.metric("Taux confiance moyen", treated_rate)

with col3:
    urgent_ratio = (df["urgence"] == "élevée").mean() * 100
    st.metric("Tweets urgents (%)", f"{urgent_ratio:.1f}%")

with col4:
    positive_ratio = (df["sentiment"] == "positif").mean() * 100
    st.metric("Sentiment positif", f"{positive_ratio:.1f}%")

st.write("---")


# -------------------------------------------------------
# 📅 COURBE VOLUME PAR JOUR (Figma)
# -------------------------------------------------------

st.markdown("### 📈 Volume quotidien des Tweets")

# Fake date colonne si absente
df["date"] = pd.to_datetime("2024-01-01") + pd.to_timedelta(df.index, unit="h")
df["day"] = df["date"].dt.date

volume_daily = df.groupby("day").size().reset_index(name="count")

fig_volume = px.area(
    volume_daily,
    x="day",
    y="count",
    title="Évolution du volume de tweets",
    markers=True
)
fig_volume.update_layout(showlegend=False)

st.plotly_chart(fig_volume, use_container_width=True)

st.write("---")


# -------------------------------------------------------
# 🎭 RÉPARTITION SENTIMENTS
# -------------------------------------------------------

st.markdown("### 🎭 Répartition des sentiments")

sent_counts = df["sentiment"].value_counts()

fig_sent = px.pie(
    names=sent_counts.index,
    values=sent_counts.values,
    color=sent_counts.index,
    color_discrete_map={
        "positif": "#2ecc71",
        "negatif": "#e74c3c",
        "neutre": "#95a5a6"
    }
)
st.plotly_chart(fig_sent, use_container_width=True)

st.write("---")


# -------------------------------------------------------
# 🟪 THEMES
# -------------------------------------------------------

st.markdown("### 🟪 Répartition des thèmes")

theme_counts = df["theme"].value_counts()

fig_theme = px.bar(
    theme_counts,
    title="Thèmes les plus fréquents",
    color=theme_counts.index,
    color_discrete_sequence=px.colors.qualitative.Set3
)

st.plotly_chart(fig_theme, use_container_width=True)

st.write("---")


# -------------------------------------------------------
# 🔥 URGENCE
# -------------------------------------------------------

st.markdown("### 🔥 Urgences")

urgence_counts = df["urgence"].value_counts()

fig_urg = px.bar(
    urgence_counts,
    title="Répartition des niveaux d’urgence",
    color=urgence_counts.index,
    color_discrete_sequence=px.colors.qualitative.Pastel
)

st.plotly_chart(fig_urg, use_container_width=True)

st.write("---")


# -------------------------------------------------------
# 🧠 ANALYSE STRATÉGIQUE
# -------------------------------------------------------

st.markdown("### 🧠 Analyse stratégique automatique")

analysis_list = []

# Volume moyen
if df.shape[0] > 2000:
    analysis_list.append("📌 Volume élevé → risque de surcharge dans les équipes.")
elif df.shape[0] > 1000:
    analysis_list.append("📌 Volume stable → charge normale.")
else:
    analysis_list.append("📌 Volume faible → marge d'optimisation possible.")

# Sentiment
neg = (df["sentiment"] == "negatif").mean()

if neg > 0.30:
    analysis_list.append("🔴 Niveau élevé de tweets négatifs → risque d'incident réseau ou insatisfaction.")
elif neg > 0.20:
    analysis_list.append("🟠 Niveau modéré de négatif → surveiller les causes.")
else:
    analysis_list.append("🟢 Sentiment global satisfaisant.")

# Urgence
urgent = (df["urgence"] == "élevée").mean()

if urgent > 0.25:
    analysis_list.append("🚨 Beaucoup d'urgences → renforcer la capacité de réponse.")
else:
    analysis_list.append("🟢 Les urgences sont sous contrôle.")

for item in analysis_list:
    st.markdown(f"- {item}")
