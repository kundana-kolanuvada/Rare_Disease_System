import os
import json
import chromadb
from typing import List, Dict

from app.services.embedding_service import generate_embedding

# --- Pre-computation and Initialization ---

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__)
        )
    )
)

def create_hpo_map(json_path):
    hpo_map = {}
    with open(json_path, 'r', encoding='utf-8') as f:
        diseases = json.load(f)
        for disease in diseases:
            for term in disease.get("hpo_terms", []):
                if term["hpo_id"] not in hpo_map:
                    hpo_map[term["hpo_id"]] = term["hpo_name"]
    return hpo_map

DATA_PATH = os.path.join(BASE_DIR, "backend", "data", "diseases.json")
HPO_ID_TO_NAME_MAP = create_hpo_map(DATA_PATH)

chroma_client = chromadb.PersistentClient(
    path=os.path.join(BASE_DIR, "chroma_db")
)

collection = chroma_client.get_or_create_collection(name="diseases")


# --- Main Service Function ---

def match_diseases(
    symptom_text: str,
    top_k: int = 5
) -> List[Dict]:
    """
    Performs vector search and returns disease matches with structured HPO term information.
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
        
        # Retrieve the HPO IDs string and split it back into a list
        hpo_ids_str = metadata.get("hpo_ids", "")
        matched_hpo_ids = hpo_ids_str.split(',') if hpo_ids_str else []
        
        matched_terms_structured = []
        for hpo_id in matched_hpo_ids:
            hpo_name = HPO_ID_TO_NAME_MAP.get(hpo_id, "Unknown HPO Term")
            matched_terms_structured.append({"hpo_id": hpo_id, "hpo_name": hpo_name})

        matches.append({
            "disease_name": metadata.get("disease_name", "Unknown disease"),
            "match_score": round(1 - results["distances"][0][i], 4),
            "matched_terms": matched_terms_structured
        })

    return matches
