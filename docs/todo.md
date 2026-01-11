# Phase 3: Refinement and Advanced Matching - Work Breakdown

This plan divides the tasks for Phase 3, "Refinement and Advanced Matching", into two balanced roles for a collaborative effort, focusing on integrating a vector database (ChromaDB) for improved disease matching.

---

### **Part 1: Teammate 1 - Embedding Generation & ChromaDB Setup**

This role focuses on setting up the vector database and populating it with disease symptom embeddings.

*   **1. Backend: Set up ChromaDB and install embedding model dependencies.**
    *   **Goal:** Prepare the backend environment for generating and storing vector embeddings.
    *   **Implementation:**
        1.  Add `chromadb` and `sentence-transformers` (for generating embeddings) to `backend/requirements.txt`.
        2.  Run `pip install -r backend/requirements.txt` in the backend virtual environment to install these new dependencies.

*   **2. Backend: Create a script to generate and store disease embeddings in ChromaDB.**
    *   **File to Create:** `scripts/generate_embeddings.py`
    *   **Goal:** Process the `diseases.json` data, generate vector embeddings for each disease's symptoms, and load them into a ChromaDB collection.
    *   **Implementation:**
        1.  Load the `diseases.json` file.
        2.  Initialize an embedding model, for example, `SentenceTransformer('all-MiniLM-L6-v2')` as a lightweight option to start.
        3.  For each disease entry:
            *   Extract and combine its symptom names (e.g., from `hpo_terms`) into a single text string.
            *   Generate an embedding (vector) for this symptom string using the initialized model.
            *   Store the embedding, the disease's `orphacode` (as ID), and relevant metadata (like disease name, symptoms) in a ChromaDB collection.

---

### **Part 2: Teammate 2 - Advanced Matching Integration & API Update**

This role focuses on integrating the new ChromaDB-based matching into the existing backend API and verifying frontend compatibility.

*   **3. Backend: Upgrade the Disease Matcher service to use ChromaDB.**
    *   **File to Modify:** `backend/app/services/matcher.py`
    *   **Goal:** Replace the current keyword-based matching logic with a vector similarity search using the ChromaDB collection populated by Teammate 1.
    *   **Implementation:**
        1.  Modify the `match_diseases` function:
            *   Initialize and connect to the ChromaDB collection (ensuring it's populated from `generate_embeddings.py`).
            *   Take the user's input symptoms (which will still be HPO IDs from the `extractor`, but can be translated back to text or have an embedding generated for the query).
            *   Generate an embedding for the user's input symptoms.
            *   Query the ChromaDB collection using this user embedding to find the `top_k` most similar disease vectors.
            *   Retrieve the associated disease information (name, `orphacode`) from ChromaDB's metadata.
            *   Calculate a `match_score` based on the similarity distance returned by ChromaDB (e.g., cosine similarity).
            *   Return the ranked list of `DiseaseMatch` objects.

*   **4. Backend: Update the API endpoint to utilize the advanced matcher.**
    *   **File to Modify:** `backend/app/api/routes.py`
    *   **Goal:** Ensure the `/api/v1/diagnose` endpoint correctly uses the upgraded `matcher.py` with its new vector-based logic.
    *   **Implementation:**
        1.  Review the `diagnose_endpoint` in `routes.py`. If the `match_diseases` function's signature was changed significantly (e.g., now taking raw text instead of HPO IDs directly), update the endpoint call accordingly. Otherwise, simply ensure it continues to pass the necessary arguments (like extracted HPO IDs or the raw symptom text) to the new matcher.

*   **5. Frontend: Verify compatibility and display of advanced matching results.**
    *   **File to Modify:** `frontend/src/pages/Diagnose.tsx` and `frontend/src/services/api.ts` (if `DiseaseMatch` schema changes).
    *   **Goal:** Confirm that the existing frontend UI can handle and correctly display the output from the new advanced matching engine.
    *   **Implementation:**
        1.  Review the `DiseaseMatch` Pydantic model (`backend/app/models/schemas.py`) and its corresponding TypeScript interface (`frontend/src/services/api.ts`). If the new matching logic introduces new fields or changes the meaning of existing ones, update these schemas.
        2.  Verify that `frontend/src/pages/Diagnose.tsx` correctly renders the `match_score`, disease names, and any other relevant information from the API response. No significant UI changes are expected unless the `DiseaseMatch` structure was explicitly altered.

---