# 🐦 Twitter SAV - Plateforme d'Analyse IA

> Application Streamlit moderne pour l'analyse et la gestion du service client Twitter avec IA (Mistral)

[![Version](https://img.shields.io/badge/version-2.0-blue.svg)](CHANGELOG_V2.md)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![Mistral AI](https://img.shields.io/badge/AI-Mistral-purple.svg)](https://mistral.ai)

---

## ✨ Nouveautés v2.0

🎨 **Interface Refondée** - Style React SPA moderne
🔄 **Navigation par Rôles** - Agent / Manager / Direction
📱 **Cards Twitter-Style** - Vue moderne des tweets
💬 **Vue Conversation** - Page dédiée pour chaque tweet
⚙️ **Settings** - Configuration centralisée
🎯 **KPIs Améliorés** - Métriques stratégiques enrichies

[➡️ Voir toutes les nouveautés](NOUVELLE_INTERFACE.md)

---

## 🚀 Démarrage Rapide

```bash
# 1. Installer les dépendances
pip install -r requirement.txt

# 2. Configurer la clé API Mistral (.env)
echo "MISTRAL_API_KEY=votre_clé_ici" > .env

# 3. Lancer l'application
streamlit run app.py
```

**C'est tout !** L'application s'ouvre à `http://localhost:8501`

[📖 Guide détaillé](GUIDE_DEMARRAGE.md)

---

## 🎯 Fonctionnalités Principales

### Pour les Agents SAV
- ✅ Dashboard avec liste tweets style Twitter
- ✅ Filtres multi-critères (urgence, sentiment, catégorie)
- ✅ Génération réponses IA à la demande
- ✅ Workflow complet (assigner, traiter, répondre)
- ✅ Badges visuels colorés

### Pour les Managers
- ✅ 6 graphiques analytics
- ✅ Distribution catégories & sentiments
- ✅ Performance par agent
- ✅ Assignment en masse de tickets
- ✅ Tendances temps de réponse

### Pour la Direction
- ✅ KPIs stratégiques
- ✅ Taux de satisfaction client
- ✅ Volume & traitement (trends)
- ✅ Temps moyen de traitement
- ✅ Synthèse par catégorie

---

## 📊 Aperçu Interface

### Header Navigation
```
🐦 Twitter SAV - Free
┌──────────────────────────────────────┐
│ [👤 Agent SAV] [📊 Manager] [🎯 Direction] │
└──────────────────────────────────────┘
```

### Dashboard Agent SAV
```
📊 Mes Métriques
┌─────────┬─────────┬─────────┐
│ 🟡 En attente    42         │
│ 🔵 Assignés       8         │
│ 🟢 Traités       15         │
└─────────┴─────────┴─────────┘

🔍 Filtres: [Status] [Urgence] [Sentiment] [Catégorie]

📋 File d'Attente
┌────────────────────────────────┐
│ Tweet Card                     │
│ 📅 15 jan 2024 · [🟡 En attente] │
│ @client · Ma connexion...      │
│ [🟠 Haute] [😞 Négatif]         │
│ [👁️ Ouvrir] [👤 M'assigner]     │
└────────────────────────────────┘
```

---

## 🗂️ Structure Projet

```
poc/
├── app.py                      # Point d'entrée & router
├── core/                       # Logique métier
│   ├── config.py              # Configuration (prompts, catégories)
│   ├── preprocessing.py       # Pipeline analyse LLM
│   ├── llm_client.py          # Client Mistral AI
│   └── rag.py                 # RAG simple
├── ui/                         # Interface utilisateur
│   ├── components.py          # Composants réutilisables
│   ├── agent_sav.py           # Dashboard Agent
│   ├── conversation.py        # Vue détail tweet
│   ├── manager.py             # Dashboard Manager
│   ├── direction.py           # Dashboard Direction
│   ├── settings.py            # Paramètres
│   └── backoffice.py          # Configuration système
├── data/
│   └── free_tweet_export.csv  # Dataset exemple
├── .env                        # Clé API Mistral
├── requirement.txt             # Dépendances Python
├── README.md                   # Ce fichier
├── GUIDE_DEMARRAGE.md         # Guide utilisateur
├── NOUVELLE_INTERFACE.md      # Documentation complète v2
└── CHANGELOG_V2.md            # Liste changements
```

---

## 🔑 Prérequis

- **Python** 3.10+
- **Clé API Mistral AI** ([Obtenir ici](https://console.mistral.ai))
- **Dépendances** : voir `requirement.txt`

```txt
streamlit
pandas
numpy
mistralai
python-dotenv
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Ce fichier (vue d'ensemble) |
| [GUIDE_DEMARRAGE.md](GUIDE_DEMARRAGE.md) | Guide utilisateur complet |
| [NOUVELLE_INTERFACE.md](NOUVELLE_INTERFACE.md) | Documentation interface v2 |
| [CHANGELOG_V2.md](CHANGELOG_V2.md) | Liste complète des changements |
| [MODIFICATIONS_SUMMARY.md](MODIFICATIONS_SUMMARY.md) | Corrections techniques v1.1 |
| [BEFORE_AFTER.md](BEFORE_AFTER.md) | Comparaison v1 vs v2 |

---

## 🎓 Utilisation

### 1. Configuration Initiale

```bash
# Créer le fichier .env
cat > .env << EOF
MISTRAL_API_KEY=votre_clé_mistral_ici
EOF
```

### 2. Premier Lancement

1. Lancer : `streamlit run app.py`
2. Cliquer **"🚀 Ouvrir le Backoffice"**
3. **"Charger le CSV par défaut"**
4. Définir nombre de tweets (10 pour test)
5. **"🚀 Lancer l'analyse"**
6. Attendre 1-2 minutes
7. **"← Retour au Dashboard"**

### 3. Traiter un Tweet

1. Dashboard Agent → voir liste tweets
2. Cliquer **"👁️ Ouvrir"** sur un tweet
3. Cliquer **"🤖 Générer réponse IA"**
4. Éditer la réponse
5. **"✅ Marquer comme traité"**

### 4. Voir Analytics

1. Header : cliquer **"📊 Manager"**
2. Explorer les graphiques
3. Changer période si besoin

### 5. KPIs Direction

1. Header : cliquer **"🎯 Direction"**
2. Voir satisfaction client
3. Analyser temps de traitement

---

## 🤖 Technologies

| Techno | Usage | Version |
|--------|-------|---------|
| **Streamlit** | Framework web Python | 1.28+ |
| **Mistral AI** | LLM (classification + génération) | Latest |
| **Pandas** | Manipulation données | 2.0+ |
| **Python** | Langage principal | 3.10+ |

---

## 🎨 Architecture

### Pattern Architectural
- **Presentation Layer** : `ui/` (Streamlit components)
- **Business Logic** : `core/` (LLM, preprocessing, RAG)
- **Configuration** : `core/config.py`
- **Data Layer** : Session state (Pandas DataFrames)

### Routing SPA-style
```python
Current View × Current Role → Component à afficher
────────────────────────────────────────────────────
dashboard     × agent        → render_agent_sav()
dashboard     × manager      → render_manager()
conversation  × agent        → render_conversation()
settings      × *            → render_settings()
backoffice    × *            → render_backoffice()
```

---

## 📊 Métriques Projet

- **~1100 lignes** de code Python (core)
- **~1200 lignes** d'interface (ui)
- **~1200 lignes** de documentation
- **9 modules** Python
- **6 dashboards** / vues
- **3 rôles** utilisateur

---

## 🐛 Dépannage

### L'application ne démarre pas
```bash
# Vérifier dépendances
pip install --upgrade -r requirement.txt

# Vérifier Python
python --version  # Doit être 3.10+
```

### "Aucune donnée"
→ Charger un CSV via Backoffice

### Graphiques vides
→ Analyser des tweets d'abord (Backoffice)

### Erreur API Mistral
```bash
# Vérifier clé dans .env
cat .env

# Tester la clé
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OK' if os.getenv('MISTRAL_API_KEY') else 'MISSING')"
```

[➡️ Plus d'aide dans le guide](GUIDE_DEMARRAGE.md#problèmes-courants)

---

## 🤝 Contribution

### Rapporter un Bug
1. Vérifier qu'il n'existe pas déjà
2. Fournir steps to reproduce
3. Inclure logs/screenshots

### Proposer une Feature
1. Décrire le use case
2. Expliquer le bénéfice
3. Fournir mockup si UI

---

## 📜 Licence

Ce projet est un POC (Proof of Concept) à des fins éducatives et de démonstration.

---

## 🎉 Changelog

### v2.0 - 2025-01-24
- 🎨 Refonte interface style React SPA
- 🔄 Navigation par rôles
- 📱 Dashboard cards Twitter-style
- 💬 Vue conversation dédiée
- ⚙️ Settings centralisés
- [Voir détails](CHANGELOG_V2.md)

### v1.1 - 2025-01-24
- 🐛 Correction FutureWarnings Pandas
- 🔧 Génération réponses manuelle
- [Voir détails](MODIFICATIONS_SUMMARY.md)

### v1.0 - 2024
- ✨ Version initiale
- 4 dashboards (tabs)
- Classification LLM
- Génération réponses automatique

---

## 📞 Support

- **Documentation** : Voir fichiers `.md` dans le projet
- **Questions** : Consulter le [Guide](GUIDE_DEMARRAGE.md)
- **Bugs** : Créer une issue

---

## ✨ Auteurs

- **Architecture** : Claude AI
- **Code Original** : Équipe Développement
- **v2.0 Refonte** : Claude AI + Équipe

---

## 🙏 Remerciements

- **Mistral AI** pour l'API LLM
- **Streamlit** pour le framework
- **Free** pour le use case

---

**🚀 Prêt à démarrer ?**

```bash
streamlit run app.py
```

📖 [Guide complet](GUIDE_DEMARRAGE.md) | 🎨 [Nouvelle interface](NOUVELLE_INTERFACE.md) | 📝 [Changelog](CHANGELOG_V2.md)

---

*POC Twitter SAV v2.0 - Analyse et Gestion de Service Client avec IA* 🐦✨
