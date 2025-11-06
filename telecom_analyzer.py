# telecom_analyzer.py
from __future__ import annotations
from typing import List, Dict, Any, Optional
import os, json, time, random, re, threading, unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from mistralai import Mistral  # pip install mistralai

# ====== Config par variables d'env ======
MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))       # parallélisme: 3–6 conseillé
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "4"))
BACKOFF_BASE = float(os.getenv("BACKOFF_BASE", "2.0"))
BACKOFF_JITTER = (0.0, 0.7)

# ====== Prompt court (1 tweet / appel) ======
SYSTEM_ONE = {
    "role": "system",
    "content": (
        "Tu es un analyste télécom francophone. Réponds UNIQUEMENT par un objet JSON valide, sans texte autour. "
        'Schéma: {"tweet": str, "sentiment": "positif|neutre|negatif", '
        '"thème": "Panne Internet|Facturation|Débit Internet|Espace Client|Fibre|Résiliation|Remerciement|Autre", '
        '"urgence": 0|1|2|3}. '
        'Si hors-sujet: "thème"="Autre", "urgence"=0.'
    )
}
TASK_ONE = "Tweet: "
BRACES = re.compile(r"\{.*\}", re.DOTALL)

ALLOWED_SENT = {"positif","neutre","negatif"}
ALLOWED_THEME = {
    "Panne Internet","Facturation","Débit Internet","Espace Client",
    "Fibre","Résiliation","Remerciement","Autre"
}

# ====== Client thread-local ======
_tls = threading.local()
def get_client() -> Mistral:
    cli = getattr(_tls, "client", None)
    if cli is None:
        api_key = os.getenv("API_KEY") or os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise RuntimeError("API_KEY (ou MISTRAL_API_KEY) manquant dans .env")
        _tls.client = Mistral(api_key=api_key)
        cli = _tls.client
    return cli

def _is_capacity(e: Exception) -> bool:
    s = str(e).lower()
    return ("429" in s) or ("capacity" in s) or ("service_tier_capacity_exceeded" in s)

# ====== Normalisation tolérante ======
def _norm(s: str) -> str:
    s = (s or "").strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()

def _norm_sentiment(x: Any) -> Optional[str]:
    s = _norm(str(x))
    if s.startswith("pos") or s in {"positive","positif","plus","bonne","favorable"}:
        return "positif"
    if s.startswith("neu") or s in {"neutral"}:
        return "neutre"
    if s.startswith("neg") or s in {"negative","mauvais","defavorable","pas content","pascontent"}:
        return "negatif"
    return None

def _norm_urgence(x: Any) -> int:
    if isinstance(x, (int, float)):
        u = int(x)
    else:
        xs = _norm(str(x))
        if xs.isdigit():
            u = int(xs)
        elif xs in {"eleve","urgent","critique","haute"}: u = 3
        elif xs in {"moyen","moyenne"}: u = 2
        elif xs in {"faible","bas","basse"}: u = 1
        else: u = 0
    return max(0, min(3, u))

def _norm_theme(x: Any, tweet: str) -> str:
    t = _norm(str(x))
    if any(k in t for k in ["panne","hors service","plus d internet","outage","down"]):
        return "Panne Internet"
    if any(k in t for k in ["factur","prelev","prelevement","debit","debite","paiement","payer","rembourse"]):
        return "Facturation"
    if any(k in t for k in ["debit","lent","vitesse","ping","latence","lag"]):
        return "Débit Internet"
    if any(k in t for k in ["espace client","mon compte","compte","identifiant","mdp","mot de passe","login"]):
        return "Espace Client"
    if "fibre" in t or "ftth" in t:
        return "Fibre"
    if "resili" in t or "resil" in t or "quitter" in t:
        return "Résiliation"
    if any(k in t for k in ["merci","remerci","bravo","top service"]):
        return "Remerciement"
    # fallback via tweet si libellé exotique
    tw = _norm(tweet)
    if any(k in tw for k in ["panne","plus d internet","hors service","outage","down","clignote rouge"]): return "Panne Internet"
    if any(k in tw for k in ["factur","prelev","paiement","payer","remboursement","debite"]): return "Facturation"
    if any(k in tw for k in ["debit","lent","vitesse","ping","latence","lag"]): return "Débit Internet"
    if any(k in tw for k in ["espace client","mon compte","identifiant","mdp","mot de passe","login"]): return "Espace Client"
    if "fibre" in tw or "ftth" in tw: return "Fibre"
    if "resili" in tw or "resil" in tw or "quitter" in tw: return "Résiliation"
    if any(k in tw for k in ["merci","merci!","bravo","top service"]): return "Remerciement"
    return "Autre"

def _coerce(obj: Dict[str, Any], tweet: str) -> Dict[str, Any]:
    return {
        "tweet": tweet,
        "sentiment": _norm_sentiment(obj.get("sentiment")) or "neutre",
        "thème": _norm_theme(obj.get("thème") or obj.get("theme"), tweet),
        "urgence": _norm_urgence(obj.get("urgence")),
    }

def _valid(rec: Dict[str, Any]) -> bool:
    return (
        isinstance(rec.get("tweet",""), str) and len(rec["tweet"])>0 and
        rec.get("sentiment") in ALLOWED_SENT and
        rec.get("thème") in ALLOWED_THEME and
        isinstance(rec.get("urgence"), int) and rec["urgence"] in (0,1,2,3)
    )

def _parse_json_object(txt: str) -> Dict[str, Any]:
    m = BRACES.search((txt or "").strip())
    if m: txt = m.group(0)
    obj = json.loads(txt)
    if not isinstance(obj, dict):
        raise ValueError("Réponse non-objet JSON.")
    return obj

# ====== Règles déterministes (overrides) ======
def _contains_any(hay: str, needles: list[str]) -> bool:
    h = _norm(hay)
    return any(n in h for n in needles)

def _rule_override(tweet: str) -> dict | None:
    h = _norm(tweet)

    billing_terms = [
        "factur","prelev","prelevement","preleve","prelevé","prelevee",
        "debit","debite","debité","debitee","paiement","payer","rembourse"
    ]
    dispute_terms = [
        "non restitution","resiliation","résiliation",
        "n ai pas effectue","n'ai pas effectue","pas effectue moi meme","pas effectuée", "fraude","litige"
    ]
    contact_blockers = [
        "impossible de vous joindre","impossible de joindre","impossible de les joindre",
        "identifiants n existent plus","identifiant n existe plus","compte desactive",
        "n existent plus","ne fonctionnent plus"
    ]
    escalation_terms = ["relances","mise en demeure","huissier","contentieux"]

    # Facturation en priorité
    if _contains_any(h, billing_terms) or _contains_any(h, dispute_terms):
        urgence = 2
        if _contains_any(h, contact_blockers) or _contains_any(h, escalation_terms):
            urgence = 3
        return {"tweet": tweet, "sentiment": "negatif", "thème": "Facturation", "urgence": urgence}

    # Panne / Débit / Remerciement
    if _contains_any(h, ["panne","plus d internet","hors service","outage","down","box clignote rouge"]):
        return {"tweet": tweet, "sentiment": "negatif", "thème": "Panne Internet", "urgence": 3}
    if _contains_any(h, ["debit","lent","vitesse","ping","latence","lag"]):
        return {"tweet": tweet, "sentiment": "negatif", "thème": "Débit Internet", "urgence": 2}
    if _contains_any(h, ["merci","remerci","bravo","top service"]):
        return {"tweet": tweet, "sentiment": "positif", "thème": "Remerciement", "urgence": 0}

    return None

# ====== Appel unitaire (retries + overrides) ======
def analyze_one_tweet(tweet: str) -> Dict[str, Any]:
    # Fast-path : règle avant LLM
    forced = _rule_override(tweet)
    if forced is not None:
        return forced

    messages = [SYSTEM_ONE, {"role": "user", "content": TASK_ONE + tweet}]
    for attempt in range(MAX_RETRIES):
        try:
            res = get_client().chat.complete(
                model=MODEL,
                messages=messages,
                temperature=0.0,
                max_tokens=80,
                stream=False,
            )
            raw = (res.choices[0].message.content or "").strip()
            obj = _parse_json_object(raw)
            rec = _coerce(obj, tweet)

            # Safety-net : réappliquer la règle si cas évident
            forced_after = _rule_override(tweet)
            if forced_after is not None:
                rec = forced_after

            if not _valid(rec):
                rec = {"tweet": tweet, "sentiment": "neutre", "thème": "Autre", "urgence": 0}
            return rec

        except Exception as e:
            if _is_capacity(e) and attempt < MAX_RETRIES - 1:
                backoff = BACKOFF_BASE * (2**attempt) + random.uniform(*BACKOFF_JITTER)
                time.sleep(backoff); continue
            return {"tweet": tweet, "sentiment": "neutre", "thème": "Autre", "urgence": 0}

# ====== API publique ======
def analyze_tweets(tweets: List[str]) -> List[Dict[str, Any]]:
    out: List[Optional[Dict[str, Any]]] = [None]*len(tweets)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        fut2i = {pool.submit(analyze_one_tweet, tw): i for i, tw in enumerate(tweets)}
        for fut in as_completed(fut2i):
            i = fut2i[fut]
            try:
                out[i] = fut.result()
            except Exception:
                out[i] = {"tweet": tweets[i], "sentiment":"neutre","thème":"Autre","urgence":0}
    return out  # type: ignore
