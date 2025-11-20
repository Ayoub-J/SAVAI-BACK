# ui/charts.py
"""
Graphiques Plotly professionnels pour analytics
Style moderne avec couleurs personnalisées
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st


# Palette de couleurs professionnelle
COLORS = {
    'primary': '#4A90E2',      # Bleu
    'success': '#7ED321',      # Vert
    'warning': '#F5A623',      # Orange
    'danger': '#D0021B',       # Rouge
    'purple': '#9013FE',       # Violet
    'cyan': '#50E3C2',         # Cyan
    'pink': '#FF6B9D',         # Rose
    'teal': '#00C9A7',         # Turquoise

    # Palette graphiques
    'recu': '#5B8DEE',         # Bleu pour "Reçus"
    'resolu': '#4CAF50',       # Vert pour "Résolus"

    # Catégories (palette arc-en-ciel)
    'cat1': '#FF6384',  # Rouge-rose (Panne Internet)
    'cat2': '#FF9F40',  # Orange (Facturation)
    'cat3': '#4BC0C0',  # Cyan (Débit Internet)
    'cat4': '#36A2EB',  # Bleu (Espace Client)
    'cat5': '#9966FF',  # Violet (Fibre)
    'cat6': '#FF6BB5',  # Rose (Résiliation)
    'cat7': '#00CED1',  # Turquoise (Remerciement)
}


def plot_line_chart(df, x_col, y_col, title, y_label, color='#FF9F40'):
    """
    Graphique en ligne style temps de réponse

    Args:
        df: DataFrame avec données
        x_col: Colonne pour axe X
        y_col: Colonne pour axe Y
        title: Titre du graphique
        y_label: Label axe Y
        color: Couleur de la ligne
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode='lines+markers',
        name=y_label,
        line=dict(color=color, width=3),
        marker=dict(size=8, color=color, symbol='circle'),
        hovertemplate='%{x}<br>%{y:.1f} min<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>⏱️ {title}</b>",
            font=dict(size=16, color='#333')
        ),
        xaxis=dict(
            title='',
            showgrid=True,
            gridcolor='#E5E5E5',
            gridwidth=1,
            zeroline=False
        ),
        yaxis=dict(
            title='',
            showgrid=True,
            gridcolor='#E5E5E5',
            gridwidth=1,
            zeroline=True,
            zerolinecolor='#E5E5E5'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified',
        height=300,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return fig


def plot_dual_bar_chart(df, x_col, y1_col, y2_col, title, label1='Reçus', label2='Résolus'):
    """
    Graphique à barres groupées (Reçus vs Résolus)

    Args:
        df: DataFrame avec données
        x_col: Colonne pour axe X (dates)
        y1_col: Colonne valeurs 1 (Reçus)
        y2_col: Colonne valeurs 2 (Résolus)
        title: Titre du graphique
    """
    fig = go.Figure()

    # Barres Reçus (bleu)
    fig.add_trace(go.Bar(
        x=df[x_col],
        y=df[y1_col],
        name=label1,
        marker_color=COLORS['recu'],
        hovertemplate='%{x}<br>' + label1 + ': %{y}<extra></extra>'
    ))

    # Barres Résolus (vert)
    fig.add_trace(go.Bar(
        x=df[x_col],
        y=df[y2_col],
        name=label2,
        marker_color=COLORS['resolu'],
        hovertemplate='%{x}<br>' + label2 + ': %{y}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>📊 {title}</b>",
            font=dict(size=16, color='#333')
        ),
        xaxis=dict(
            title='',
            showgrid=False
        ),
        yaxis=dict(
            title='',
            showgrid=True,
            gridcolor='#E5E5E5',
            gridwidth=1
        ),
        barmode='group',
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        height=300,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return fig


def plot_pie_chart(df, values_col, names_col, title):
    """
    Graphique circulaire (Pie chart) avec pourcentages et légende

    Args:
        df: DataFrame avec données
        values_col: Colonne avec valeurs
        names_col: Colonne avec noms catégories
        title: Titre du graphique
    """
    # Palette de couleurs pour les catégories
    colors_list = [
        COLORS['cat1'], COLORS['cat2'], COLORS['cat3'],
        COLORS['cat4'], COLORS['cat5'], COLORS['cat6'], COLORS['cat7']
    ]

    # Trier par valeurs décroissantes
    df_sorted = df.sort_values(by=values_col, ascending=False)

    fig = go.Figure()

    fig.add_trace(go.Pie(
        labels=df_sorted[names_col],
        values=df_sorted[values_col],
        hole=0,  # Pas de donut, pie complet
        marker=dict(
            colors=colors_list[:len(df_sorted)],
            line=dict(color='white', width=2)
        ),
        textposition='inside',
        textinfo='percent',
        textfont=dict(size=14, color='white', family='Arial Bold'),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>',
        showlegend=True
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>🎯 {title}</b>",
            font=dict(size=16, color='#333')
        ),
        paper_bgcolor='white',
        height=400,
        margin=dict(l=40, r=200, t=60, b=40),  # Plus de marge à droite pour légende
        legend=dict(
            orientation='v',
            yanchor='middle',
            y=0.5,
            xanchor='left',
            x=1.05,
            font=dict(size=12)
        )
    )

    return fig


def plot_horizontal_bar_chart(df, x_col, y_col, title, color='#4A90E2'):
    """
    Graphique à barres horizontales (ex: top mots)

    Args:
        df: DataFrame avec données
        x_col: Colonne pour valeurs (axe X)
        y_col: Colonne pour labels (axe Y)
        title: Titre du graphique
        color: Couleur des barres
    """
    # Trier par valeur décroissante et prendre top 20
    df_sorted = df.sort_values(by=x_col, ascending=True).tail(20)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_sorted[x_col],
        y=df_sorted[y_col],
        orientation='h',
        marker_color=color,
        hovertemplate='<b>%{y}</b><br>Occurrences: %{x}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>📝 {title}</b>",
            font=dict(size=16, color='#333')
        ),
        xaxis=dict(
            title='',
            showgrid=True,
            gridcolor='#E5E5E5'
        ),
        yaxis=dict(
            title='',
            showgrid=False
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,
        margin=dict(l=100, r=40, t=60, b=40)
    )

    return fig


def plot_simple_bar_chart(df, x_col, y_col, title, color='#5B8DEE'):
    """
    Graphique à barres simple vertical

    Args:
        df: DataFrame avec données
        x_col: Colonne pour axe X
        y_col: Colonne pour valeurs
        title: Titre du graphique
        color: Couleur des barres
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df[x_col],
        y=df[y_col],
        marker_color=color,
        hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=16, color='#333')
        ),
        xaxis=dict(
            title='',
            showgrid=False
        ),
        yaxis=dict(
            title='',
            showgrid=True,
            gridcolor='#E5E5E5',
            gridwidth=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=300,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return fig


def plot_performance_chart(df, agent_col, count_col, title):
    """
    Graphique performance agents (barres horizontales)
    """
    df_sorted = df.sort_values(by=count_col, ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_sorted[count_col],
        y=df_sorted[agent_col],
        orientation='h',
        marker_color='#7ED321',
        hovertemplate='<b>%{y}</b><br>Tweets traités: %{x}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>👥 {title}</b>",
            font=dict(size=16, color='#333')
        ),
        xaxis=dict(
            title='Nombre de tweets traités',
            showgrid=True,
            gridcolor='#E5E5E5'
        ),
        yaxis=dict(
            title='',
            showgrid=False
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=300,
        margin=dict(l=100, r=40, t=60, b=40)
    )

    return fig


def plot_stacked_bar_sentiment_category(crosstab_df, title="Analyse de sentiment par catégorie"):
    """
    Graphique en barres empilées 100% pour sentiment par catégorie
    Inspiré du style "Analyse de sentiment par thème"

    Args:
        crosstab_df: DataFrame résultat de pd.crosstab(category, sentiment)
        title: Titre du graphique

    Returns:
        Plotly Figure
    """
    # Couleurs pour sentiments (rouge, orange, vert)
    sentiment_colors = {
        'negative': '#D0021B',    # Rouge
        'neutral': '#F5A623',     # Orange
        'positive': '#008000',    # Vert foncé
        'mixed': '#FF9F40'        # Orange clair
    }

    # Normaliser pour obtenir des proportions (0-1)
    df_pct = crosstab_df.div(crosstab_df.sum(axis=1), axis=0)

    # Créer figure
    fig = go.Figure()

    # Ordre des sentiments (du négatif au positif)
    sentiment_order = ['negative', 'neutral', 'positive', 'mixed']

    # Ajouter une trace par sentiment
    for sentiment in sentiment_order:
        if sentiment in df_pct.columns:
            fig.add_trace(go.Bar(
                name=sentiment.capitalize(),
                x=df_pct.index,
                y=df_pct[sentiment],
                marker_color=sentiment_colors.get(sentiment, '#999999'),
                text=[f"{val*100:.1f}%" for val in df_pct[sentiment]],
                textposition='inside',
                textfont=dict(size=12, color='white'),
                hovertemplate='<b>%{x}</b><br>' + sentiment.capitalize() + ': %{y:.1%}<extra></extra>'
            ))

    fig.update_layout(
        title=dict(
            text=f"<b>📊 {title}</b>",
            font=dict(size=16, color='#333')
        ),
        barmode='stack',
        xaxis=dict(
            title='',
            showgrid=False,
            tickangle=-45
        ),
        yaxis=dict(
            title='Proportion',
            showgrid=True,
            gridcolor='#E5E5E5',
            tickformat='.0%',
            range=[0, 1]
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(
            title='Sentiment',
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        height=400,
        margin=dict(l=60, r=40, t=80, b=120),
        hovermode='x unified'
    )

    return fig


def plot_area_chart(df, x_col, y_col, title, y_label, color='#4BC0C0', fill_color='rgba(75, 192, 192, 0.3)'):
    """
    Graphique en aire (area chart) pour évolution temporelle

    Args:
        df: DataFrame avec données
        x_col: Colonne pour axe X (dates)
        y_col: Colonne pour valeurs
        title: Titre du graphique
        y_label: Label axe Y
        color: Couleur de la ligne
        fill_color: Couleur de remplissage (avec transparence)
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode='lines',
        name=y_label,
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=fill_color,
        hovertemplate='%{x}<br>%{y:.1f}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=16, color='#333')
        ),
        xaxis=dict(
            title='',
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title='',
            showgrid=True,
            gridcolor='#E5E5E5',
            gridwidth=1,
            zeroline=True
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified',
        height=300,
        margin=dict(l=50, r=40, t=60, b=40)
    )

    return fig


def plot_stacked_area_chart(df, x_col, y1_col, y2_col, title, label1='Volume reçu', label2='Résolus'):
    """
    Graphique en aires empilées (stacked area) pour volume et traitement
    Style inspiré de l'image avec dégradé bleu/vert

    Args:
        df: DataFrame avec données
        x_col: Colonne pour axe X (dates)
        y1_col: Colonne valeurs 1 (Volume total)
        y2_col: Colonne valeurs 2 (Résolus)
        title: Titre du graphique
    """
    fig = go.Figure()

    # Aire pour résolus (vert en bas)
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y2_col],
        mode='lines',
        name=label2,
        line=dict(color='#4CAF50', width=0),
        fill='tozeroy',
        fillcolor='rgba(76, 175, 80, 0.6)',
        stackgroup='one',
        hovertemplate='%{x}<br>' + label2 + ': %{y}<extra></extra>'
    ))

    # Aire pour volume reçu (bleu au-dessus)
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y1_col],
        mode='lines',
        name=label1,
        line=dict(color='#5B8DEE', width=0),
        fill='tonexty',
        fillcolor='rgba(91, 141, 238, 0.6)',
        stackgroup='one',
        hovertemplate='%{x}<br>' + label1 + ': %{y}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>📈 {title}</b>",
            font=dict(size=16, color='#333')
        ),
        xaxis=dict(
            title='',
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title='',
            showgrid=True,
            gridcolor='#E5E5E5',
            gridwidth=1,
            zeroline=True
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5
        ),
        hovermode='x unified',
        height=350,
        margin=dict(l=50, r=40, t=60, b=80)
    )

    return fig


def plot_dual_metric_chart(df, x_col, y1_col, y2_col, title, label1='Taux de traitement (%)', label2='Temps moyen (min)',
                           color1='#4CAF50', color2='#FF9F40'):
    """
    Graphique avec deux axes Y (barres + ligne)
    Pour afficher taux de traitement (barres) et temps moyen (ligne)

    Args:
        df: DataFrame avec données
        x_col: Colonne pour axe X (dates)
        y1_col: Colonne pour barres (ex: taux)
        y2_col: Colonne pour ligne (ex: temps)
        title: Titre du graphique
    """
    fig = go.Figure()

    # Barres pour taux de traitement (axe Y gauche)
    fig.add_trace(go.Bar(
        x=df[x_col],
        y=df[y1_col],
        name=label1,
        marker_color=color1,
        yaxis='y',
        hovertemplate='%{x}<br>' + label1 + ': %{y:.1f}%<extra></extra>'
    ))

    # Ligne pour temps moyen (axe Y droit)
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y2_col],
        name=label2,
        line=dict(color=color2, width=3),
        mode='lines+markers',
        marker=dict(size=6),
        yaxis='y2',
        hovertemplate='%{x}<br>' + label2 + ': %{y:.1f} min<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>📊 {title}</b>",
            font=dict(size=16, color='#333')
        ),
        xaxis=dict(
            title='',
            showgrid=False
        ),
        yaxis=dict(
            title=label1,
            showgrid=True,
            gridcolor='#E5E5E5',
            side='left'
        ),
        yaxis2=dict(
            title=label2,
            overlaying='y',
            side='right',
            showgrid=False
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.25,
            xanchor='center',
            x=0.5
        ),
        hovermode='x unified',
        height=350,
        margin=dict(l=60, r=60, t=60, b=80)
    )

    return fig
