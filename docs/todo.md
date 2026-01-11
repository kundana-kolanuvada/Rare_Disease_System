# Phase 3: Refinement and Advanced Matching - Work Breakdown

This plan divides the tasks for Phase 3, "Refinement and Advanced Matching", into two balanced roles for a collaborative effort, focusing on integrating a vector database (ChromaDB) for improved disease matching.

---

### **Part 1: Teammate 1 - Embedding Infrastructure & Data Pipeline**

This role focuses on creating the core embedding service and using it to build the disease vector database.

*   **1. Backend: Set up ChromaDB and install embedding model dependencies.**
    *   **Goal:** Prepare the environment for vector embeddings.
    *   **Implementation:** Add `chromadb` and `sentence-transformers` to `backend/requirements.txt` and install them.

*   **2. Backend: Create a reusable Embedding Service.**
    *   **File to Create:** `backend/app/services/embedding_service.py`
    *   **Goal:** Create a centralized service for generating text embeddings that can be used by other parts of the application.
    *   **Implementation:**
        1.  Initialize the embedding model (e.g., `SentenceTransformer('all-MiniLM-L6-v2')`) in this file so it's loaded only once.
        2.  Create a function `generate_embedding(text: str) -> List[float]` that takes a string and returns its vector embedding.

*   **3. Backend: Create the script to populate ChromaDB.**
    *   **File to Create:** `scripts/generate_embeddings.py`
    *   **Goal:** Use the new `embedding_service` to process `diseases.json` and load the embeddings into ChromaDB.
    *   **Implementation:**
        1.  Import the `generate_embedding` function from the `embedding_service`.
        2.  For each disease, call this function to generate its symptom embedding and store it in a ChromaDB collection.

---

### **Part 2: Teammate 2 - Advanced Matching API Integration**

This role focuses on using the new embedding infrastructure to upgrade the live API endpoint.

*   **4. Backend: Upgrade the Disease Matcher service to use ChromaDB.**
    *   **File to Modify:** `backend/app/services/matcher.py`
    *   **Goal:** Replace the current keyword-based matching with a vector similarity search.
    *   **Implementation:**
        1.  Import the `generate_embedding` function from the `embedding_service` (created by Teammate 1).
        2.  Modify the `match_diseases` function to:
            *   Take the user's symptom text.
            *   Call `generate_embedding` to get the vector for the user's text.
            *   Query the ChromaDB collection with this vector to find the most similar diseases.
            *   Process the results and return the ranked list.

*   **5. Backend: Update the API endpoint to utilize the advanced matcher.**
    *   **Files to Modify:** `backend/app/api/routes.py`
    *   **Goal:** Ensure the API endpoint correctly uses the upgraded matcher.
    *   **Implementation:** Adjust the `diagnose_endpoint` in `routes.py` to pass the raw symptom text to the new `match_diseases` function.

*   **6. Frontend: Verify compatibility and display of advanced matching results.**
    *   **Files to Modify:** `frontend/src/pages/Diagnose.tsx` (if needed).
    *   **Goal:** Ensure the frontend can display the results from the new advanced matching.
    *   **Implementation:** Verify that the frontend UI still displays the results correctly, making minor adjustments if any new fields are introduced in the `DiseaseMatch` schema.

---
