# core/rag.py
from typing import List
import re

class SimpleRAG:
    """
    RAG ultra simple :
    - on stocke des "documents" (paragraphes de doc technique)
    - on fait une recherche basique par mots-clés (count d'occurrences)
    -> suffisant pour un POC, pourra être remplacé par FAISS / embeddings plus tard.
    """
    def __init__(self):
        self.documents: List[str] = []

    def build_from_text(self, raw_text: str, min_chunk_length: int = 50):
        """
        Découpe le texte complet en "paragraphes" et les stocke.
        """
        if not isinstance(raw_text, str):
            return
        # split sur double saut de ligne
        chunks = re.split(r"\n\s*\n", raw_text)
        self.documents = [c.strip() for c in chunks if len(c.strip()) >= min_chunk_length]

    def query(self, query_text: str, top_k: int = 5) -> List[str]:
        """
        Recherche très naïve : score = nombre de mots en commun.
        """
        if not self.documents:
            return []
        if not isinstance(query_text, str) or not query_text.strip():
            return []

        query_words = set(query_text.lower().split())
        scores = []
        for doc in self.documents:
            doc_words = set(doc.lower().split())
            overlap = len(query_words & doc_words)
            scores.append(overlap)

        # on récupère les indices triés par score décroissant
        indices = sorted(range(len(self.documents)), key=lambda i: scores[i], reverse=True)
        top_indices = [i for i in indices if scores[i] > 0][:top_k]
        return [self.documents[i] for i in top_indices]
