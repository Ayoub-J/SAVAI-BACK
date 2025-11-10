#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test rapide du chargement CSV et des modifications"""
import pandas as pd
import sys
import warnings

# Filtrer les FutureWarnings pour vérifier qu'ils n'apparaissent plus
warnings.filterwarnings('error', category=FutureWarning)

print("=" * 70)
print("TEST RAPIDE - Vérification des modifications")
print("=" * 70)

# Test 1: Charger le CSV
print("\n[1/5] Chargement du CSV...")
try:
    df = pd.read_csv("data/free_tweet_export.csv")
    print(f"✓ CSV chargé: {len(df)} lignes, {len(df.columns)} colonnes")
    print(f"  Colonnes: {', '.join(df.columns[:5])}...")
except Exception as e:
    print(f"✗ Erreur: {e}")
    sys.exit(1)

# Test 2: Vérifier les colonnes requises
print("\n[2/5] Vérification colonnes requises...")
from core.config import REQUIRED_COLUMNS
missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
if missing:
    print(f"✗ Colonnes manquantes: {missing}")
    sys.exit(1)
else:
    print(f"✓ Toutes les colonnes requises sont présentes: {REQUIRED_COLUMNS}")

# Test 3: Simuler l'initialisation des colonnes comme dans preprocessing
print("\n[3/5] Initialisation colonnes avec dtypes corrects...")
try:
    # Colonnes string
    string_columns = ["sentiment", "urgency", "category", "theme", "llm_raw",
                      "suggested_reply", "reply_raw_llm"]
    for col in string_columns:
        if col not in df.columns:
            df[col] = pd.Series(dtype="object")

    # Colonnes float
    float_columns = ["sentiment_confidence", "urgency_confidence",
                     "category_confidence", "overall_confidence", "reply_confidence"]
    for col in float_columns:
        if col not in df.columns:
            df[col] = pd.Series(dtype="float64")

    print("✓ Colonnes initialisées:")
    print(f"  String: {string_columns[:3]}... (dtype=object)")
    print(f"  Float: {float_columns[:3]}... (dtype=float64)")
except Exception as e:
    print(f"✗ Erreur: {e}")
    sys.exit(1)

# Test 4: Tester l'assignation (le test critique!)
print("\n[4/5] Test assignation de valeurs (sans FutureWarning)...")
try:
    idx = df.index[0]

    # Assignations string
    df.at[idx, "sentiment"] = "negative"
    df.at[idx, "urgency"] = "haute"
    df.at[idx, "category"] = "plainte_service"
    df.at[idx, "theme"] = "débit instable et performances"
    df.at[idx, "llm_raw"] = '{"sentiment": "negative", "urgency": "haute"}'

    # Assignations float
    df.at[idx, "sentiment_confidence"] = 0.95
    df.at[idx, "urgency_confidence"] = 0.88
    df.at[idx, "overall_confidence"] = 0.90

    print("✓ Toutes les assignations réussies SANS FutureWarning!")
    print(f"  sentiment = '{df.at[idx, 'sentiment']}' (dtype: {df['sentiment'].dtype})")
    print(f"  sentiment_confidence = {df.at[idx, 'sentiment_confidence']} (dtype: {df['sentiment_confidence'].dtype})")

except FutureWarning as e:
    print(f"✗ FutureWarning détecté: {e}")
    print("  Les modifications n'ont PAS résolu le problème!")
    sys.exit(1)
except Exception as e:
    print(f"✗ Autre erreur: {e}")
    sys.exit(1)

# Test 5: Vérifier les imports des modules core
print("\n[5/5] Vérification des imports core...")
try:
    from core.config import AppConfig
    from core.preprocessing import (
        clean_text_basic,
        add_direction_and_status,
        generate_reply_for_tweet
    )
    print("✓ Tous les imports fonctionnent")
except Exception as e:
    print(f"✗ Erreur d'import: {e}")
    sys.exit(1)

# Résumé final
print("\n" + "=" * 70)
print("✓✓✓ TOUS LES TESTS RÉUSSIS ✓✓✓")
print("=" * 70)
print("\nRésumé:")
print("  ✓ CSV chargé correctement")
print("  ✓ Colonnes requises présentes")
print("  ✓ Dtypes initialisés correctement")
print("  ✓ Assignations SANS FutureWarning")
print("  ✓ Imports fonctionnels")
print("\n🚀 Le code est prêt pour Streamlit!")
print("\nPour lancer l'application:")
print("  streamlit run app.py")
