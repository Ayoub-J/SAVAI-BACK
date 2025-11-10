import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
import re
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import base64

# Configuration de la page Streamlit
st.set_page_config(
    page_title="POC Analyse de Tweets - Télécom",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration des styles CSS personnalisés
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79, #2d5aa0);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    .profile-section {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

class TwitterAnalyzer:
    def __init__(self, mistral_api_key: str = None):
        self.mistral_api_key = mistral_api_key
        self.mistral_api_url = "https://api.mistral.ai/v1/chat/completions"
        
    def clean_tweet(self, text: str) -> str:
        """Nettoie le texte du tweet en supprimant les mentions, URLs, etc."""
        # Suppression des URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        # Suppression des mentions @
        text = re.sub(r'@\w+', '', text)
        # Suppression des hashtags (garde le texte)
        text = re.sub(r'#(\w+)', r'\1', text)
        # Suppression des caractères spéciaux excessifs
        text = re.sub(r'[^\w\s\.,!?;:]', '', text)
        # Suppression des espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def call_mistral_api(self, prompt: str, max_tokens: int = 150) -> str:
        """Appelle l'API Mistral pour l'analyse"""
        if not self.mistral_api_key:
            # Simulation pour le POC sans API key
            return self._simulate_mistral_response(prompt)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.mistral_api_key}"
        }
        
        data = {
            "model": "mistral-small-latest",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(self.mistral_api_url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            else:
                return f"Erreur API: {response.status_code}"
        except Exception as e:
            return f"Erreur: {str(e)}"
    
    def _simulate_mistral_response(self, prompt: str) -> str:
        """Simule les réponses de Mistral pour le POC"""
        if "sentiment" in prompt.lower():
            sentiments = ["positif", "négatif", "neutre"]
            return np.random.choice(sentiments)
        elif "thème" in prompt.lower():
            themes = ["facturation", "réseau", "service client", "offres", "technique", "réclamation"]
            return np.random.choice(themes)
        elif "urgence" in prompt.lower():
            urgences = ["faible", "moyenne", "élevée"]
            return np.random.choice(urgences)
        elif "réponse" in prompt.lower():
            responses = [
                "Bonjour, nous vous remercions pour votre retour. Notre équipe va examiner votre situation.",
                "Nous sommes désolés pour ce désagrément. Un conseiller va vous contacter rapidement.",
                "Merci pour votre confiance. Nous travaillons à améliorer nos services continuellement.",
                "Votre problème est pris en compte. Vous recevrez une réponse sous 24h."
            ]
            return np.random.choice(responses)
        else:
            return "Analyse en cours..."
    
    def analyze_sentiment(self, text: str) -> str:
        """Analyse le sentiment du tweet"""
        prompt = f"""
        Analyse le sentiment de ce tweet de client télécom français et réponds uniquement par un mot: 
        "positif", "négatif", ou "neutre".
        
        Tweet: "{text}"
        
        Réponse:"""
        return self.call_mistral_api(prompt, 10)
    
    def classify_theme(self, text: str) -> str:
        """Classifie le thème du tweet"""
        prompt = f"""
        Classe ce tweet de client télécom français dans une de ces catégories et réponds uniquement par le mot correspondant:
        "facturation", "réseau", "service_client", "offres", "technique", "réclamation"
        
        Tweet: "{text}"
        
        Catégorie:"""
        return self.call_mistral_api(prompt, 10)
    
    def assess_urgency(self, text: str) -> str:
        """Évalue l'urgence du tweet"""
        prompt = f"""
        Évalue l'urgence de ce tweet de client télécom et réponds uniquement par un mot:
        "faible", "moyenne", "élevée"
        
        Tweet: "{text}"
        
        Urgence:"""
        return self.call_mistral_api(prompt, 10)
    
    def generate_response(self, text: str, sentiment: str, theme: str) -> str:
        """Génère une réponse appropriée au tweet"""
        prompt = f"""
        Génère une réponse professionnelle et empathique pour ce client télécom.
        Contexte: Sentiment {sentiment}, Thème {theme}
        
        Tweet client: "{text}"
        
        Réponse (maximum 280 caractères):"""
        return self.call_mistral_api(prompt, 100)
    
    def process_tweets(self, df: pd.DataFrame, progress_bar) -> pd.DataFrame:
        """Traite l'ensemble des tweets"""
        processed_data = []
        total_tweets = len(df)
        
        for idx, row in df.iterrows():
            # Nettoyage du tweet
            cleaned_text = self.clean_tweet(row['full_text'])
            
            # Analyse avec LLM
            sentiment = self.analyze_sentiment(cleaned_text)
            theme = self.classify_theme(cleaned_text)
            urgency = self.assess_urgency(cleaned_text)
            response = self.generate_response(cleaned_text, sentiment, theme)
            
            # Simulation du temps de traitement
            processing_time = np.random.uniform(0.5, 2.0)
            time.sleep(0.1)  # Petite pause pour l'effet visuel
            
            # Status de résolution simulé
            resolved = np.random.choice([True, False], p=[0.7, 0.3])
            
            processed_data.append({
                'id': row['id'],
                'screen_name': row['screen_name'],
                'created_at': row['created_at'],
                'original_text': row['full_text'],
                'cleaned_text': cleaned_text,
                'sentiment': sentiment.lower(),
                'theme': theme.lower(),
                'urgency': urgency.lower(),
                'generated_response': response,
                'processing_time': processing_time,
                'resolved': resolved,
                'processed_at': datetime.now()
            })
            
            # Mise à jour de la barre de progression
            progress = (idx + 1) / total_tweets
            progress_bar.progress(progress)
        
        return pd.DataFrame(processed_data)

def create_dashboard(df: pd.DataFrame, user_profile: str):
    """Crée le tableau de bord selon le profil utilisateur"""
    
    if user_profile == "Agent SAV":
        st.markdown('<div class="profile-section">', unsafe_allow_html=True)
        st.markdown("### 👤 Dashboard Agent SAV")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tweets = len(df)
            st.metric("Tweets à traiter", total_tweets)
        
        with col2:
            urgent_tweets = len(df[df['urgency'] == 'élevée'])
            st.metric("Tweets urgents", urgent_tweets, delta=f"{urgent_tweets/total_tweets*100:.1f}%")
        
        with col3:
            avg_response_time = df['processing_time'].mean()
            st.metric("Temps moyen (s)", f"{avg_response_time:.1f}")
        
        with col4:
            resolution_rate = df['resolved'].mean() * 100
            st.metric("Taux résolution", f"{resolution_rate:.1f}%")
        
        # Tweets urgents à traiter en priorité
        st.markdown("#### 🚨 Tweets urgents à traiter")
        urgent_df = df[df['urgency'] == 'élevée'].head(5)
        for idx, row in urgent_df.iterrows():
            with st.expander(f"@{row['screen_name']} - {row['theme']}"):
                st.write(f"**Tweet:** {row['original_text']}")
                st.write(f"**Réponse suggérée:** {row['generated_response']}")
                st.write(f"**Sentiment:** {row['sentiment']} | **Urgence:** {row['urgency']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif user_profile == "Analyste":
        st.markdown('<div class="profile-section">', unsafe_allow_html=True)
        st.markdown("### 📊 Dashboard Analyste")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution des sentiments
            sentiment_counts = df['sentiment'].value_counts()
            fig_sentiment = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title="Répartition des sentiments",
                color_discrete_map={'positif': '#28a745', 'négatif': '#dc3545', 'neutre': '#6c757d'}
            )
            st.plotly_chart(fig_sentiment, use_container_width=True)
        
        with col2:
            # Distribution des thèmes
            theme_counts = df['theme'].value_counts()
            fig_theme = px.bar(
                x=theme_counts.index,
                y=theme_counts.values,
                title="Répartition des thèmes",
                color=theme_counts.values,
                color_continuous_scale='Blues'
            )
            fig_theme.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_theme, use_container_width=True)
        
        # Analyse croisée sentiment/thème
        st.markdown("#### Analyse sentiment par thème")
        sentiment_theme = pd.crosstab(df['theme'], df['sentiment'])
        fig_heatmap = px.imshow(
            sentiment_theme.values,
            x=sentiment_theme.columns,
            y=sentiment_theme.index,
            color_continuous_scale='RdYlBu_r',
            title="Matrice Sentiment x Thème"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Urgence par thème
        st.markdown("#### Analyse urgence par thème")
        urgency_theme = pd.crosstab(df['theme'], df['urgency'])
        fig_urgency = px.bar(
            urgency_theme,
            title="Distribution de l'urgence par thème",
            color_discrete_map={'faible': '#28a745', 'moyenne': '#ffc107', 'élevée': '#dc3545'}
        )
        st.plotly_chart(fig_urgency, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif user_profile == "Manager/Direction":
        st.markdown('<div class="profile-section">', unsafe_allow_html=True)
        st.markdown("### 📈 Dashboard Direction")
        
        # KPIs principaux
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_tweets = len(df)
        resolution_rate = df['resolved'].mean() * 100
        avg_processing_time = df['processing_time'].mean()
        negative_sentiment_rate = (df['sentiment'] == 'négatif').mean() * 100
        high_urgency_rate = (df['urgency'] == 'élevée').mean() * 100
        
        with col1:
            st.metric("Volume total", f"{total_tweets:,}")
        with col2:
            st.metric("Taux résolution", f"{resolution_rate:.1f}%")
        with col3:
            st.metric("Temps moyen (s)", f"{avg_processing_time:.1f}")
        with col4:
            st.metric("Sentiment négatif", f"{negative_sentiment_rate:.1f}%")
        with col5:
            st.metric("Tweets urgents", f"{high_urgency_rate:.1f}%")
        
        # Évolution temporelle (simulation)
        st.markdown("#### Évolution des volumes et KPIs")
        
        # Simulation de données temporelles
        dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='D')
        daily_volume = np.random.randint(50, 200, len(dates))
        daily_resolution = np.random.uniform(65, 85, len(dates))
        
        fig_evolution = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_evolution.add_trace(
            go.Bar(x=dates, y=daily_volume, name="Volume tweets", marker_color='lightblue'),
            secondary_y=False,
        )
        
        fig_evolution.add_trace(
            go.Scatter(x=dates, y=daily_resolution, mode='lines+markers', 
                      name="Taux résolution (%)", line=dict(color='red', width=3)),
            secondary_y=True,
        )
        
        fig_evolution.update_xaxes(title_text="Date")
        fig_evolution.update_yaxes(title_text="Volume", secondary_y=False)
        fig_evolution.update_yaxes(title_text="Taux résolution (%)", secondary_y=True)
        fig_evolution.update_layout(title="Évolution des volumes et taux de résolution")
        
        st.plotly_chart(fig_evolution, use_container_width=True)
        
        # Analyse des problèmes critiques
        st.markdown("#### Analyse des problèmes critiques")
        critical_issues = df[(df['sentiment'] == 'négatif') & (df['urgency'] == 'élevée')]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Problèmes critiques", len(critical_issues))
            if len(critical_issues) > 0:
                critical_themes = critical_issues['theme'].value_counts()
                fig_critical = px.bar(
                    x=critical_themes.values,
                    y=critical_themes.index,
                    orientation='h',
                    title="Thèmes des problèmes critiques",
                    color=critical_themes.values,
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig_critical, use_container_width=True)
        
        with col2:
            # Recommandations automatiques
            st.markdown("##### 💡 Recommandations")
            recommendations = []
            
            if negative_sentiment_rate > 30:
                recommendations.append("⚠️ Taux de sentiment négatif élevé - Renforcer la formation SAV")
            
            if high_urgency_rate > 25:
                recommendations.append("🚨 Nombreux tweets urgents - Augmenter les effectifs")
            
            if resolution_rate < 70:
                recommendations.append("📊 Taux de résolution faible - Revoir les processus")
            
            if avg_processing_time > 1.5:
                recommendations.append("⏱️ Temps de traitement lent - Optimiser les workflows")
            
            if not recommendations:
                recommendations.append("✅ Tous les indicateurs sont dans les objectifs")
            
            for rec in recommendations:
                st.write(rec)
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    # En-tête principal
    st.markdown("""
    <div class="main-header">
        <h1>📱 POC Analyse de Tweets - Solution Télécom</h1>
        <p>Automatisation du traitement et classification des tweets clients</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar pour la configuration
    st.sidebar.markdown("## ⚙️ Configuration")
    
    # Sélection du profil utilisateur
    user_profile = st.sidebar.selectbox(
        "Profil utilisateur:",
        ["Agent SAV", "Analyste", "Manager/Direction"]
    )
    
    # Configuration API Mistral (optionnelle)
    st.sidebar.markdown("### API Mistral AI")
    mistral_key = st.sidebar.text_input(
        "Clé API Mistral (optionnelle):",
        type="password",
        help="Laissez vide pour utiliser la simulation"
    )
    
    if not mistral_key:
        st.sidebar.info("Mode simulation activé (sans API Mistral)")
    
    # Upload du fichier CSV
    st.sidebar.markdown("### 📁 Import des données")
    uploaded_file = st.sidebar.file_uploader(
        "Choisir un fichier CSV:",
        type=['csv'],
        help="Format: id, full_text, screen_name, created_at"
    )
    
    if uploaded_file is not None:
        try:
            # Lecture du fichier CSV
            df = pd.read_csv(uploaded_file)
            
            # Validation des colonnes requises
            required_columns = ['id', 'full_text', 'screen_name', 'created_at']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"Colonnes manquantes: {', '.join(missing_columns)}")
                return
            
            # Affichage des informations sur le dataset
            st.sidebar.success(f"✅ {len(df)} tweets chargés")
            
            # Aperçu des données
            with st.expander("👀 Aperçu des données brutes"):
                st.dataframe(df.head())
            
            # Traitement des tweets
            if st.sidebar.button("🚀 Lancer l'analyse", type="primary"):
                
                st.markdown("## 🔄 Traitement en cours...")
                
                # Initialisation de l'analyseur
                analyzer = TwitterAnalyzer(mistral_key)
                
                # Barre de progression
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Traitement des tweets
                with st.spinner("Analyse et classification des tweets..."):
                    processed_df = analyzer.process_tweets(df, progress_bar)
                
                progress_bar.empty()
                status_text.success("✅ Traitement terminé!")
                
                # Stockage en session pour éviter de reprocesser
                st.session_state['processed_data'] = processed_df
                st.session_state['user_profile'] = user_profile
                
                # Affichage du dashboard
                st.markdown("## 📊 Dashboard")
                create_dashboard(processed_df, user_profile)
                
                # Export des résultats
                st.markdown("## 📥 Export des résultats")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    csv_export = processed_df.to_csv(index=False)
                    st.download_button(
                        label="💾 Télécharger CSV complet",
                        data=csv_export,
                        file_name=f"tweets_analyzed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    # Export JSON pour intégration API
                    json_export = processed_df.to_json(orient='records', date_format='iso')
                    st.download_button(
                        label="📄 Télécharger JSON",
                        data=json_export,
                        file_name=f"tweets_analyzed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        
        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier: {str(e)}")
    
    # Si des données sont déjà en session, afficher le dashboard
    elif 'processed_data' in st.session_state:
        st.markdown("## 📊 Dashboard")
        create_dashboard(st.session_state['processed_data'], user_profile)
    
    else:
        # Affichage des informations sur la solution
        st.markdown("""
        ## 🎯 À propos de cette solution
        
        Ce POC démontre une solution complète d'analyse automatisée des tweets clients pour un opérateur télécom.
        
        ### 🔧 Fonctionnalités démontrées:
        - **Nettoyage automatique** des tweets (suppression URLs, mentions, etc.)
        - **Classification par sentiment** (positif, négatif, neutre)
        - **Catégorisation thématique** (facturation, réseau, service client, etc.)
        - **Évaluation d'urgence** (faible, moyenne, élevée)
        - **Génération de réponses** automatisées et contextuelles
        - **Dashboards personnalisés** par profil utilisateur
        
        ### 👥 Profils utilisateurs:
        - **Agent SAV**: Vue opérationnelle avec tweets urgents et réponses suggérées
        - **Analyste**: Analyses statistiques et corrélations thématiques
        - **Manager/Direction**: KPIs stratégiques et recommandations
        
        ### 📋 Format de données attendu:
        ```
        id,full_text,screen_name,created_at
        123456,"Problème avec ma facture",@client1,2024-01-15 10:30:00
        123457,"Excellente qualité réseau",@client2,2024-01-15 11:00:00
        ```
        """)
        
        # Exemple de données pour test
        st.markdown("### 💡 Exemple de données de test")
        example_data = """id,full_text,screen_name,created_at
1234567890,"@OperateurTel votre service client est catastrophique ! 2h d'attente pour rien !",client_furieux,2024-11-24 09:15:00
1234567891,"Merci @OperateurTel pour la résolution rapide de mon problème de connexion 👍",client_satisfait,2024-11-24 09:30:00
1234567892,"Ma facture a doublé sans explication, pouvez-vous me contacter svp ?",client_inquiet,2024-11-24 10:00:00
1234567893,"Réseau 5G excellent dans ma région, bravo !",client_content,2024-11-24 10:15:00
1234567894,"Impossible de joindre le SAV depuis 3 jours, c'est inacceptable !",client_enerve,2024-11-24 10:30:00"""
        
        st.code(example_data, language='csv')
        
        # Bouton pour télécharger l'exemple
        st.download_button(
            label="📥 Télécharger l'exemple CSV",
            data=example_data,
            file_name="exemple_tweets.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()