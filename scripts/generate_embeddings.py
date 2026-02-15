import json
import os
import sys
import chromadb

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from backend.app.services.embedding_service import generate_embedding

def load_diseases(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

DATA_PATH = os.path.join(BASE_DIR, "backend", "data", "diseases.json")
DISEASES = load_diseases(DATA_PATH)

# Initialize ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="diseases",
    configuration={"hnsw": {"space": "cosine"}}
)

print("Processing diseases...")
for idx, disease in enumerate(DISEASES):
    disease_name = disease["disease_name"]
    hpo_terms = disease.get("hpo_terms", [])
    
    symptoms_text = " ".join(term["hpo_name"] for term in hpo_terms)
    hpo_ids = [term["hpo_id"] for term in hpo_terms]
    hpo_ids_str = ",".join(hpo_ids)

    combined_text = f"{disease_name}. Symptoms: {symptoms_text}"

    embedding = generate_embedding(combined_text)
    collection.add(
        ids=[str(idx)],
        embeddings=[embedding],
        metadatas=[{
            "disease_name": disease_name,
            "hpo_ids": hpo_ids_str
        }]
    )

    if (idx + 1) % 500 == 0:
        print(f"Processed {idx + 1}/{len(DISEASES)} diseases.")

print(f"\nDisease embeddings successfully generated and stored for {len(DISEASES)} diseases.")
print("Database Details:")
print(f" Collection Name: {collection.name}")
print(f" Distance Metric: cosine")
