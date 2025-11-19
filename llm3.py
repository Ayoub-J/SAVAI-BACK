from mistralai import Mistral
import pandas as pd
from dotenv import load_dotenv
import os, json, re, time, random, sys, threading
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===== Logs =====
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

# ===== Config =====
load_dotenv()
API_KEY = os.getenv("API_KEY")
INPUT_PATH = "tweets_cleaned_enriched.csv"
TEXT_COL = "clean_text"
OUTPUT_PATH = "tweets_analyzed.csv"

MODEL_MAIN   = "mistral-tiny-latest"   # qualité
MODEL_REPAIR = "mistral-tiny-latest"   # tu peux mettre "mistral-tiny-latest" si la réparation est bonne

N_ROWS = 20
BATCH_SIZE = 8            
MAX_WORKERS = 3
MAX_RETRIES = 4
BACKOFF_BASE_SEC = 2.0
BACKOFF_JITTER_SEC = (0.0, 0.7)

ALLOWED_SENT = {"positif","neutre","negatif"}
ALLOWED_THEME = {"Panne Internet","Facturation","Débit Internet","Espace Client","Fibre","Résiliation","Remerciement","Autre"}
BRACKETS = re.compile(r"\[.*\]", re.DOTALL)
BRACES   = re.compile(r"\{.*\}", re.DOTALL)

# ===== Prompts =====
SYSTEM_BATCH = {
    "role": "system",
    "content": (
        "Tu es un analyste télécom. Réponds STRICTEMENT par UN SEUL tableau JSON (et rien d'autre). "
        "Chaque élément doit être: "
        '{"id": int, "tweet": str, "sentiment": "positif|neutre|negatif", '
        '"thème": "Panne Internet|Facturation|Débit Internet|Espace Client|Fibre|Résiliation|Remerciement|Autre", '
        '"urgence": 0|1|2|3}. '
        'Si hors-sujet: "thème"="Autre", "urgence"=0. Ne change jamais "id".'
    )
}
TASK_BATCH = (
    "Analyse les tweets suivants (liste d'objets) et renvoie UNIQUEMENT un tableau JSON valide avec le même ordre. "
    "Conserve chaque 'id'.\nTweets:\n"
)

SYSTEM_ONE = {
    "role": "system",
    "content": (
        "Réponds UNIQUEMENT par un objet JSON (sans texte autour) selon le schéma exact: "
        '{"tweet": str, "sentiment": "positif|neutre|negatif", '
        '"thème": "Panne Internet|Facturation|Débit Internet|Espace Client|Fibre|Résiliation|Remerciement|Autre", '
        '"urgence": 0|1|2|3}. '
        'Si hors-sujet: "thème"="Autre", "urgence"=0.'
    )
}
TASK_ONE = "Tweet: "

# ===== Thread-local clients =====
import threading
_tls = threading.local()
def get_client(model_kind: str) -> Mistral:
    key = f"client_{model_kind}"
    cli = getattr(_tls, key, None)
    if cli is None:
        _tls.__dict__[key] = Mistral(api_key=API_KEY)
        cli = _tls.__dict__[key]
    return cli

def is_capacity_error(e: Exception) -> bool:
    s = str(e).lower()
    return ("429" in s) or ("capacity" in s) or ("service_tier_capacity_exceeded" in s)

def call_api(model: str, messages: List[Dict[str,str]], max_tokens: int) -> str:
    for attempt in range(MAX_RETRIES):
        try:
            t0 = time.time()
            res = get_client(model).chat.complete(
                model=model,
                messages=messages,
                temperature=0.0,
                max_tokens=max_tokens,
                stream=False,
            )
            dt = time.time() - t0
            # print(f"⏱️ API {model}: {dt:.2f}s", flush=True)  # décommente pour profiler
            return (res.choices[0].message.content or "").strip()
        except Exception as e:
            if is_capacity_error(e) and attempt < MAX_RETRIES - 1:
                backoff = BACKOFF_BASE_SEC * (2 ** attempt) + random.uniform(*BACKOFF_JITTER_SEC)
                print(f"⏳ 429/capacity. Retry dans {backoff:.1f}s…", flush=True)
                time.sleep(backoff)
                continue
            raise

# ===== Validation & parsing =====
def valid_record(rec: Dict[str,Any]) -> bool:
    try:
        return (
            isinstance(rec.get("tweet",""), str) and len(rec["tweet"]) > 0 and
            rec.get("sentiment") in ALLOWED_SENT and
            rec.get("thème") in ALLOWED_THEME and
            isinstance(rec.get("urgence"), int) and rec["urgence"] in (0,1,2,3)
        )
    except Exception:
        return False

def parse_json_array(txt: str) -> List[Dict[str,Any]]:
    m = BRACKETS.search(txt)
    if m:
        txt = m.group(0)
    arr = json.loads(txt)
    if not isinstance(arr, list):
        raise ValueError("Réponse non-liste JSON.")
    return arr

def parse_json_object(txt: str) -> Dict[str,Any]:
    m = BRACES.search(txt)
    if m:
        txt = m.group(0)
    obj = json.loads(txt)
    if not isinstance(obj, dict):
        raise ValueError("Réponse non-objet JSON.")
    return obj

# ===== Calls =====
def call_batch(items: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
    messages = [SYSTEM_BATCH, {"role":"user","content": TASK_BATCH + json.dumps(items, ensure_ascii=False)}]
    txt = call_api(MODEL_MAIN, messages, max_tokens=160 + 40*len(items))
    try:
        return parse_json_array(txt)
    except Exception as e:
        # tout le batch en erreur → sera réparé individuellement
        return [{"id": it["id"], "tweet": it["tweet"], "sentiment": "erreur", "thème": "Autre", "urgence": 0, "_err":"batch-parse"} for it in items]

def repair_one(tweet: str) -> Dict[str,Any]:
    messages = [SYSTEM_ONE, {"role":"user","content": TASK_ONE + tweet}]
    txt = call_api(MODEL_REPAIR, messages, max_tokens=60)
    try:
        obj = parse_json_object(txt)
    except Exception:
        return {"tweet": tweet, "sentiment":"neutre", "thème":"Autre", "urgence":0, "_err":"parse"}
    # clamp / normalise
    rec = {
        "tweet": tweet,
        "sentiment": obj.get("sentiment") if obj.get("sentiment") in ALLOWED_SENT else "neutre",
        "thème": obj.get("thème") if obj.get("thème") in ALLOWED_THEME else "Autre",
        "urgence": obj.get("urgence") if isinstance(obj.get("urgence"), int) and obj.get("urgence") in (0,1,2,3) else 0,
    }
    return rec

# ===== Utils =====
def gen_batches(items, size):
    for i in range(0, len(items), size):
        yield items[i:i+size]

# ===== Main =====
def main():
    if not API_KEY or API_KEY == "API_KEY":
        raise RuntimeError("⚠️ Renseigne ta clé API.")

    df = pd.read_csv(INPUT_PATH)
    if TEXT_COL not in df.columns:
        raise ValueError(f"Colonne '{TEXT_COL}' manquante.")
    if isinstance(N_ROWS, int) and N_ROWS > 0:
        df = df.head(N_ROWS).copy()

    items = [{"id": int(i), "tweet": str(t)} for i, t in zip(df.index, df[TEXT_COL].astype(str))]
    batches = list(gen_batches(items, BATCH_SIZE))
    total = len(items)
    print(f"Total: {total} | Batches: {len(batches)} | Parallélisme: {MAX_WORKERS}", flush=True)

    out: Dict[int, Dict[str,Any]] = {}
    repairs: List[Dict[str,Any]] = []

    # 1) Passe principale en batch
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        fut2b = {pool.submit(call_batch, b): b for b in batches}
        done = 0
        for fut in as_completed(fut2b):
            b = fut2b[fut]
            try:
                arr = fut.result()
            except Exception:
                arr = [{"id": it["id"], "tweet": it["tweet"], "sentiment":"erreur","thème":"Autre","urgence":0,"_err":"exception"} for it in b]

            # map par id + validation
            for it, rec in zip(b, arr):
                # si le modèle ne renvoie pas le tweet, on le force
                rec_tweet = rec.get("tweet", it["tweet"])
                # tentative de normalisation
                candidate = {
                    "tweet": rec_tweet,
                    "sentiment": rec.get("sentiment","neutre"),
                    "thème": rec.get("thème","Autre"),
                    "urgence": rec.get("urgence",0),
                }
                if not valid_record(candidate):
                    # marquer pour repasse
                    repairs.append({"id": it["id"], "tweet": it["tweet"]})
                else:
                    out[it["id"]] = candidate

            done += len(b)
            print(f"✅ Batch ok: {done}/{total}", flush=True)

    # 2) Repasse ciblée (unitaire) sur les KO
    if repairs:
        print(f"🔧 Réparations unitaires: {len(repairs)}", flush=True)
        def fix_one(job):
            rec = repair_one(job["tweet"])
            return job["id"], rec

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futs = [pool.submit(fix_one, j) for j in repairs]
            fixed = 0
            for fut in as_completed(futs):
                idx, rec = fut.result()
                # si encore invalide, on force les defaults corrects
                if not valid_record(rec):
                    rec = {"tweet": rec.get("tweet",""), "sentiment":"neutre","thème":"Autre","urgence":0}
                out[idx] = rec
                fixed += 1
                if fixed % 20 == 0:
                    print(f"…réparés: {fixed}/{len(repairs)}", flush=True)

    # 3) Sortie ordonnée
    ordered = [out.get(int(i), {"tweet": str(t), "sentiment":"neutre","thème":"Autre","urgence":0})
               for i, t in zip(df.index, df[TEXT_COL].astype(str))]
    pd.DataFrame(ordered, columns=["tweet","sentiment","thème","urgence"]).to_csv(
        OUTPUT_PATH, index=False, encoding="utf-8-sig"
    )
    print(f"\n✅ Terminé -> {OUTPUT_PATH}", flush=True)

if __name__ == "__main__":
    main()
