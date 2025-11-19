from __future__ import annotations
from typing import List, Dict, Any, Optional
import os, json, time, random, re, threading, unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from mistralai import Mistral

# =============================
#  LECTURE PROMPT + FEW-SHOTS
# =============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_DIR = os.path.join(BASE_DIR, "Prompt")

def load_system_prompt() -> Dict[str, str]:
    path = os.path.join(PROMPT_DIR, "prompt_system.txt")
    with open(path, "r", encoding="utf-8") as f:
        return {"role": "system", "content": f.read().strip()}

def load_few_shots() -> List[Dict[str, str]]:
    path = os.path.join(PROMPT_DIR, "few_shots.txt")
    few_shots = []

    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()


    u, a = None, None
    for line in lines:
        line = line.strip()
        if line.startswith("U:"):
            u = line[2:].strip()
        elif line.startswith("A:"):
            a = line[2:].strip()
        elif line == "":
            if u and a:
                few_shots.append({"u": u, "a": a})
            u, a = None, None

    if u and a:
        few_shots.append({"u": u, "a": a})

    return few_shots


SYSTEM_ONE = load_system_prompt()
FEW_SHOTS = load_few_shots()
TASK_ONE = "Tweet: "
BRACES = re.compile(r"\{.*\}", re.DOTALL)

# =============================
#   CONFIG
# =============================

MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "4"))

# =============================
#   CLIENT MISTRAL
# =============================

_tls = threading.local()
def get_client() -> Mistral:
    cli = getattr(_tls, "client", None)
    if cli is None:
        api_key = os.getenv("API_KEY") or os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise RuntimeError("API_KEY manquant")
        _tls.client = Mistral(api_key=api_key)
        cli = _tls.client
    return cli

# =============================
#   NORMALISATIONS (inchangées)
# =============================

def _norm(s: str) -> str:
    s = (s or "").strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()

def _norm_sentiment(x: Any) -> Optional[str]:
    s = _norm(str(x))
    if s.startswith("pos"): return "positif"
    if s.startswith("neu"): return "neutre"
    if s.startswith("neg"): return "negatif"
    return "neutre"

def _norm_urgence(x: Any) -> int:
    try: return max(0, min(3, int(x)))
    except: return 0

def _norm_theme(x: Any, tweet: str) -> str:
    t = _norm(str(x))
    if "panne" in t: return "Panne Internet"
    if "fact" in t or "prelev" in t: return "Facturation"
    if "debit" in t or "lent" in t or "instable" in t: return "Débit Internet"
    if "espace" in t or "compte" in t: return "Espace Client"
    if "fibre" in t: return "Fibre"
    if "resil" in t: return "Résiliation"
    if "merci" in t: return "Remerciement"
    return "Autre"

def _valid(rec: Dict[str, Any]) -> bool:
    return rec["sentiment"] in {"positif","neutre","negatif"} and rec["thème"] in {
        "Panne Internet","Facturation","Débit Internet","Espace Client",
        "Fibre","Résiliation","Remerciement","Autre"
    }

# =============================
#   BUILD LLM MESSAGES
# =============================

def _build_messages(tweet: str) -> List[Dict[str, str]]:
    messages = [SYSTEM_ONE]

    for ex in FEW_SHOTS:
        messages.append({"role": "user", "content": TASK_ONE + ex["u"]})
        messages.append({"role": "assistant", "content": ex["a"]})

    messages.append({"role": "user", "content": TASK_ONE + tweet})
    return messages

# =============================
#   PARSE + ANALYZE
# =============================

def _parse_json_object(txt: str) -> Dict[str, Any]:
    m = BRACES.search(txt)
    if m:
        txt = m.group(0)
    return json.loads(txt)

def analyze_one_tweet(tweet: str) -> Dict[str, Any]:
    messages = _build_messages(tweet)

    for attempt in range(MAX_RETRIES):
        try:
            res = get_client().chat.complete(
                model=MODEL,
                messages=messages,
                temperature=0.0,
                max_tokens=200,
                stream=False,
            )
            raw = (res.choices[0].message.content or "").strip()
            obj = _parse_json_object(raw)

            rec = {
                "tweet": tweet,
                "sentiment": _norm_sentiment(obj.get("sentiment")),
                "thème": _norm_theme(obj.get("thème"), tweet),
                "urgence": _norm_urgence(obj.get("urgence")),
            }

            if not _valid(rec):
                return {"tweet": tweet, "sentiment": "neutre", "thème": "Autre", "urgence": 0}

            return rec

        except Exception:
            time.sleep(1)

    return {"tweet": tweet, "sentiment":"neutre","thème":"Autre","urgence":0}

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

def analyze_tweets(tweets: List[str]) -> List[Dict[str, Any]]:
    """
    Analyse une liste de tweets en parallèle avec un pool de threads.
    Le nombre de workers vient de la variable d'env MAX_WORKERS (par défaut 4).
    """
    n = len(tweets)
    if n == 0:
        return []

    max_workers = int(os.getenv("MAX_WORKERS", "4"))

    # on prépare une liste de résultats de la même taille
    out: List[Optional[Dict[str, Any]]] = [None] * n

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_to_index = {
            pool.submit(analyze_one_tweet, tw): i
            for i, tw in enumerate(tweets)
        }

        for fut in as_completed(future_to_index):
            i = future_to_index[fut]
            try:
                out[i] = fut.result()
            except Exception:
                # fallback si un thread plante
                out[i] = {
                    "tweet": tweets[i],
                    "sentiment": "neutre",
                    "thème": "Autre",
                    "urgence": 0,
                }

    # au cas où, on remplace les None restants par un défaut
    for i, v in enumerate(out):
        if v is None:
            out[i] = {
                "tweet": tweets[i],
                "sentiment": "neutre",
                "thème": "Autre",
                "urgence": 0,
            }

    return out  # type: ignore

