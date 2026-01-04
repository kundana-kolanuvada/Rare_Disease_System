# Implementation Plan: Rare Disease Diagnostic Assistant (MVP First)

This plan focuses on an iterative approach, starting with a Minimum Viable Product (MVP) to validate the core functionality before building the full system.

---

### **Phase 1: Project Setup & Data Foundation (1-2 Weeks)**

The goal of this phase is to set up the development environment and create a robust data pipeline for the rare disease data.

1.  **Initialize Project Structure:**
    -   Create a main project directory.
    -   Inside, create `backend` and `frontend` subdirectories.
    -   Initialize a Git repository.

2.  **Set Up Backend Environment (Python/FastAPI):**
    -   Create a Python virtual environment inside the `backend` directory.
    -   Install initial dependencies: `fastapi`, `uvicorn`, `requests`, `python-dotenv`.
    -   Create a basic "Hello World" FastAPI application to ensure it's working.

3.  **Build the Data Ingestion Pipeline:**
    -   Create a standalone Python script (`data_pipeline.py`) in a `scripts` directory.
    -   **Fetch Data:** Write functions to connect to the Orphanet API and download disease profiles. Start with a subset of 100-200 diseases for faster iteration.
    -   **Process and Clean:** For each disease, extract and clean the essential information: `orphacode`, `disorder_name`, `symptoms`, `genes`, `inheritance`.
    -   **Store Data:** Save the cleaned data into a structured format like a JSON file (`diseases.json`) or a SQLite database for now. This will be the source of truth for the disease matcher.

4.  **Set Up Frontend Environment (React/TypeScript):**
    -   Inside the `frontend` directory, initialize a new React project using Vite for speed: `npm create vite@latest . -- --template react-ts`.
    -   Install basic dependencies: `axios`.
    -   Clean up the default template to create a simple app structure.

---

### **Phase 2: Core MVP Development (2-3 Weeks)**

This phase focuses on building the core functionality: symptom input and disease matching.

1.  **Develop Agent 1: Symptom Extractor:**
    -   In the backend, create a module for the symptom extractor.
    -   **Initial Approach:** Start with a simple keyword-based extraction from the user's input text.
    -   **API Endpoint:** Create a FastAPI endpoint (e.g., `/extract-symptoms`) that takes a text input and returns a list of recognized symptoms.

2.  **Develop Agent 2: Disease Matcher (Simple Version):**
    -   In the backend, load the `diseases.json` data.
    -   Create a matching function that takes a list of symptoms and compares it against the symptoms of each disease in the database.
    -   **Algorithm:** Use a simple Jaccard similarity or a basic count of overlapping symptoms to calculate a match score.
    -   **API Endpoint:** Create a FastAPI endpoint (e.g., `/match-diseases`) that takes a list of symptoms and returns a ranked list of the top 10 diseases with their scores.

3.  **Build the MVP Frontend UI:**
    -   Create a simple form with a large text area for the user to describe their symptoms (as per the UI plan, Step 2).
    -   When the user submits the form, call the `/extract-symptoms` endpoint, then the `/match-diseases` endpoint.
    -   Display the returned ranked list of diseases in a clean, simple format.
    -   **Crucially:** Add the disclaimer that this is not a medical diagnosis.

---

### **Phase 3: Refinement and Advanced Matching (2 Weeks)**

Now that the MVP is working, improve the accuracy of the matching engine.

1.  **Integrate Vector Database:**
    -   Set up ChromaDB (can be run in-memory or as a Docker container).
    -   Modify your `data_pipeline.py` script.
    -   **Generate Embeddings:** For each disease, use a pre-trained clinical model (like BioBERT) to generate a vector embedding from its symptom list.
    -   **Load into ChromaDB:** Store these embeddings in a ChromaDB collection, associating each vector with its `orphacode`.

2.  **Upgrade the Disease Matcher:**
    -   Update the `/match-diseases` endpoint.
    -   Instead of simple keyword matching, generate an embedding from the user's input symptoms.
    -   Query ChromaDB with this input embedding to find the most similar disease vectors.
    -   Return the ranked list from ChromaDB. This will provide much more semantically relevant results.

---

### **Phase 4: Expanding Features (3-4 Weeks)**

With the core functionality robust, start adding the other agents and features from your original plan.

1.  **Develop Agent 3: Context & Demographics Scorer:**
    -   Add fields for age, sex, and family history to the frontend form.
    -   Create a new agent/module in the backend that takes the ranked list from the disease matcher and adjusts the scores based on this demographic context.

2.  **Develop Agent 4: Evidence & Recommendation Generator:**
    -   Integrate the PubMed API.
    -   For the top 3-5 diseases, create a function that searches PubMed for relevant case studies or research.
    -   Add this information to the API response.

3.  **Develop Agent 5: Explanation Agent:**
    -   Use a simple templating engine to generate the "Why this matches your case" explanations based on which symptoms overlapped.

4.  **Enhance the Frontend:**
    -   Build out the full multi-step form as designed in `rare_ui_design_plan.md`.
    -   Create the detailed results cards, including the evidence and explanations.
    -   Implement the feedback mechanism.

---

### **Phase 5: Finalization and Deployment (1-2 Weeks)**

1.  **Containerize the Application:**
    -   Create `Dockerfile`s for the backend and frontend.
    -   Create a `docker-compose.yml` file to orchestrate the backend, frontend, and databases for easy local development and deployment.
2.  **Testing and Refinement:**
    -   Test the system with synthetic patient data.
    -   Refine the UI/UX based on feedback.
3.  **Documentation:**
    -   Update the `README.md` with detailed instructions on how to set up and run the project.
    -   Document the API endpoints.

---

### **Project Timeline Summary**

This project is designed to be completed in iterative phases. The estimated timeline is as follows:

-   **Phase 1: Project Setup & Data Foundation:** 1-2 Weeks
-   **Phase 2: Core MVP Development:** 2-3 Weeks
-   **Phase 3: Refinement and Advanced Matching:** 2 Weeks
-   **Phase 4: Expanding Features:** 3-4 Weeks
-   **Phase 5: Finalization and Deployment:** 1-2 Weeks

**Total Estimated Project Duration: 9 to 13 weeks.**

This timeline is an estimate and can vary based on your pace and the complexity of implementation details. The phased approach allows for flexibility and ensures you have a working product at the end of each stage.
