This updated Implementation Plan integrates the LangGraph agentic architecture with your new, superior **Orphanet-based data enrichment strategy**. This version replaces the previous OMIM/Wikidata Step 0 with the localized XML fusion process, which is more viable for a college project and provides better structured clinical data.

---

# Refined Implementation Plan: Agentic Architecture with LangGraph

**Project Status:** Phase 3 Complete. The current system is a functional FastAPI pipeline with vector-based disease matching.

---

### **Phase 4: Refactor to an Agentic Workflow (Current Phase)**

The goal is to transform the existing services into the foundational nodes of a multi-agent graph.

**1. Install LangChain Dependencies & Setup Environment:**

* **Task:** Add `langchain`, `langgraph`, and `langchain-openai` to `backend/requirements.txt`.
* **Task:** Create a `.env` file in the `backend` directory and add your `OPENAI_API_KEY`.
* **Task:** Install dependencies: `backend/.venv/bin/pip install -r backend/requirements.txt`.

**2. Define the Agentic Core:**

* **State Definition (`state.py`):** Define `AgentState` to hold `symptom_text`, `user_demographics` (age, history), and `matched_diseases`.
* **Tool Definition (`tools.py`):** Wrap the vector matching logic from `matcher.py` into a `@tool` named `disease_vector_search_tool`.

**3. Build the Initial Graph (`graph.py`):**

* **Symptom Analysis Agent:** An agent that interprets user input and executes the `disease_vector_search_tool`.
* **Graph Assembly:** Use LangGraph's `StatefulGraph` to create an entry point leading to the `symptom_analyzer_node`.

**4. Update the API Endpoint:**

* Modify `routes.py` to invoke the graph: `app.invoke({"symptom_text": request.text, "user_demographics": request.demographics})`.

---

### **Phase 5: Orphanet Data Fusion & Clinical Refinement Agents**

Instead of using restricted APIs (OMIM), we will enrich the dataset locally and add specialized agents to reason over that clinical data.

**1. Step 0: Local Data Fusion (The Medical Brain):**
Perform this enrichment *before* the agents run to provide them with the `diseases_enriched.json`.

* **Task 1: Setup Folders:** Organize `/raw_data/Epidemiological_data/` and `/raw_data/Rare_diseases_with_associated_phenotypes/`.
* **Task 2: Enrichment Script (`scripts/enrich_dataset.py`):**
* **HPO-to-ORPHA Bridge:** Parse `en_product4.xml` to link HPO IDs to ORPHAcodes and extract **Symptom Frequencies**.
* **Clinical Context:** Parse `en_product9_ages.xml` to extract `PrevalenceClass`, `AverageAgeOfOnset`, and `TypeOfInheritance`.
* **Fusion:** Merge this data into `data/diseases_enriched.json`.



**2. Step 1: Develop Clinical Reasoning Tools:**
In `backend/app/agent_graph/tools.py`, create tools that use the enriched data:

* `clinical_context_scorer_tool`: Takes a list of potential diseases and compares the user's **Age** and **Family History** against the `AverageAgeOfOnset` and `TypeOfInheritance` found in the enriched JSON. It re-ranks results based on clinical fit.

**3. Step 2: Add Specialized Nodes to the Graph:**
In `backend/app/agent_graph/graph.py`, define:

* **Clinical Refiner Agent (Agent 3):** Equipped with the `clinical_context_scorer_tool`. It acts as the "Senior Consultant" that validates the vector search results against medical facts.
* **Explanation Agent:** Uses a tool to generate a plain-language summary of *why* a disease was ranked higher (e.g., "Matches your age group and common inheritance patterns").

**4. Step 3: Implement Conditional Logic:**

* **Edge 1:** `Symptom Analyzer` → `Clinical Refiner`.
* **Conditional Edge:** If the `Clinical Refiner` finds a high-confidence match (matching age and high frequency symptoms), proceed to `Explanation Agent`. If confidence is low, add a node to ask the user clarifying questions.

**5. Step 4: Enhance Frontend:**

* Update `Diagnose.tsx` to display clinical metadata (Prevalence, Age of Onset) alongside the disease name to provide transparency to the user.

---

### **Phase 6: Finalization and Deployment**

1. **Containerize:** Create `Dockerfile` and `docker-compose.yml` for the backend (LangGraph), frontend, and ChromaDB.
2. **Testing:** Run the graph through synthetic "Patient Profiles" (e.g., a 5-year-old with symptoms X, Y, Z) to ensure the Clinical Refiner correctly prioritizes pediatric-onset diseases.
3. **Documentation:** Document the graph architecture, the local XML parsing logic, and the scoring system used by the agents.