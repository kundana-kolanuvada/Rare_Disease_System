import json
import os
import sys
import chromadb

# Add the project root to sys.path so we can import our services
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from backend.app.services.embedding_service import generate_embedding

# Paths
ENRICHED_DATA_PATH = os.path.join(BASE_DIR, "backend", "data", "enriched_metadata.json")
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

def load_enriched_data():
    if not os.path.exists(ENRICHED_DATA_PATH):
        print(f"Error: Enriched metadata file not found at {ENRICHED_DATA_PATH}")
        sys.exit(1)
    with open(ENRICHED_DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def reindex():
    print("Loading enriched metadata...")
    enriched_data = load_enriched_data()
    
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # Delete the old collection if it exists to start fresh
    try:
        client.delete_collection(name="diseases")
        print("Deleted existing 'diseases' collection.")
    except:
        print("No existing 'diseases' collection found. Creating new.")
        
    collection = client.create_collection(
        name="diseases",
        configuration={"hnsw": {"space": "cosine"}}
    )

    print(f"Re-indexing {len(enriched_data)} diseases...")
    
    for idx, (orpha_code, data) in enumerate(enriched_data.items()):
        disease_name = data["name"]
        symptoms = data.get("symptoms", [])
        
        # 1. Prepare text for embedding (Name + All Symptom Names)
        symptom_names = [s["hpo_name"] for s in symptoms]
        combined_text = f"{disease_name}. Symptoms: {', '.join(symptom_names)}"
        
        # 2. Prepare Metadata (ChromaDB requires strings, ints, or floats)
        # We'll store lists as comma-separated strings
        metadata = {
            "orpha_code": orpha_code,
            "disease_name": disease_name,
            "onset": ", ".join(data.get("onset", [])),
            "inheritance": ", ".join(data.get("inheritance", [])),
            "prevalence": ", ".join(data.get("prevalence", [])),
            "genes": ", ".join(data.get("genes", [])),
            "hpo_ids": ",".join([s["hpo_id"] for s in symptoms]),
            "hpo_names": "|".join([s["hpo_name"] for s in symptoms]) # Use pipe to avoid confusion with commas in names
        }

        # 3. Generate Embedding and Add to Collection
        embedding = generate_embedding(combined_text)
        
        collection.add(
            ids=[orpha_code], # Use OrphaCode as the primary ID
            embeddings=[embedding],
            metadatas=[metadata]
        )

        if (idx + 1) % 500 == 0:
            print(f"Processed {idx + 1}/{len(enriched_data)} diseases.")

    print(f"\nSuccessfully re-indexed {len(enriched_data)} diseases into ChromaDB!")


if __name__ == "__main__":
    reindex()
