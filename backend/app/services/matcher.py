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

collection = chroma_client.get_or_create_collection(
    name="diseases"
)

def match_diseases(
    symptom_text: str,
    top_k: int = 5
) -> List[Dict]:
    """
    Perform text-based disease matching using embeddings + ChromaDB.
    """

    if not symptom_text or not symptom_text.strip():
        return []

    query_embedding = generate_embedding(symptom_text)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    if not results.get("ids") or not results["ids"][0]:
        return []

    matches = []

    for i in range(len(results["ids"][0])):
        metadata = results["metadatas"][0][i]
        matches.append({
            "disease_name": metadata.get("disease_name", "Unknown disease"),
            "match_score": round(1 - results["distances"][0][i], 4),
            "matched_hpo_ids": metadata.get("hpo_ids", [])
        })

    return matches