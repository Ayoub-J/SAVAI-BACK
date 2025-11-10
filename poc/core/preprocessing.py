# core/preprocessing.py
from typing import Optional, Dict, Any

import numpy as np
import pandas as pd
import streamlit as st

from .config import AppConfig, FREE_ACCOUNTS, REQUIRED_COLUMNS
from .llm_client import mistral_chat, extract_json_from_text


def clean_text_basic(text: str) -> str:
    """
    Nettoyage léger pour NLP : enlève URLs, mentions, hashtags, ponctuation forte.
    """
    import re

    if not isinstance(text, str):
        return ""
    t = text

    # Supprimer les retweets "RT @..."
    t = re.sub(r"^RT @\S+:", "", t)

    # URLs
    t = re.sub(r"http\S+|www\.\S+", " ", t)

    # Mentions & hashtags
    t = re.sub(r"[@#]\S+", " ", t)

    # Ponctuation et caractères spéciaux de base
    t = re.sub(r"[^0-9A-Za-zÀ-ÖØ-öø-ÿ\s]", " ", t)

    # Espaces multiples
    t = re.sub(r"\s+", " ", t).strip()

    return t.lower()


def compute_response_times(df: pd.DataFrame) -> pd.DataFrame:
    """
    Inspiré de test.py :
    - calcule le temps entre un tweet et le tweet auquel il répond (si parent présent)
    - ajoute la colonne service_response_time_minutes (float)
    """
    df = df.copy()
    if not {"id", "in_reply_to", "created_at"}.issubset(df.columns):
        return df

    df["id"] = df["id"].astype("string")
    df["in_reply_to"] = df["in_reply_to"].astype("string")
    df["created_at_dt"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)

    all_ids = set(df["id"].dropna())
    mask_replies = df["in_reply_to"].notna() & (df["in_reply_to"] != "")
    df_replies = df[mask_replies].copy()
    df_replies["has_parent_in_dataset"] = df_replies["in_reply_to"].isin(all_ids)

    df_replies = df_replies[df_replies["has_parent_in_dataset"]].copy()

    parents = df[["id", "created_at_dt"]].rename(
        columns={"id": "parent_id", "created_at_dt": "parent_created_at_dt"}
    )
    df_replies = df_replies.merge(
        parents,
        left_on="in_reply_to",
        right_on="parent_id",
        how="left",
        validate="m:1",
    )

    df_replies["response_time"] = df_replies["created_at_dt"] - df_replies["parent_created_at_dt"]
    df_replies["response_time_seconds"] = df_replies["response_time"].dt.total_seconds()

    df_replies_valid = df_replies[
        df_replies["response_time_seconds"].notna()
        & (df_replies["response_time_seconds"] >= 0)
    ].copy()

    df["service_response_time_minutes"] = np.nan
    df.loc[df_replies_valid.index, "service_response_time_minutes"] = (
        df_replies_valid["response_time_seconds"] / 60.0
    )

    return df


def add_direction_and_status(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute :
    - direction : inbound (client) / outbound (compte Free)
    - status, assigned_to, answered_by, answered_at
    """
    df = df.copy()
    df["screen_name_lower"] = df["screen_name"].astype(str).str.lower()
    df["direction"] = np.where(
        df["screen_name_lower"].isin(FREE_ACCOUNTS),
        "outbound",
        "inbound",
    )

    if "status" not in df.columns:
        df["status"] = pd.Series("pending", index=df.index, dtype="object")  # pending / assigned / answered
    if "assigned_to" not in df.columns:
        df["assigned_to"] = pd.Series(dtype="object")
    if "answered_by" not in df.columns:
        df["answered_by"] = pd.Series(dtype="object")
    if "answered_at" not in df.columns:
        df["answered_at"] = pd.Series(dtype="datetime64[ns]")
    if "agent_final_reply" not in df.columns:
        df["agent_final_reply"] = pd.Series(dtype="object")

    return df


def classify_single_tweet(clean_text: str, cfg: AppConfig) -> Dict[str, Any]:
    """
    Appel Mistral pour classifier un tweet (sentiment, urgence, catégorie, etc.).
    Retourne un dict avec champs + confidences.
    """
    categories_str = ", ".join(cfg.categories)
    prompt = cfg.classify_prompt.format(
        tweet_text=clean_text,
        categories=categories_str,
    )

    raw = mistral_chat(prompt, model=cfg.classify_model)
    data = extract_json_from_text(raw) or {}

    res = {
        "sentiment": data.get("sentiment"),
        "sentiment_confidence": float(data.get("sentiment_confidence", 0.0) or 0.0),
        "urgency": data.get("urgency"),
        "urgency_confidence": float(data.get("urgency_confidence", 0.0) or 0.0),
        "category": data.get("category"),
        "category_confidence": float(data.get("category_confidence", 0.0) or 0.0),
        "theme": data.get("theme"),
        "overall_confidence": float(data.get("overall_confidence", 0.0) or 0.0),
        "raw_llm_output": raw,
    }
    return res


def generate_reply_for_tweet(row: pd.Series, cfg: AppConfig) -> Dict[str, Any]:
    """
    Appel Mistral pour générer une proposition de réponse.
    RAG simple: on utilise l'engine stocké en session_state si dispo,
    sinon on prend le texte brut cfg.rag_text.
    """
    from .rag import SimpleRAG

    # RAG : si un index est en mémoire, on s'en sert
    rag_engine: Optional[SimpleRAG] = st.session_state.get("rag_engine")  # type: ignore
    if rag_engine is not None:
        passages = rag_engine.query(str(row.get("clean_text") or row.get("full_text") or ""), top_k=5)
        if passages:
            rag_context = "\n\n".join(passages)
        else:
            rag_context = cfg.rag_text or "Pas de contexte technique fourni."
    else:
        rag_context = cfg.rag_text or "Pas de contexte technique fourni."

    prompt = cfg.reply_prompt.format(
        tweet_text=row.get("full_text"),
        sentiment=row.get("sentiment"),
        urgency=row.get("urgency"),
        category=row.get("category"),
        rag_context=rag_context,
    )
    raw = mistral_chat(prompt, model=cfg.reply_model)
    data = extract_json_from_text(raw) or {}

    return {
        "reply_text": data.get("reply_text", ""),
        "reply_confidence": float(data.get("reply_confidence", 0.0) or 0.0),
        "raw_reply_llm_output": raw,
    }


def preprocess_and_analyse(
    df: pd.DataFrame,
    cfg: AppConfig,
    max_inbound_tweets: Optional[int] = None,
) -> pd.DataFrame:
    """
    Pipeline complet :
    - vérification structure
    - typage colonnes, ajout created_at_dt
    - temps de réponse (test.py)
    - direction (inbound/outbound), statuts
    - nettoyages texte (clean_text)
    - classification LLM sur inbound
    - génération de réponses LLM pour inbound à faible confiance
    """
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        st.error(f"Colonnes manquantes dans le CSV : {missing}")
        return df

    df = df.copy()

    # Typage
    df["id"] = df["id"].astype("string")
    df["in_reply_to"] = df["in_reply_to"].astype("string")
    df["created_at"] = df["created_at"].astype("string")
    df["created_at_dt"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)

    # Temps de réponse basé sur test.py
    df = compute_response_times(df)

    # Direction & statuts
    df = add_direction_and_status(df)

    # Texte nettoyé
    df["clean_text"] = df["full_text"].astype(str).apply(clean_text_basic)

    # On se concentre sur les inbound pour classification
    inbound_mask = df["direction"] == "inbound"
    df_inbound = df[inbound_mask].copy()

    if max_inbound_tweets is not None:
        df_inbound = df_inbound.head(max_inbound_tweets)

    # Colonnes LLM à créer avec les dtypes appropriés pour éviter les FutureWarnings
    # Colonnes string (object)
    string_columns = ["sentiment", "urgency", "category", "theme", "llm_raw", "suggested_reply", "reply_raw_llm"]
    for col in string_columns:
        if col not in df.columns:
            df[col] = pd.Series(dtype="object")
        else:
            df[col] = df[col].astype("object")

    # Colonnes numériques (float64)
    float_columns = [
        "sentiment_confidence", "urgency_confidence", "category_confidence",
        "overall_confidence", "reply_confidence"
    ]
    for col in float_columns:
        if col not in df.columns:
            df[col] = pd.Series(dtype="float64")
        else:
            df[col] = df[col].astype("float64")

    st.write(f"Analyse LLM sur {len(df_inbound)} tweets inbound...")

    progress = st.progress(0)
    total = len(df_inbound)
    for i, (idx, row) in enumerate(df_inbound.iterrows(), start=1):
        res = classify_single_tweet(row["clean_text"], cfg)

        df.at[idx, "sentiment"] = res["sentiment"]
        df.at[idx, "sentiment_confidence"] = res["sentiment_confidence"]
        df.at[idx, "urgency"] = res["urgency"]
        df.at[idx, "urgency_confidence"] = res["urgency_confidence"]
        df.at[idx, "category"] = res["category"]
        df.at[idx, "category_confidence"] = res["category_confidence"]
        df.at[idx, "theme"] = res["theme"]
        df.at[idx, "overall_confidence"] = res["overall_confidence"]
        df.at[idx, "llm_raw"] = res["raw_llm_output"]

        progress.progress(i / max(total, 1))

    progress.empty()
    st.success("Classification LLM terminée.")

    # Note : La génération de réponses est désormais manuelle via l'interface Agent SAV
    # Les agents peuvent cliquer sur "💬 Générer une proposition de réponse" pour chaque tweet
    st.info("💡 Les réponses LLM seront générées à la demande par les agents SAV.")

    return df
