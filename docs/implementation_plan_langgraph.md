# Implementation Plan: Agentic Architecture with LangGraph

**Project Status:** Phase 3 Complete. The current system is a functional FastAPI pipeline with vector-based disease matching.

**Next Step:** Refactor the existing pipeline into a scalable, agentic architecture using LangChain and LangGraph before expanding its capabilities.

---

### **Phase 4: Refactor to an Agentic Workflow (Current Phase)**

The goal is to transform the existing services into the foundational nodes of a multi-agent graph.

**1. Install LangChain Dependencies & Setup Environment:**
- **Task:** Add `langchain`, `langgraph`, and `langchain-openai` to `backend/requirements.txt`.
- **Task:** Create a `.env` file in the `backend` directory and add your `OPENAI_API_KEY`.
- **Task:** Install the new dependencies into your virtual environment:
  ```bash
  backend/.venv/bin/pip install -r backend/requirements.txt
  ```

**2. Define the Agentic Core:**
- **Task:** Create a new directory: `backend/app/agent_graph`.
- **State Definition:** Create `backend/app/agent_graph/state.py`. Define a `TypedDict` called `AgentState` to hold the data that flows through the graph (e.g., `symptom_text: str`, `matched_diseases: list`).
- **Tool Definition:** Create `backend/app/agent_graph/tools.py`. Refactor your existing services into tools:
    - Wrap the vector-based matching logic from `backend/app/services/matcher.py` into a LangChain `@tool` function named `disease_vector_search_tool`. This tool will take symptom text as input and return a list of matched diseases from ChromaDB.

**3. Build the Initial Graph:**
- **Task:** Create `backend/app/agent_graph/graph.py`.
- **LLM & Agent Definition:**
    - Define a `ChatOpenAI` model instance.
    - Define the first true agent: the **Symptom Analysis Agent**. This agent's role is to interpret the user's input and decide if it's suitable for a search. For now, its primary job is to call the search tool.
- **Node Definition:**
    - Implement an agent node function, `symptom_analyzer_node`, which executes the Symptom Analysis Agent. This agent will be equipped with the `disease_vector_search_tool`.
- **Graph Assembly:**
    - Use LangGraph's `StatefulGraph` to build a simple graph with an entry point that leads to the `symptom_analyzer_node`.
    - Compile the graph into a runnable `app`.

**4. Update the API Endpoint:**
- **Task:** Modify `backend/app/api/routes.py`.
- **Implementation:**
    - Import the compiled graph `app`.
    - Change the `diagnose_endpoint` to invoke the graph with the request's symptom text: `app.invoke({"symptom_text": request.text})`.
    - Return the final state from the graph.

At the end of this phase, your application will produce the same output as before, but the underlying logic will be running inside a scalable agentic framework.

---

### **Phase 5: Expand the Graph with Enriched Data and New Agents**

**Step 0: Data Fusion with OMIM and Wikidata**

*   **Goal:** Enrich your dataset with `inheritance`, `age_of_onset`, and `prevalence` data by programmatically linking your diseases to the OMIM database.
*   **Tasks:**
    1.  **Create the Enrichment Script:** Create a new script: `scripts/enrich_dataset.py`. This script will perform a multi-step process for each disease.
    2.  **Task 1: Find the OMIM ID (via Wikidata):** Inside your script, create a function that takes a disease name (e.g., "Ehlers-Danlos syndrome, classical type") and queries Wikidata's free API to find its corresponding "OMIM ID" property.
    3.  **Task 2: Fetch Disease Data from OMIM:** OMIM provides a free API that allows you to fetch entries using an OMIM ID (requires a free API key). Your script will call the OMIM API to retrieve the full data entry.
    4.  **Task 3: Parse the OMIM Data:** The core logic of your script will be to parse the text entry from OMIM to extract fields like "INHERITANCE", "CLINICAL FEATURES" (for age of onset), and "PREVALENCE".
    5.  **Task 4: Fuse and Save:** Combine the newly extracted data with the existing information for each disease in your `diseases.json`. Save the final, combined object to a new file: `data/diseases_enriched.json`.

**Step 1. Develop New Tools:**
- **Task:** In `backend/app/agent_graph/tools.py`, create the tools for the remaining agents using the new `diseases_enriched.json` file.
    - `context_scorer_tool`: A function that takes diseases and demographics, then re-ranks them based on the new enriched data.
    - `evidence_generator_tool`: A tool that uses a library like `pubmed-lookup` or a custom web search tool to find supporting literature.
    - `explanation_generator_tool`: A tool that takes the final results and generates a plain-language summary.

**Step 2. Add New Agents and Nodes to the Graph:**
- **Task:** In `backend/app/agent_graph/graph.py`, define the new agents and their corresponding nodes:
    - **Contextual Scorer Agent:** An agent equipped with the `context_scorer_tool`.
    - **Evidence Retrieval Agent:** An agent that uses the `evidence_generator_tool`.
    - **Explanation Agent:** An agent that uses the `explanation_generator_tool`.
    - Add the corresponding nodes (`context_scorer_node`, etc.) to your graph definition.

**Step 3. Implement Conditional Graph Edges:**
- **Task:** Enhance `graph.py` to control the workflow with conditional logic.
- **Implementation:**
    - After the `symptom_analyzer_node`, add an edge to the `context_scorer_node`.
    - After scoring, add a conditional edge: if scores are above a certain threshold, proceed to the `evidence_retrieval_node`. Otherwise, proceed directly to the `explanation_node`.
    - The final step should be the `explanation_node`, which leads to the end of the graph.

**Step 4. Enhance the Frontend:**
- **Task:** Update the frontend components in `frontend/src/pages/Diagnose.tsx` to display the new, richer information (explanations, evidence links, updated scores) returned by the agentic graph.

---

### **Phase 6: Finalization and Deployment (Previously Phase 5)**

The goal of this final phase remains the same.

1.  **Containerize the Application:**
    - Create `Dockerfile`s and a `docker-compose.yml` file to orchestrate the backend (now running LangGraph), frontend, and ChromaDB.
2.  **Testing and Refinement:**
    - Test the full agentic workflow with synthetic patient data.
    - Refine agent prompts, tools, and graph logic based on results.
3.  **Documentation:**
    - Update the `README.md` with instructions on how to run the new agentic system.
    - Document the agent roles, tools, and the graph's decision logic.