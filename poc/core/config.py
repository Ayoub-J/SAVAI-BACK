# core/config.py
from dataclasses import dataclass, field
from typing import List

# Comptes SAV de Free (pour inbound/outbound)
FREE_ACCOUNTS = {
    "free", "freebox", "free_1337",
    "groupeiliad", "freemobile", "free_mobile"
}

# Colonnes minimales attendues dans le CSV
REQUIRED_COLUMNS = ["id", "created_at", "full_text", "screen_name", "in_reply_to"]

DEFAULT_CLASSIFY_MODEL = "mistral-small-latest"
DEFAULT_REPLY_MODEL = "mistral-small-latest"

DEFAULT_CLASSIFY_PROMPT = """\
Tu es un assistant qui analyse des tweets adressés à un service client télécom (SAV).

Analyse le tweet ci-dessous et réponds STRICTEMENT en JSON valide, sans texte autour.

Tweet :
"{tweet_text}"

Tu dois renvoyer un JSON de la forme :

{{
  "sentiment": "positive | negative | neutral | mixed",
  "sentiment_confidence": 0.0-1.0,
  "urgency": "critique | haute | normale | basse",
  "urgency_confidence": 0.0-1.0,
  "category": "une catégorie parmi : {categories}",
  "category_confidence": 0.0-1.0,
  "theme": "résumé très court du thème principal (5-10 mots)",
  "overall_confidence": 0.0-1.0
}}

Contraintes :
- sentiment_confidence, urgency_confidence, category_confidence, overall_confidence sont des nombres entre 0 et 1.
- category DOIT être choisie parmi la liste fournie.
- Réponds en français.
"""

DEFAULT_REPLY_PROMPT = """\
Tu es un agent du service client sur Twitter/X pour un opérateur télécom (Free).
On te fournit :
- le tweet du client
- le sentiment détecté
- l'urgence détectée
- la catégorie métier
- un contexte de documentation technique (RAG) éventuel

Tu dois proposer une réponse professionnelle, empathique, claire, en français, adaptée à Twitter (max ~280 caractères),
et respecter la politique de communication SAV (pas de promesses impossibles, pas d'informations sensibles).

Retourne STRICTEMENT un JSON valide de la forme :

{{
  "reply_text": "texte de la réponse en français",
  "reply_confidence": 0.0-1.0
}}

Données :
- Tweet : "{tweet_text}"
- Sentiment : {sentiment}
- Urgence : {urgency}
- Catégorie : {category}
- Contexte technique : "{rag_context}"
"""

@dataclass
class AppConfig:
    """Configuration métier de l'application."""
    confidence_threshold: float = 0.7
    classify_model: str = DEFAULT_CLASSIFY_MODEL
    reply_model: str = DEFAULT_REPLY_MODEL
    categories: List[str] = field(default_factory=lambda: [
        "plainte_service",
        "question_technique",
        "demande_aide",
        "reclamation_rdv",
        "information_commerciale",
        "spam",
        "autre",
    ])
    classify_prompt: str = DEFAULT_CLASSIFY_PROMPT
    reply_prompt: str = DEFAULT_REPLY_PROMPT
    rag_text: str = ""  # texte brut de doc technique (RAG simple)
