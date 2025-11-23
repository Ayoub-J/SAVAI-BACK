import io
import math
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from analyse_core import run_analysis


app = FastAPI(
    title="SAVAI Backend",
    description="Backend d'analyse des tweets SAV Free",
    version="1.0.0",
)

# Autorise les requêtes venant du frontend Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tu peux restreindre plus tard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================
#  FONCTION DE NETTOYAGE JSON
# ============================
def sanitize_for_json(obj):
    """
    Remplace automatiquement :
    - NaN
    - None
    - inf / -inf
    par des valeurs JSON valides (None).
    Fonctionne sur :
    - dict
    - list
    - float
    - structures imbriquées
    """
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj

    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]

    return obj


# ============================
#   ENDPOINT PRINCIPAL
# ============================
@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    """
    Réceptionne un CSV brut envoyé par Streamlit,
    lance TON analyseur (run_analysis),
    nettoie les NaN/inf,
    renvoie un JSON propre.
    """

    # Lire le CSV envoyé en upload
    content = await file.read()
    df_raw = pd.read_csv(io.BytesIO(content))

    # Appeler ton analyseur
    df_final, df_problematic = run_analysis(df_raw)

    # Remplacer NaN par None dans DataFrames
    df_final = df_final.where(pd.notna(df_final), None)

    if df_problematic is not None and not df_problematic.empty:
        df_problematic = df_problematic.where(pd.notna(df_problematic), None)
    else:
        df_problematic = pd.DataFrame([])

    # Préparation du résumé pour le dashboard
    summary = {
        "volume_initial": len(df_raw),
        "volume_final": len(df_final),
        "volume_problematic": len(df_problematic),
    }

    # Convertir DataFrame → listes dict (records)
    cleaned_records = df_final.to_dict(orient="records")
    problematic_records = df_problematic.to_dict(orient="records")

    # Payload complet
    payload = {
        "summary": summary,
        "cleaned": cleaned_records,
        "problematic": problematic_records,
    }

    # Nettoyage global JSON
    safe_payload = sanitize_for_json(payload)

    return safe_payload


@app.get("/")
def root():
    return {"status": "ok", "message": "Backend SAVAI en ligne"}
