from __future__ import annotations
from typing import List, Dict, Any, Optional
import os, json, time, re, unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed

import ollama  # pip install ollama

# =============== CHEMINS DES PROMPTS =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_DIR = os.path.join(BASE_DIR, "Prompt")

SYSTEM_PATH = os.path.join(PROMPT_DIR, "prompt_system.txt")
FEWSHOTS_PATH = os.path.join(PROMPT_DIR, "few_shots.txt")

BRACES = re.compile(r"\{.*\}", re.DOTALL)

MODEL = os.getenv("MISTRAL_MODEL", "mistral")
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "3"))


# =============== CHARGEMENT PROMPTS ===================

def load_system_prompt() -> Dict[str, str]:
    with open(SYSTEM_PATH, "r", encoding="utf-8") as f:
        content = f.read().strip()
    return {"role": "system", "content": content}

def load_few_shots() -> List[Dict[str, str]]:
    few_shots: List[Dict[str, str]] = []
    with open(FEWSHOTS_PATH, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    u, a = None, None
    for line in lines:
        line = line.strip()
        if not line:
            # fin bloc
            if u and a:
                few_shots.append({"u": u, "a": a})
            u, a = None, None
            continue

        if line.startswith("U:"):
            u = line[2:].strip()
        elif line.startswith("A:"):
            a = line[2:].strip()

    # dernier bloc si pas de ligne vide
    if u and a:
        few_shots.append({"u": u, "a": a})

    return few_shots


SYSTEM_ONE = load_system_prompt()
FEW_SHOTS = load_few_shots()
TASK_ONE = "Tweet: "

ALLOWED_SENT = {"positif", "neutre", "negatif"}
ALLOWED_THEME = {
    "Panne Internet", "Facturation", "Débit Internet", "Espace Client",
    "Fibre", "Résiliation", "Remerciement", "Autre"
}


# =============== NORMALISATION ========================

def _norm(s: str) -> str:
    s = (s or "").strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()

def _norm_sentiment(x: Any) -> str:
    s = _norm(str(x))
    if s.startswith("pos"):
        return "positif"
    if s.startswith("neu"):
        return "neutre"
    if s.startswith("neg"):
        return "negatif"
    return "neutre"

def _norm_urgence(x: Any) -> int:
    try:
        u = int(x)
    except Exception:
        u = 0
    return max(0, min(3, u))

def _norm_theme(x: Any, tweet: str) -> str:
    t = _norm(str(x))
    if "panne" in t or "plus d internet" in t:
        return "Panne Internet"
    if "factur" in t or "prelev" in t or "rembours" in t:
        return "Facturation"
    if any(k in t for k in ["debit", "lent", "instable", "latence", "ping"]):
        return "Débit Internet"
    if "espace client" in t or "compte" in t or "identifiant" in t:
        return "Espace Client"
    if "fibre" in t:
        return "Fibre"
    if "resili" in t or "résili" in t:
        return "Résiliation"
    if "merci" in t or "remerci" in t:
        return "Remerciement"
    return "Autre"

def _valid(rec: Dict[str, Any]) -> bool:
    return (
        isinstance(rec.get("tweet",""), str)
        and rec.get("sentiment") in ALLOWED_SENT
        and rec.get("thème") in ALLOWED_THEME
        and isinstance(rec.get("urgence"), int)
        and rec["urgence"] in (0,1,2,3)
    )


# =============== BUILD MESSAGES =======================

def _build_messages(tweet: str) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = [SYSTEM_ONE]

    for ex in FEW_SHOTS:
        messages.append({"role": "user", "content": TASK_ONE + ex["u"]})
        messages.append({"role": "assistant", "content": ex["a"]})

    messages.append({"role": "user", "content": TASK_ONE + tweet})
    return messages


# =============== LLM VIA OLLAMA =======================

def _call_ollama(messages: List[Dict[str, str]]) -> str:
    """
    Appel simple à Ollama : ollama.chat(model, messages=[...])
    """
    res = ollama.chat(model=MODEL, messages=messages)
    # structure: {"message": {"role": "...", "content": "..."}}
    return res["message"]["content"]

def _parse_json_object(txt: str) -> Dict[str, Any]:
    m = BRACES.search((txt or "").strip())
    if m:
        txt = m.group(0)
    obj = json.loads(txt)
    if not isinstance(obj, dict):
        raise ValueError("Réponse non-objet JSON.")
    return obj


# =============== ANALYSE D'UN TWEET ===================

def analyze_one_tweet(tweet: str) -> Dict[str, Any]:
    messages = _build_messages(tweet)

    try:
        raw = _call_ollama(messages).strip()
        obj = _parse_json_object(raw)
        rec = {
            "tweet": tweet,
            "sentiment": _norm_sentiment(obj.get("sentiment")),
            "thème": _norm_theme(obj.get("thème") or obj.get("theme"), tweet),
            "urgence": _norm_urgence(obj.get("urgence")),
        }
        if not _valid(rec):
            rec = {"tweet": tweet, "sentiment": "neutre", "thème": "Autre", "urgence": 0}
        return rec
    except Exception:
        # fallback en cas d'erreur LLM
        return {"tweet": tweet, "sentiment": "neutre", "thème": "Autre", "urgence": 0}


# =============== ANALYSE EN LOT =======================

def analyze_tweets(tweets: List[str]) -> List[Dict[str, Any]]:
    n = len(tweets)
    if n == 0:
        return []

    out: List[Optional[Dict[str, Any]]] = [None] * n

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        fut2i = {
            pool.submit(analyze_one_tweet, tw): i
            for i, tw in enumerate(tweets)
        }
        for fut in as_completed(fut2i):
            i = fut2i[fut]
            try:
                out[i] = fut.result()
            except Exception:
                out[i] = {
                    "tweet": tweets[i],
                    "sentiment": "neutre",
                    "thème": "Autre",
                    "urgence": 0,
                }

    # sécurité si des None restent
    for i, v in enumerate(out):
        if v is None:
            out[i] = {
                "tweet": tweets[i],
                "sentiment": "neutre",
                "thème": "Autre",
                "urgence": 0,
            }

    return out  # type: ignore
