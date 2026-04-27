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


def _first_non_empty(*values):
    for value in values:
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned:
                return cleaned
        elif value is not None:
            return value
    return None

def match_diseases(
    symptom_text: str,
    top_k: int = 15
) -> List[Dict]:
    """
    Performs vector search and returns disease matches using metadata stored in ChromaDB.
    No external JSON files are needed for this lookup.
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
        metadata = results["metadatas"][0][i] or {}
        
        # 1. Retrieve the HPO IDs and Names from metadata
        hpo_ids_str = metadata.get("hpo_ids", "")
        hpo_names_str = metadata.get("hpo_names", "")
        
        # 2. Split using their respective delimiters
        hpo_ids = hpo_ids_str.split(',') if hpo_ids_str else []
        hpo_names = hpo_names_str.split('|') if hpo_names_str else []
        
        # 3. Zip them back into structured term objects
        matched_terms_structured = []
        for j in range(len(hpo_ids)):
            name = hpo_names[j] if j < len(hpo_names) else "Unknown HPO Term"
            matched_terms_structured.append({
                "hpo_id": hpo_ids[j],
                "hpo_name": name
            })

        # 4. Construct the match result (including new clinical fields for later use)
        disease_name = _first_non_empty(
            metadata.get("disease_name"),
            metadata.get("name"),
            metadata.get("disease"),
            metadata.get("label"),
            metadata.get("disorder_name"),
            metadata.get("preferred_label"),
            metadata.get("title"),
        )
        if not disease_name:
            disease_name = f"ORPHA:{metadata.get('orpha_code')}" if metadata.get("orpha_code") else "Unnamed disease"

        matches.append({
            "disease_name": disease_name,
            "match_score": round(1 - results["distances"][0][i], 4),
            "matched_terms": matched_terms_structured,
            "orpha_code": metadata.get("orpha_code"),
            # clinical metadata
            "onset": metadata.get("onset"),
            "inheritance": metadata.get("inheritance"),
            "prevalence": metadata.get("prevalence"),
            "genes": metadata.get("genes"),
            # future scoring support
            "symptom_weights": metadata.get("symptom_weights", {})
        })

    return matches
