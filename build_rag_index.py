import os
import pickle
from sentence_transformers import SentenceTransformer

def load_all_documents(folder="knowledge_base"):
    docs = []
    print("\n📥 Chargement des documents...")

    for file in os.listdir(folder):
        path = os.path.join(folder, file)

        if file.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                text = f.read().strip()

                # On découpe par paragraphes pour de petits chunks
                parts = text.split("\n\n")
                docs.extend([p.strip() for p in parts if len(p.strip()) > 20])

    print(f"📄 {len(docs)} morceaux de connaissances détectés.")
    return docs


def build_rag_index():
    docs = load_all_documents()

    print("⚙️ Chargement du modèle d'embedding...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    print("🧠 Génération des embeddings...")
    embeddings = model.encode(docs)

    print("💾 Sauvegarde de l'index RAG dans rag_index.pkl ...")
    with open("rag_index.pkl", "wb") as f:
        pickle.dump({
            "texts": docs,           # 🔥 IMPORTANT : les clés correctes
            "embeddings": embeddings # 🔥
        }, f)

    print("🎉 Index RAG créé avec succès !")


if __name__ == "__main__":
    build_rag_index()
