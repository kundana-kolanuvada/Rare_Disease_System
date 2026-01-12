import json
import os
import sys
import chromadb
from chromadb.config import Settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from backend.app.services.embedding_service import generate_embedding

def load_diseases(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

DATA_PATH = os.path.join(BASE_DIR, "backend", "data", "diseases.json")
DISEASES = load_diseases(DATA_PATH)

# Initialize ChromaDB (local persistent DB)
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="diseases"
)

for idx, disease in enumerate(DISEASES):
    disease_name = disease["disease_name"]
    symptoms = " ".join(
        term["hpo_name"] for term in disease.get("hpo_terms", [])
    )

    combined_text = f"{disease_name}. Symptoms: {symptoms}"

    embedding = generate_embedding(combined_text)
    collection.add(
        ids=[str(idx)],
        embeddings=[embedding],
        metadatas=[{
            "disease_name": disease_name
        }]
    )

client.persist()
print("Disease embeddings successfully generated and stored.")