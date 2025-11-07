from mistralai import Mistral
import pandas as pd
from dotenv import load_dotenv
import json, os, re, time, random

# === Configuration ===
load_dotenv()
api_key = os.getenv("API_KEY") 
input_path = "tweets_cleaned_enriched.csv"  
output_path = "tweets_analyzed.csv"         

# === Lecture du CSV ===
df = pd.read_csv(input_path)

# --- Limiter à 5 tweets pour test rapide ---
df = df.head(5)

if "clean_text" not in df.columns:
    raise ValueError("La colonne 'clean_text' est manquante dans le CSV !")

# === Prompt global ===
prompt = """Tu es un analyste télécom francophone.
Tu reçois des tweets concernant l'opérateur Free (mobile, box, réseau, facturation, etc.).
Pour chaque tweet, produis une analyse objective, concise, et un thème métier.
Les définitions :
sentiment ∈ {positif, neutre, negatif}
confiance ∈ [0,1]
theme : classifie le tweet dans l'une des catégories suivantes : Panne Internet, Facturation, Débit Internet, Espace Client, Fibre, Résiliation, Remerciement
urgence ∈ {0,1,2,3} (0 = aucune urgence, 1 = à surveiller, 2 = intervention souhaitable, 3 = intervention immédiate)
Règles :
Ne reformule pas le tweet, ne commente pas : la réponse doit toujours être au format JSON suivant :
{
"tweet" : tweet,
"sentiment" : sentiment,
"thème" : thème,
"urgence" : urgence
}
Si le tweet est hors-sujet, mets theme="Autre" et urgence=0.
"""

# === Initialisation du modèle ===
with Mistral(api_key=api_key) as mistral:
    analyses = []

    for i, tweet in enumerate(df["clean_text"].astype(str).tolist()):
        try:
            res = mistral.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {"role": "user", "content": prompt + "\nLe tweet est : " + tweet}
                ],
                stream=False
            )

            content = res.choices[0].message.content.strip()

            # Tentative de parsing JSON
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                parsed = {"tweet": tweet, "sentiment": "neutre", "thème": "Autre", "urgence": 0}

            analyses.append(parsed)

            print(f"✅ {i+1}/{len(df)} traité : {parsed}")

        except Exception as e:
            print(f"⚠️ Erreur sur le tweet {i+1}: {e}")
            analyses.append({"tweet": tweet, "sentiment": "erreur", "thème": "erreur", "urgence": 0})

# === Sauvegarde du résultat ===
result_df = pd.DataFrame(analyses)
result_df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"\n✅ Analyse terminée. Résultat sauvegardé dans : {output_path}")
