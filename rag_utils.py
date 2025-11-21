import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

# Charge le modèle d'embedding une seule fois
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# -------------------------------
# Charger l'index RAG
# -------------------------------
def load_rag_index(path="rag_index.pkl"):
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data["texts"], data["embeddings"]


# -------------------------------
# Récupérer les k meilleurs contextes
# -------------------------------
def retrieve_context(query, texts, embeddings, k=3):
    """
    Retourne les k passages les plus pertinents.
    """
    query_emb = model.encode([query], convert_to_numpy=True)

    # Similarités cosinus
    scores = np.dot(embeddings, query_emb.T).flatten()

    # Indices triés par pertinence
    top_k_idx = scores.argsort()[::-1][:k]

    # Retour des meilleurs passages
    return [texts[i] for i in top_k_idx]
