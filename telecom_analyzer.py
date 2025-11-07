# telecom_analyzer.py
from __future__ import annotations
from typing import List, Dict, Any, Optional
import os, json, time, random, re, threading, unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from mistralai import Mistral  # pip install mistralai

# ====== Config par variables d'env ======
MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "4"))
BACKOFF_BASE = float(os.getenv("BACKOFF_BASE", "2.0"))
BACKOFF_JITTER = (0.0, 0.7)

# ====== Prompt complet (1 tweet / appel) ======
SYSTEM_ONE = {
    "role": "system",
    "content": (
        "Tu es un analyste télécom francophone pour des tweets adressés à l’opérateur Free/Freebox. "
        "Ta tâche : décider si le message est une réclamation et attribuer les champs demandés en suivant strictement les règles ci-dessous.\n\n"
        "Réponds UNIQUEMENT par un objet JSON valide, sans texte autour.\n"
        'Schéma de sortie : {"tweet": str, "sentiment": "positif|neutre|negatif", '
        '"thème": "Panne Internet|Facturation|Débit Internet|Espace Client|Fibre|Résiliation|Remerciement|Autre", '
        '"urgence": 0|1|2|3}.\n\n'
        "Définitions et rappels :\n"
        "- Réclamation = demande d’aide / dysfonctionnement / problème (panne, débit, facture, activation, résiliation, etc.).\n"
        "- Hors-sujet / info pure (RT, annonce, promo, news sans demande d’aide) => thème='Autre', urgence=0.\n"
        "- Sentiment ∈ {positif, neutre, negatif}.\n"
        "- Urgence ∈ {0,1,2,3} avec : 0=hors-sujet, 1=basse, 2=moyenne, 3=haute.\n\n"
        "Cartographie des cas vers 'thème' :\n"
        "- Pannes ou indisponibilités générales (coupure, “plus d’internet”, TV KO, Wi-Fi/DSL/Fibre HS) => 'Panne Internet'.\n"
        "- Débit instable/faible, latence, stream qui coupe => 'Débit Internet'.\n"
        "- Fibre (raccordement, PTO, signal, intervention) => 'Fibre'.\n"
        "- Facturation, prélèvements, remboursements => 'Facturation'.\n"
        "- Espace Client / compte / identifiants / activation / suivi commande => 'Espace Client'.\n"
        "- Résiliation (problèmes, confirmation, demande) => 'Résiliation'.\n"
        "- Remerciements ou félicitations => 'Remerciement'.\n"
        "- Sinon => 'Autre'.\n\n"
        "Règles spécifiques :\n"
        "1. Interpellation SAV explicite (@Free/@Freebox + “allo”, “répondez”, “quelqu’un ?”, “vous jouez à quoi ?”) sans détail technique "
        "=> sentiment='negatif', thème='Autre', urgence=2.\n"
        "2. Stream/live annulé ou gâché à cause de la connexion (“connexion instable”, “ça coupe”, “le stream tient pas”) "
        "=> sentiment='negatif', thème='Débit Internet', urgence=3 (live en cours) sinon 2.\n"
        "3. Si ambigu, sois conservateur : thème='Autre', sentiment='neutre', urgence=0 ou 1.\n"
        "4. Si remerciement ou félicitation => thème='Remerciement', sentiment='positif', urgence=0.\n"
        "5. TV KO due au réseau : panne => 'Panne Internet' ; saccades/latence/artefacts => 'Débit Internet'.\n"
        "6. Mention explicite de “fibre” pour un problème d’accès => 'Fibre' ; si uniquement performance, plutôt 'Débit Internet'.\n\n"
        "Barème d’urgence :\n"
        "- 3 (haute) : service critique indisponible en direct (live/stream/panne totale).\n"
        "- 2 (moyenne) : dysfonctionnement gênant, suivi SAV sans réponse.\n"
        "- 1 (basse) : question non urgente, gêne mineure.\n"
        "- 0 : hors-sujet ou info pure.\n\n"
        "Sortie exigée :\n"
        "- Tous les champs doivent être remplis.\n"
        "- Utilise exactement les valeurs 'positif', 'neutre', 'negatif'.\n"
        "- Pas de texte hors JSON.\n"
    )
}
TASK_ONE = "Tweet: "
BRACES = re.compile(r"\{.*\}", re.DOTALL)

# ====== Few-shots (nombreux exemples) ======
FEW_SHOTS: List[Dict[str, str]] = [
    # Panne totale
    {
        "u": "Plus d'internet depuis ce matin à Lyon, la box clignote rouge. Ça bouge @Free ?",
        "a": '{"tweet":"Plus d\'internet depuis ce matin à Lyon, la box clignote rouge. Ça bouge @Free ?","sentiment":"negatif","thème":"Panne Internet","urgence":3}'
    },
    # Débit lent / latence
    {
        "u": "Le débit est catastrophique le soir, 2 Mbps à peine… ingérable pour bosser.",
        "a": '{"tweet":"Le débit est catastrophique le soir, 2 Mbps à peine… ingérable pour bosser.","sentiment":"negatif","thème":"Débit Internet","urgence":2}'
    },
    # Stream / live
    {
        "u": "Mon live Twitch coupe toutes les 2 minutes, connexion instable chez @Freebox !",
        "a": '{"tweet":"Mon live Twitch coupe toutes les 2 minutes, connexion instable chez @Freebox !","sentiment":"negatif","thème":"Débit Internet","urgence":3}'
    },
    # Fibre accès
    {
        "u": "Raccordement fibre fait hier mais pas de signal au PTO, que faire ?",
        "a": '{"tweet":"Raccordement fibre fait hier mais pas de signal au PTO, que faire ?","sentiment":"negatif","thème":"Fibre","urgence":2}'
    },
    # Facturation simple
    {
        "u": "Double prélèvement ce mois-ci, merci de régulariser.",
        "a": '{"tweet":"Double prélèvement ce mois-ci, merci de régulariser.","sentiment":"negatif","thème":"Facturation","urgence":2}'
    },
    # Facturation + escalade
    {
        "u": "Toujours pas de remboursement malgré mes relances, je passe en mise en demeure.",
        "a": '{"tweet":"Toujours pas de remboursement malgré mes relances, je passe en mise en demeure.","sentiment":"negatif","thème":"Facturation","urgence":3}'
    },
    # Espace client / login
    {
        "u": "Impossible de me connecter à l’espace client, mot de passe refusé.",
        "a": '{"tweet":"Impossible de me connecter à l’espace client, mot de passe refusé.","sentiment":"negatif","thème":"Espace Client","urgence":1}'
    },
    # Activation / SIM / ligne
    {
        "u": "Carte SIM reçue mais l’activation ne se fait pas, une idée ?",
        "a": '{"tweet":"Carte SIM reçue mais l’activation ne se fait pas, une idée ?","sentiment":"neutre","thème":"Espace Client","urgence":1}'
    },
    # Suivi livraison (mappé Espace Client)
    {
        "u": "Ma Freebox devait arriver hier, toujours rien sur le suivi…",
        "a": '{"tweet":"Ma Freebox devait arriver hier, toujours rien sur le suivi…","sentiment":"neutre","thème":"Espace Client","urgence":1}'
    },
    # Résiliation
    {
        "u": "Je souhaite résilier immédiatement, comment procéder ?",
        "a": '{"tweet":"Je souhaite résilier immédiatement, comment procéder ?","sentiment":"neutre","thème":"Résiliation","urgence":1}'
    },
    # Remerciement
    {
        "u": "Merci au technicien Free passé ce matin, problème réglé rapidement !",
        "a": '{"tweet":"Merci au technicien Free passé ce matin, problème réglé rapidement !","sentiment":"positif","thème":"Remerciement","urgence":0}'
    },
    # Hors-sujet / promo
    {
        "u": "RT Super promo smartphone chez X, foncez !",
        "a": '{"tweet":"RT Super promo smartphone chez X, foncez !","sentiment":"neutre","thème":"Autre","urgence":0}'
    },
    # Interpellation SAV explicite sans détail
    {
        "u": "@Freebox allo ? quelqu’un pour répondre ?",
        "a": '{"tweet":"@Freebox allo ? quelqu’un pour répondre ?","sentiment":"negatif","thème":"Autre","urgence":2}'
    },
    # TV KO (panne)
    {
        "u": "La TV ne marche plus du tout depuis 1h, écran noir.",
        "a": '{"tweet":"La TV ne marche plus du tout depuis 1h, écran noir.","sentiment":"negatif","thème":"Panne Internet","urgence":3}'
    },
    # TV saccades (débit)
    {
        "u": "La TV pixelise et freeze sans arrêt ce soir.",
        "a": '{"tweet":"La TV pixelise et freeze sans arrêt ce soir.","sentiment":"negatif","thème":"Débit Internet","urgence":2}'
    },
    # Mobile HS (panne)
    {
        "u": "Plus de réseau mobile Free dans mon quartier depuis ce matin.",
        "a": '{"tweet":"Plus de réseau mobile Free dans mon quartier depuis ce matin.","sentiment":"negatif","thème":"Panne Internet","urgence":3}'
    },
    # Mobile lent (débit)
    {
        "u": "4G inutilisable en centre-ville, débit trop faible.",
        "a": '{"tweet":"4G inutilisable en centre-ville, débit trop faible.","sentiment":"negatif","thème":"Débit Internet","urgence":2}'
    },
    # Fibre mention + perf (débit)
    {
        "u": "Fibre Free installée mais j’ai à peine 10 Mbps, c’est normal ?",
        "a": '{"tweet":"Fibre Free installée mais j’ai à peine 10 Mbps, c’est normal ?","sentiment":"negatif","thème":"Débit Internet","urgence":2}'
    },
    # Processus SAV (rdv tardif, pas de réponse)
    {
        "u": "Rendez-vous technicien dans une semaine et plus de réponse du SAV, c’est abusé pour le télétravail.",
        "a": '{"tweet":"Rendez-vous technicien dans une semaine et plus de réponse du SAV, c’est abusé pour le télétravail.","sentiment":"negatif","thème":"Autre","urgence":2}'
    },
    # Ambigu / informatif
    {
        "u": "Des nouvelles de la maintenance prévue ce soir ?",
        "a": '{"tweet":"Des nouvelles de la maintenance prévue ce soir ?","sentiment":"neutre","thème":"Autre","urgence":1}'
    },
    # Menace de quitter (résiliation implicite)
    {
        "u": "Si ça continue je pars chez la concurrence.",
        "a": '{"tweet":"Si ça continue je pars chez la concurrence.","sentiment":"negatif","thème":"Résiliation","urgence":2}'
    },
    # Panne + localisation
    {
        "u": "Coupure totale internet à Marseille 8e, vous êtes au courant ?",
        "a": '{"tweet":"Coupure totale internet à Marseille 8e, vous êtes au courant ?","sentiment":"negatif","thème":"Panne Internet","urgence":3}'
    },
    # Question simple (basse urgence)
    {
        "u": "Comment changer l’IBAN pour mes paiements ?",
        "a": '{"tweet":"Comment changer l’IBAN pour mes paiements ?","sentiment":"neutre","thème":"Facturation","urgence":1}'
    },
    # Info pure / news
    {
        "u": "Free annonce une nouvelle box aujourd’hui.",
        "a": '{"tweet":"Free annonce une nouvelle box aujourd’hui.","sentiment":"neutre","thème":"Autre","urgence":0}'
    },
    # Politesse négative sans technique (SAV)
    {
        "u": "Service client injoignable, c’est inadmissible.",
        "a": '{"tweet":"Service client injoignable, c’est inadmissible.","sentiment":"negatif","thème":"Autre","urgence":2}'
    },
    # Activation box
    {
        "u": "Ma box reste bloquée sur étape 2, une aide ?",
        "a": '{"tweet":"Ma box reste bloquée sur étape 2, une aide ?","sentiment":"negatif","thème":"Espace Client","urgence":1}'
    },
    # --- Few-shots additionnels ciblés TV/HDR/SAV ---
    {
        "u": "Toujours des soucis sur les chaînes 103 et 104 en HDR sur ma TV Samsung.",
        "a": "{\"tweet\":\"Toujours des soucis sur les chaînes 103 et 104 en HDR sur ma TV Samsung.\",\"sentiment\":\"negatif\",\"thème\":\"Débit Internet\",\"urgence\":2}"
    },
    {
        "u": "TV Freebox écran noir sur toutes les chaînes depuis 30 min.",
        "a": "{\"tweet\":\"TV Freebox écran noir sur toutes les chaînes depuis 30 min.\",\"sentiment\":\"negatif\",\"thème\":\"Panne Internet\",\"urgence\":3}"
    },
    {
        "u": "Non mais vous répondez trois jours après… super le service après-vente.",
        "a": "{\"tweet\":\"Non mais vous répondez trois jours après… super le service après-vente.\",\"sentiment\":\"negatif\",\"thème\":\"Autre\",\"urgence\":2}"
    },
]

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
    # Panne
    if any(k in t for k in ["panne","hors service","plus d internet","outage","down"]):
        return "Panne Internet"
    # Facturation (sans le mot ambigu 'debit')
    if any(k in t for k in ["facture","factur","prelev","prelevement","preleve","prelevé","prelevee",
                            "debite","debité","debitee","paiement","payer","rembourse","remboursement","montant","€","euros"]):
        return "Facturation"
    # Débit / qualité (internet/TV)
    if any(k in t for k in ["debit","lent","vitesse","ping","latence","lag","instable","coupe","freeze","pixellise","pixelise","pixelise","saccade","desynchro","desynchronisation","hdr","4k","uhd"]):
        return "Débit Internet"
    # Espace Client / activation / suivi
    if any(k in t for k in ["espace client","mon compte","compte","identifiant","mdp","mot de passe","login","activation","activer","suivi"]):
        return "Espace Client"
    # Fibre
    if "fibre" in t or "ftth" in t or "pto" in t:
        return "Fibre"
    # Résiliation
    if "resili" in t or "résili" in t or "quitter" in t or "partir" in t or "concurrence" in t:
        return "Résiliation"
    # Remerciements
    if any(k in t for k in ["merci","remerci","bravo","top service"]):
        return "Remerciement"

    # fallback via tweet
    tw = _norm(tweet)
    if any(k in tw for k in ["panne","plus d internet","hors service","outage","down","clignote rouge","coupure totale"]):
        return "Panne Internet"
    if any(k in tw for k in ["facture","factur","prelev","paiement","payer","remboursement","debite","montant","€","euros"]):
        return "Facturation"
    # TV detection: KO vs qualité
    if any(k in tw for k in ["tv","chaine","chaîne","chaines","chaînes","canal","canaux","hdr","4k","uhd","smart tv","samsung"]):
        if any(k in tw for k in ["ecran noir","aucune image","aucun signal","plus de tv","chaine ne marche pas","chaînes ne marchent pas","canal ne marche pas","canaux ne marchent pas"]):
            return "Panne Internet"
        if any(k in tw for k in ["pixellise","pixelise","freeze","saccade","desynchro","desynchronisation","audio decalé","retard audio","coupe","instable","latence"]):
            return "Débit Internet"
    if any(k in tw for k in ["debit","lent","vitesse","ping","latence","lag","instable","coupe","freeze","pixellise","pixelise","saccade"]):
        return "Débit Internet"
    if any(k in tw for k in ["espace client","mon compte","identifiant","mdp","mot de passe","login","activation","activer","suivi"]):
        return "Espace Client"
    if "fibre" in tw or "ftth" in tw or "pto" in tw:
        return "Fibre"
    if any(k in tw for k in ["resili","résili","quitter","partir","concurrence"]):
        return "Résiliation"
    if any(k in tw for k in ["merci","merci!","bravo","top service"]):
        return "Remerciement"
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
def _contains_any(hay: str, needles: List[str]) -> bool:
    h = _norm(hay)
    return any(n in h for n in needles)

def _rule_override(tweet: str) -> dict | None:
    h = _norm(tweet)

    # --- Facturation : retirer 'debit' ambigu, garder 'debité' (banque) ---
    billing_terms = [
        "facture","factur","prelev","prelevement","preleve","prelevé","prelevee",
        "debite","debité","debitee","paiement","payer","rembourse","remboursement","montant","€","euros"
    ]
    dispute_terms = [
        "non restitution","resiliation","résiliation",
        "n ai pas effectue","n'ai pas effectue","pas effectue moi meme","pas effectuée","fraude","litige"
    ]
    contact_blockers = [
        "impossible de vous joindre","impossible de joindre","impossible de les joindre",
        "identifiants n existent plus","identifiant n existe plus","compte desactive",
        "n existent plus","ne fonctionnent plus","plus de reponse","pas de reponse","pas de réponse","aucune reponse","aucune réponse"
    ]
    escalation_terms = ["relances","mise en demeure","huissier","contentieux"]

    # Facturation prioritaire
    if _contains_any(h, billing_terms) or _contains_any(h, dispute_terms):
        urgence = 2
        if _contains_any(h, contact_blockers) or _contains_any(h, escalation_terms):
            urgence = 3
        return {"tweet": tweet, "sentiment": "negatif", "thème": "Facturation", "urgence": urgence}

    # Panne / Débit / Remerciement
    if _contains_any(h, ["panne","plus d internet","hors service","outage","down","box clignote rouge","coupure totale"]):
        return {"tweet": tweet, "sentiment": "negatif", "thème": "Panne Internet", "urgence": 3}
    if _contains_any(h, ["debit","lent","vitesse","ping","latence","lag","instable","coupe","freeze","pixelise","pixélise","saccade"]):
        return {"tweet": tweet, "sentiment": "negatif", "thème": "Débit Internet", "urgence": 2}
    if _contains_any(h, ["merci","remerci","bravo","top service"]):
        return {"tweet": tweet, "sentiment": "positif", "thème": "Remerciement", "urgence": 0}

    # TV/HDR/chaînes : KO (panne) vs qualité (débit)
    tv_terms_total = ["ecran noir","aucune image","aucun signal","plus de tv","chaine ne marche pas","chaînes ne marchent pas","canal ne marche pas","canaux ne marchent pas"]
    tv_terms_quality = ["pixellise","pixelise","freeze","saccade","desynchro","desynchronisation","hdr","4k","uhd","audio decalé","retard audio","instable","coupe"]
    if _contains_any(h, ["tv","chaine","chaîne","chaines","chaînes","canal","canaux","samsung","smart tv","freebox tv","hdr","4k","uhd"]):
        if _contains_any(h, tv_terms_total):
            return {"tweet": tweet, "sentiment": "negatif", "thème": "Panne Internet", "urgence": 2}
        if _contains_any(h, tv_terms_quality):
            return {"tweet": tweet, "sentiment": "negatif", "thème": "Débit Internet", "urgence": 2}

    # Processus SAV explicite (sans @)
    if _contains_any(h, [
        "sav","service client","service apres vente","service après vente",
        "rdv","rendez-vous","technicien","pas de reponse","plus de reponse","pas de réponse","plus de réponse",
        "injoignable","rappel","delai","délai","trois jours apres","3 jours après","trois jours après","aucune reponse","aucune réponse"
    ]):
        return {"tweet": tweet, "sentiment": "negatif", "thème": "Autre", "urgence": 2}

    return None

# ====== Construction des messages avec few-shots ======
def _build_messages(tweet: str) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = [SYSTEM_ONE]
    for ex in FEW_SHOTS:
        messages.append({"role": "user", "content": TASK_ONE + ex["u"]})
        messages.append({"role": "assistant", "content": ex["a"]})
    messages.append({"role": "user", "content": TASK_ONE + tweet})
    return messages

# ====== Appel unitaire (retries + overrides) ======
def analyze_one_tweet(tweet: str) -> Dict[str, Any]:
    # Fast-path : règle avant LLM
    forced = _rule_override(tweet)
    if forced is not None:
        return forced

    messages = _build_messages(tweet)
    for attempt in range(MAX_RETRIES):
        try:
            res = get_client().chat.complete(
                model=MODEL,
                messages=messages,
                temperature=0.0,
                max_tokens=160,  # marge pour la sortie JSON
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
    return out  
