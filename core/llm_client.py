# core/llm_client.py
import os
import json
import re
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

try:
    from mistralai import Mistral
    HAVE_MISTRAL = True
except ImportError:
    HAVE_MISTRAL = False
    import requests  # fallback HTTP

def get_mistral_api_key() -> Optional[str]:
    key = os.getenv("MISTRAL_API_KEY")
    return key

def get_mistral_client():
    api_key = get_mistral_api_key()
    if not api_key:
        return None
    if HAVE_MISTRAL:
        return Mistral(api_key=api_key)
    else:
        # on renvoie la clé, utilisée par HTTP
        return api_key

def mistral_chat(prompt: str, model: str, temperature: float = 0.1, max_tokens: int = 512) -> Optional[str]:
    """
    Appel générique à l'API Mistral (SDK si dispo, sinon HTTP).
    Retourne le texte brut de la réponse ou None en cas d'erreur.
    """
    api_key_or_client = get_mistral_client()
    if api_key_or_client is None:
        return None

    system_prompt = "Tu es un assistant spécialisé en analyse de tweets SAV en français."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    if HAVE_MISTRAL:
        try:
            resp = api_key_or_client.chat.complete(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content
        except Exception as e:
            print(f"Erreur Mistral (SDK) : {e}")
            return None
    else:
        try:
            import requests
            url = "https://api.mistral.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key_or_client}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            r = requests.post(url, headers=headers, json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Erreur Mistral (HTTP) : {e}")
            return None

def extract_json_from_text(text: str):
    """
    Essaie d'extraire un JSON à partir d'un texte renvoyé par le LLM.
    """
    if not isinstance(text, str):
        return None
    # tentative directe
    try:
        return json.loads(text)
    except Exception:
        pass

    # recherche d'un bloc {...}
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None
