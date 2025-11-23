# %% [markdown]
# # 📊 Analyse du Dataset Tweets - Service Client Free
# 
# ### 🎯 Objectif
# Identifier et éliminer les tweets non nécessaires ou erronés pour optimiser le traitement des vraies demandes clients.
# 
# ### 📚 Structure du notebook
# 1. Import et configuration
# 2. Chargement et exploration des données
# 3. Analyse de la qualité des données
# 4. Identification des tweets problématiques
# 5. Nettoyage et structuration
# 6. Recommandations et règles de filtrage
# 7. Métriques de performance
# 8. Export des résultats

# %% [markdown]
# ## 1. Import des librairies et configuration

# %%
import pandas as pd
import numpy as np
from datetime import datetime
import re
import warnings
import os

warnings.filterwarnings('ignore')

# Configuration de l'affichage
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 100)

print("✅ Librairies importées avec succès")
print(f"📅 Date d'analyse: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# %% [markdown]
# ## 2. Chargement et exploration initiale des données

# %%
# Chargement du fichier CSV
file_path = 'LLM-classified-data/free tweet export.csv'
df = pd.read_csv(file_path)

print("📊 INFORMATIONS GÉNÉRALES DU DATASET")
print("=" * 60)
print(f"Nombre de tweets: {len(df):,}")
print(f"Nombre de colonnes: {len(df.columns)}")
print(f"\nPériode couverte:")
print(f"  • Du: {df['created_at'].min()}")
print(f"  • Au: {df['created_at'].max()}")

print("\n📋 Colonnes disponibles:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:2}. {col}")

# %%
nb_doublons = df.duplicated().sum()
print(f"Nombre de doublons : {nb_doublons}")

# %%
doubl = df[df.duplicated()].sum()
print(doubl)

# %%
# Analyse de la complétude des données
print("📊 ANALYSE DE LA COMPLÉTUDE DES DONNÉES")
print("=" * 60)

completeness_data = []
for col in df.columns:
    non_null = df[col].notna().sum()
    null_count = df[col].isna().sum()
    completeness = (non_null / len(df)) * 100
    completeness_data.append({
        'Colonne': col,
        'Valeurs_Non_Null': non_null,
        'Valeurs_Null': null_count,
        'Complétude_%': round(completeness, 1)
    })

completeness_df = pd.DataFrame(completeness_data)
completeness_df = completeness_df.sort_values('Complétude_%', ascending=False)

print(completeness_df.to_string(index=False))

# %% [markdown]
# ## 3. Préparation du dataset avec les colonnes demandées

# %%
# Garder uniquement les colonnes demandées
colonnes_a_garder = ['id', 'created_at', 'full_text', 'screen_name', 'name', 'user_id', 'in_reply_to']

# Vérifier que toutes les colonnes existent
colonnes_manquantes = [col for col in colonnes_a_garder if col not in df.columns]
if colonnes_manquantes:
    print(f"⚠️ Colonnes manquantes: {colonnes_manquantes}")
else:
    print("✅ Toutes les colonnes demandées sont présentes")

# Créer le dataset nettoyé
df_clean = df[colonnes_a_garder].copy()

print(f"\n📋 Dataset restructuré:")
print(f"  • Nombre de colonnes conservées: {len(df_clean.columns)}")
print(f"  • Nombre de lignes: {len(df_clean):,}")
print(f"\nAperçu des premières lignes:")
print(df_clean.head())
print("\nInfos:")
print(df_clean.info())

# %% [markdown]
# ## 4. Fonction de catégorisation des tweets

# %%
def categorize_tweet(text):
    """
    Catégorise un tweet selon son contenu.
    """
    if pd.isna(text):
        return "Vide"
    
    text = str(text).lower()
    
    patterns = {
        "RT/Partage": r'^rt @',
        "Message automatique Freebox": r'messagerie privée x n\'est plus disponible|retrouvez-moi|messenger|https://t\.co/fozuyqkg|via https://t\.co/3rzd3',
        "Plainte service": r'coupure|panne|problème|pas de connexion|ne fonctionne pas|bug|instable|service client|pire opérateur|hs',
        "Demande d'aide": r'besoin d\'aide|j\'ai besoin|aidez-moi|help|svp|s\'il vous plaît|sos',
        "Question technique": r'comment|pourquoi|qu\'est-ce|fibre|débit|wifi|connexion|installation',
        "Spam/Promotion": r'💩|via @fingapp|@outagedetect|disponible sur le canal|nouveau|offert',
        "Réclamation RDV": r'technicien|rdv|rendez-vous|pas venu|attendre|créneau',
        "Info/Annonce": r'retrouvez|nouvelle|découvrez'
    }
    
    for category, pattern in patterns.items():
        if re.search(pattern, text):
            return category
    
    return "Autre"

# Appliquer la catégorisation
df_clean['categorie'] = df_clean['full_text'].apply(categorize_tweet)

print("✅ Catégorisation effectuée")

# %% [markdown]
# ## 5. Analyse des catégories de tweets (sans graphiques)

# %%
category_stats = df_clean['categorie'].value_counts()
category_percentages = (category_stats / len(df_clean) * 100).round(1)

stats_df = pd.DataFrame({
    'Catégorie': category_stats.index,
    'Nombre': category_stats.values,
    'Pourcentage': category_percentages.values
})

print("📊 RÉPARTITION DES TWEETS PAR CATÉGORIE")
print("=" * 60)
print(stats_df.to_string(index=False))

# %% [markdown]
# ## 6. Identification des tweets problématiques

# %%
def is_unnecessary_or_erroneous(row):
    """
    Identifie si un tweet est non nécessaire ou erroné.
    """
    issues = []
    
    if pd.isna(row['full_text']):
        issues.append("Texte vide")
        return True, issues
    
    text = str(row['full_text']).lower()
    
    if row['categorie'] == 'Message automatique Freebox':
        issues.append("Réponse automatique répétitive")
    
    if row['categorie'] == 'RT/Partage':
        issues.append("Retweet (pas une demande directe)")
    
    if row['categorie'] == 'Spam/Promotion':
        issues.append("Spam ou promotion non pertinente")
    
    if len(str(row['full_text'])) < 20:
        issues.append("Tweet trop court (<20 caractères)")
    
    if 'la messagerie privée x n\'est plus disponible' in text and row['screen_name'] == 'Freebox':
        issues.append("Message standard répétitif de Freebox")
    
    if row['in_reply_to'] == 'null' and len(text) < 50 and '?' not in text and row['screen_name'] != 'Freebox':
        issues.append("Message court sans contexte ni question")
    
    return len(issues) > 0, issues

print("🔍 Analyse des tweets problématiques en cours...")

problematic_tweets = []
for idx, row in df_clean.iterrows():
    is_problematic, issues = is_unnecessary_or_erroneous(row)
    if is_problematic:
        problematic_tweets.append({
            'index': idx,
            'id': row['id'],
            'screen_name': row['screen_name'],
            'categorie': row['categorie'],
            'issues': ', '.join(issues),
            'extrait': str(row['full_text'])[:100] + '...' if len(str(row['full_text'])) > 100 else str(row['full_text'])
        })

df_problematic = pd.DataFrame(problematic_tweets)

print(f"\n⚠️ RÉSULTATS DE L'ANALYSE")
print("=" * 60)
print(f"Tweets problématiques identifiés: {len(df_problematic):,} sur {len(df_clean):,}")
print(f"Pourcentage de tweets problématiques: {len(df_problematic)*100/len(df_clean):.1f}%")
print(f"Tweets pertinents conservés: {len(df_clean) - len(df_problematic):,}")
print(f"Pourcentage de tweets pertinents: {(len(df_clean) - len(df_problematic))*100/len(df_clean):.1f}%\n")

# %%
# Analyse des types de problèmes
if len(df_problematic) > 0:
    issues_split = df_problematic['issues'].str.split(', ', expand=True).stack()
    issue_counts = issues_split.value_counts()
    
    print("\n📊 TOP DES PROBLÈMES IDENTIFIÉS")
    print("=" * 60)
    
    issue_stats = pd.DataFrame({
        'Problème': issue_counts.index[:10],
        'Occurrences': issue_counts.values[:10],
        'Pourcentage': (issue_counts.values[:10] / len(df_problematic) * 100).round(1)
    })
    
    print(issue_stats.to_string(index=False))

# %% [markdown]
# ## 7. Analyse des comptes les plus actifs (sans graphiques)

# %%
user_stats = df_clean.groupby('screen_name').agg({
    'id': 'count',
    'categorie': lambda x: x.mode()[0] if len(x) > 0 else 'N/A'
}).sort_values('id', ascending=False).head(15)
user_stats.columns = ['nombre_tweets', 'categorie_principale']

print("👥 TOP 15 DES COMPTES LES PLUS ACTIFS")
print("=" * 60)

user_display = user_stats.reset_index()
user_display['pourcentage'] = (user_display['nombre_tweets'] / len(df_clean) * 100).round(2)
print(user_display.to_string(index=False))

# %% [markdown]
# ## 8. Exemples de tweets problématiques

# %%
print("📝 EXEMPLES DE TWEETS PROBLÉMATIQUES")
print("=" * 80)

if len(df_problematic) > 0:
    unique_issues = df_problematic['issues'].unique()[:5]
    
    for issue_type in unique_issues:
        print(f"\n🔸 Problème: {issue_type}")
        print("-" * 60)
        
        examples = df_problematic[df_problematic['issues'] == issue_type].head(5)
        
        for idx, row in examples.iterrows():
            print(f"  • @{row['screen_name']}: \"{row['extrait']}\"")
            print(f"    Catégorie: {row['categorie']}")
            print()

# %% [markdown]
# ## 9. Création du dataset final nettoyé

# %%
df_final = df_clean[~df_clean.index.isin(df_problematic['index'])]

print("✅ NETTOYAGE FINAL EFFECTUÉ")
print("=" * 60)
print(f"Tweets conservés: {len(df_final):,} sur {len(df_clean):,} ({len(df_final)*100/len(df_clean):.1f}%)")
print(f"Tweets supprimés: {len(df_clean) - len(df_final):,} ({(len(df_clean) - len(df_final))*100/len(df_clean):.1f}%)")

final_category_stats = df_final['categorie'].value_counts()

print("\n📊 RÉPARTITION APRÈS NETTOYAGE")
print("-" * 40)
for cat, count in final_category_stats.items():
    print(f"{cat:30} {count:5} tweets ({count*100/len(df_final):5.1f}%)")

# %% [markdown]
# ## 10. Analyse temporelle des tweets (features seulement, sans graphiques)

# %%
df_final['created_at'] = pd.to_datetime(df_final['created_at'], utc=True)
df_final['year'] = df_final['created_at'].dt.year
df_final['month'] = df_final['created_at'].dt.month
df_final['hour'] = df_final['created_at'].dt.hour
df_final['day_of_week'] = df_final['created_at'].dt.dayofweek

yearly_stats = df_final.groupby('year').size()
monthly_stats = df_final.groupby('month').size()
hourly_stats = df_final.groupby('hour').size()
daily_stats = df_final.groupby('day_of_week').size()

print("\n📅 TWEETS PAR ANNÉE")
print(yearly_stats)

print("\n📅 TWEETS PAR MOIS")
print(monthly_stats)

print("\n⏰ TWEETS PAR HEURE")
print(hourly_stats)

print("\n📆 TWEETS PAR JOUR DE LA SEMAINE (0 = Lundi)")
print(daily_stats)

# %% [markdown]
# ## 11. Recommandations et règles de filtrage

# %%
filtrage_rules = [
    {
        "Priorité": "🔴 CRITIQUE",
        "Filtre": "Messages automatiques Freebox",
        "Regex": r"messagerie privée X n'est plus disponible|retrouvez-moi.*Messenger",
        "Impact": "~50% du volume",
        "Code": "df[~df['full_text'].str.contains('messagerie privée X', case=False, na=False)]"
    },
    {
        "Priorité": "🟠 HAUTE",
        "Filtre": "Retweets",
        "Regex": r"^RT @",
        "Impact": "Contenus non originaux",
        "Code": "df[~df['full_text'].str.startswith('RT @', na=False)]"
    },
    {
        "Priorité": "🟡 MOYENNE",
        "Filtre": "Messages trop courts",
        "Condition": "len(text) < 30",
        "Impact": "Messages non substantiels",
        "Code": "df[df['full_text'].str.len() >= 30]"
    },
    {
        "Priorité": "🟢 BASSE",
        "Filtre": "Spam/Promotion",
        "Liste noire": ["💩", "@fingapp", "@outagedetect"],
        "Impact": "Amélioration qualité",
        "Code": "df[~df['full_text'].str.contains('💩|@fingapp|@outagedetect', na=False)]"
    }
]

print("🛠️ RÈGLES DE FILTRAGE RECOMMANDÉES")
print("=" * 80)
print()

for rule in filtrage_rules:
    print(f"{rule['Priorité']} {rule['Filtre']}")
    print(f"   Impact attendu: Suppression de {rule['Impact']}")
    if 'Regex' in rule:
        print(f"   Pattern regex: {rule['Regex']}")
    elif 'Condition' in rule:
        print(f"   Condition: {rule['Condition']}")
    elif 'Liste noire' in rule:
        print(f"   Mots-clés à filtrer: {', '.join(rule['Liste noire'])}")
    print(f"   Code Python: {rule['Code']}")
    print()

print("\n" + "=" * 80)
print("📝 FONCTION DE FILTRAGE COMPLÈTE")
print("=" * 80)
print()
print("""def clean_tweet_dataset(df):
    \\"\\"
    Nettoie le dataset de tweets en supprimant les tweets non pertinents.
    \\"\\"
    # Copie du DataFrame
    df_clean = df.copy()
    
    # Filtre 1: Supprimer les messages automatiques
    df_clean = df_clean[~df_clean['full_text'].str.contains(
        'messagerie privée X n\\'est plus disponible', case=False, na=False)]
    
    # Filtre 2: Supprimer les retweets
    df_clean = df_clean[~df_clean['full_text'].str.startswith('RT @', na=False)]
    
    # Filtre 3: Supprimer les messages trop courts
    df_clean = df_clean[df_clean['full_text'].str.len() >= 30]
    
    # Filtre 4: Supprimer le spam
    spam_patterns = '💩|@fingapp|@outagedetect|via @fingapp'
    df_clean = df_clean[~df_clean['full_text'].str.contains(spam_patterns, na=False)]
    
    return df_clean
""")

# %% [markdown]
# ## 12. Métriques de performance (sans graphiques)

# %%
metrics = {
    'Volume initial': len(df),
    'Volume après nettoyage': len(df_final),
    'Tweets supprimés': len(df) - len(df_final),
    'Taux de réduction': f"{(1 - len(df_final)/len(df))*100:.1f}%",
    'Temps de traitement économisé': f"{(len(df) - len(df_final))*0.5:.0f} minutes",  # Estimation: 30s par tweet
    'Efficacité du filtrage': f"{len(df_problematic)/len(df)*100:.1f}%"
}

print("📈 MÉTRIQUES DE PERFORMANCE")
print("=" * 60)
for key, value in metrics.items():
    print(f"{key:30} {value}")

# %% [markdown]
# ## 13. Export des résultats

# %%
output_dir = 'LLM-classified-data'

os.makedirs(output_dir, exist_ok=True)

# 1. Dataset nettoyé
clean_path = os.path.join(output_dir, 'tweets_free_cleaned.csv')
df_final.to_csv(clean_path, index=False)
print(f"✅ Dataset nettoyé sauvegardé: {clean_path}")

# 2. Liste des tweets problématiques
prob_path = os.path.join(output_dir, 'tweets_problematiques.csv')
df_problematic.to_csv(prob_path, index=False)
print(f"✅ Tweets problématiques sauvegardés: {prob_path}")

# 3. Statistiques générales
stats_path = os.path.join(output_dir, 'statistiques_analyse.txt')
with open(stats_path, 'w', encoding='utf-8') as f:
    f.write("STATISTIQUES D'ANALYSE DES TWEETS FREE\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Date d'analyse: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
    f.write(f"Volume initial: {len(df):,} tweets\n")
    f.write(f"Volume après nettoyage: {len(df_final):,} tweets\n")
    f.write(f"Taux de réduction: {(1 - len(df_final)/len(df))*100:.1f}%\n\n")
    
    f.write("Répartition des catégories (après nettoyage):\n")
    for cat, count in df_final['categorie'].value_counts().items():
        f.write(f"  - {cat}: {count} ({count*100/len(df_final):.1f}%)\n")

print(f"✅ Statistiques sauvegardées: {stats_path}")

print("\n" + "=" * 60)
print("🎉 ANALYSE TERMINÉE AVEC SUCCÈS !")
print("=" * 60)
print(f"\n📊 Résumé final:")
print(f"  • {len(df):,} tweets analysés")
print(f"  • {len(df_problematic):,} tweets problématiques identifiés ({len(df_problematic)*100/len(df):.1f}%)")
print(f"  • {len(df_final):,} tweets pertinents conservés ({len(df_final)*100/len(df):.1f}%)")
print(f"\n💡 Recommandation principale:")
print(f"  Implémenter le filtrage automatique des messages Freebox")
print(f"  pour réduire instantanément le volume de 50%")
