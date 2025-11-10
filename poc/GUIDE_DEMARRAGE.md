# 🚀 Guide de Démarrage Rapide

## ✅ Prérequis

```bash
# Installer les dépendances
pip install -r requirement.txt

# Vérifier la clé API Mistral dans .env
cat .env
# Doit contenir: MISTRAL_API_KEY=votre_clé
```

## 🎯 Lancement

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à `http://localhost:8501`

---

## 🗺️ Navigation Rapide

### Header Principal
```
🐦 Twitter SAV - Free
┌────────────────────────────────────┐
│ [👤 Agent SAV] [📊 Manager] [🎯 Direction] │
└────────────────────────────────────┘
```
- Cliquez sur un rôle pour changer de vue
- Chaque rôle a son dashboard adapté

---

## 📋 Première Utilisation

### Étape 1 : Charger des Données
1. Au lancement → Dashboard Agent SAV (vide)
2. Cliquez **"🚀 Ouvrir le Backoffice"** (en bas)
3. Cliquez **"Charger le CSV par défaut"**
   - Charge automatiquement `data/free_tweet_export.csv`
4. Définir "Nombre maximum de tweets" : **10** (pour test rapide)
5. Cliquez **"🚀 Lancer l'analyse et le nettoyage"**
6. Attendez 1-2 minutes (classification par IA)
7. Message "Classification LLM terminée" ✅
8. Cliquez **"← Retour au Dashboard"**

### Étape 2 : Traiter un Tweet (Agent)
1. Vous voyez maintenant des **cards de tweets**
2. Utilisez les **filtres** si besoin (Urgence, Sentiment, etc.)
3. Cliquez **"👁️ Ouvrir"** sur un tweet
4. → Vue Conversation s'affiche
5. Cliquez **"🤖 Générer une proposition de réponse"**
6. Attendez 3-5 secondes → Réponse IA s'affiche
7. Éditez la réponse si besoin
8. Cliquez **"✅ Marquer comme traité"**
9. → Retour automatique au dashboard

### Étape 3 : Voir les Analytics (Manager)
1. En haut, cliquez **"📊 Manager"**
2. Voir métriques : Total, Traités, Assignés, En attente
3. Voir graphiques :
   - Distribution catégories
   - Distribution sentiments
   - Top mots fréquents
   - Performance agents

### Étape 4 : KPIs Direction
1. En haut, cliquez **"🎯 Direction"**
2. Voir KPIs stratégiques :
   - Taux de traitement
   - Satisfaction client
   - Temps moyen traitement
3. Voir graphiques tendances

---

## 🎨 Composants Principaux

### Dashboard Agent SAV
- **Métriques** : En attente, Assignés, Traités
- **Filtres** : Status, Urgence, Sentiment, Catégorie, Période
- **Cards tweets** : Cliquables avec badges colorés
- **Actions** : Ouvrir, M'assigner

### Vue Conversation
- **Détails complets** du tweet
- **Classification IA** : Urgence, Sentiment, Catégorie
- **Génération réponse** : Bouton manuel
- **Actions** : Assigner, Marquer traité

### Dashboard Manager
- **6 graphiques analytics**
- **Assignment en masse**
- **Performance équipe**

### Dashboard Direction
- **4 KPIs clés**
- **3 graphiques tendances**
- **Synthèse catégories**

---

## 🔧 Raccourcis Navigation

| De | Vers | Action |
|-----|------|--------|
| N'importe où | Dashboard | Cliquer rôle (header) |
| Dashboard | Conversation | Cliquer "👁️ Ouvrir" |
| Conversation | Dashboard | "← Retour" ou marquer traité |
| Dashboard | Settings | "⚙️ Paramètres" (bas) |
| Settings | Backoffice | "🚀 Ouvrir Backoffice" |
| Backoffice | Dashboard | "← Retour" |

---

## 💡 Astuces

### Pour les Agents
- Utilisez les **filtres** pour prioriser (ex: Urgence = Haute)
- Le badge **🟡 En attente** indique les tweets non traités
- Vous pouvez éditer la réponse IA avant d'envoyer

### Pour les Managers
- Changez la **période** pour voir l'évolution
- Utilisez **Assignment en masse** pour distribuer rapidement
- Le graphique "Performance agents" montre qui traite le plus

### Pour la Direction
- **Satisfaction client** : ratio positifs/(positifs+négatifs)
- **Taux traitement** : % de tweets answered
- Filtrez par période pour trends mensuels/hebdomadaires

---

## ⚠️ Points d'Attention

### Génération Réponse
- **Manuelle** (pas automatique)
- Nécessite clic sur bouton dans conversation
- Utilise RAG si configuré

### Performance
- Premier chargement : ~2-5 min pour 10 tweets
- Chaque réponse IA : 3-5 secondes
- Graphiques : calcul instantané

### Données
- Stockées en **session** (pas de persistence)
- Si vous fermez l'application, rechargez le CSV

---

## 🐛 Problèmes Courants

### "Aucune donnée"
→ Ouvrez le Backoffice et chargez un CSV

### Tweet ne s'ouvre pas
→ Vérifiez que processed_df contient des données

### Graphiques vides
→ Analysez d'abord des tweets (Backoffice)

### Badges ne s'affichent pas
→ L'analyse LLM a peut-être échoué, vérifiez la clé API

---

## 📞 Commandes Utiles

```bash
# Lancer l'application
streamlit run app.py

# Lancer avec port spécifique
streamlit run app.py --server.port 8502

# Vérifier dépendances
pip list | grep streamlit
pip list | grep pandas
pip list | grep mistralai

# Tester imports
python -c "from ui.components import render_header; print('OK')"
```

---

## 🎯 Workflow Complet Type

```
1. Lancer app
2. Backoffice → Charger CSV → Analyser (10 tweets)
3. Retour Dashboard Agent
4. Ouvrir tweet 1 → Générer réponse → Marquer traité
5. Ouvrir tweet 2 → Générer réponse → Marquer traité
6. Switch Manager → Voir analytics (2 tweets traités)
7. Switch Direction → Voir KPIs
8. Switch Agent → Voir file d'attente (8 tweets restants)
9. Filtrer par Urgence=Haute
10. Traiter tweets urgents en priorité
```

---

## ✅ Checklist Démarrage

- [ ] Dependencies installées (`pip install -r requirement.txt`)
- [ ] Clé API Mistral configurée (`.env`)
- [ ] Application lancée (`streamlit run app.py`)
- [ ] CSV chargé via Backoffice
- [ ] Analyse lancée (au moins 10 tweets)
- [ ] Au moins 1 tweet traité en mode Agent
- [ ] Analytics vus en mode Manager
- [ ] KPIs vus en mode Direction

---

**Temps estimé premier parcours** : 10-15 minutes

**Support** : Consultez [NOUVELLE_INTERFACE.md](NOUVELLE_INTERFACE.md) pour détails complets

---

🎉 **Bon démarrage !**
