import os
import chromadb
from typing import List, Dict

from app.services.embedding_service import generate_embedding

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__)
        )
    )
)

chroma_client = chromadb.PersistentClient(
    path=os.path.join(BASE_DIR, "chroma_db")
)

collection = chroma_client.get_or_create_collection(name="diseases")

def match_diseases(
    symptom_text: str,
    top_k: int = 5
) -> List[Dict]:

    if not symptom_text.strip():
        return []

    query_embedding = generate_embedding(symptom_text)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    matches = []
    for i in range(len(results["ids"][0])):
        matches.append({
            "disease_name": results["metadatas"][0][i]["disease_name"],
            "similarity_score": round(
                1 - results["distances"][0][i], 4
            )
        })

    return matches
