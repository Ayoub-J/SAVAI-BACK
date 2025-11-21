import os
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("MODEL", "mistral-tiny")
API_KEY = os.getenv("API_KEY")

# ====== Charger la FAQ selon thème ======
FAQ_FILES = {
    "panne_fibre": "RAG-knowledge/fibre_problems.txt",
    "debit_internet": "RAG-knowledge/internet_wifi_debit.txt",
    "erreur_freebox": "RAG-knowledge/freebox_errors_and_fix.txt",
    "facturation": "RAG-knowledge/facturation_free.txt",
    "mobile": "RAG-knowledge/mobile_problems.txt",
    "resiliation": "RAG-knowledge/resiliation_procedures.txt",
    "contact_sav": "RAG-knowledge/sav_free_contacts.txt",
    "general": "RAG-knowledge/general_faq_free.txt",
}

def load_faq(theme):
    theme = str(theme).lower().strip()
    path = FAQ_FILES.get(theme, FAQ_FILES["general"])

    if not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


# ====== Charger le prompt ======
def load_prompt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


# ====== TEST : 1 seul tweet ======

tweet = "Ma fibre ne marche plus depuis hier, ça clignote rouge 😡"
sentiment = "negatif"
theme = "panne_fibre"
urgence = 2

faq_text = load_faq(theme)

prompt = load_prompt("Prompt-files/prompt-response.txt")
prompt = (
    prompt.replace("{tweet}", tweet)
          .replace("{sentiment}", sentiment)
          .replace("{theme}", theme)
          .replace("{urgence}", str(urgence))
          .replace("{faq}", faq_text)
)

print("\n==== PROMPT ENVOYÉ AU LLM ====\n")
print(prompt)
print("\n==============================\n")

client = Mistral(api_key=API_KEY)

reply = client.chat.complete(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3,
    max_tokens=200
)

print("==== RÉPONSE DU LLM ====\n")
print(reply.choices[0].message.content)
print("\n========================\n")
