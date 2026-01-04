# Tech Stack for Rare Disease Diagnostic Assistant

This project will be built using a modern, scalable web stack.

-   **Backend:**
    -   **Language:** Python
    -   **Framework:** FastAPI
    -   **Agent Orchestration:** LangChain or CrewAI (to be integrated in later phases for managing the multi-agent workflow).
    -   **Key Libraries:**
        -   `transformers` & `torch`: For loading and using clinical language models (e.g., BioBERT).
        -   `scikit-learn`: For traditional machine learning and data processing tasks.
        -   `requests`: For interacting with external APIs like Orphanet and PubMed.
        -   `psycopg2-binary`: For connecting to the PostgreSQL database.
        -   `uvicorn`: As the ASGI server to run FastAPI.

-   **Frontend:**
    -   **Framework:** React
    -   **Language:** TypeScript
    -   **Key Libraries:**
        -   `axios`: For making API calls to the backend.
        -   `react-router-dom`: For managing navigation between different views.
        -   `@mui/material` or `Chakra UI`: For a component library to build the UI quickly and consistently.

-   **Databases:**
    -   **Primary Database:** PostgreSQL
        -   **Use Case:** Storing user case data, feedback, and cached API results.
    -   **Vector Database:** ChromaDB
        -   **Use Case:** Storing disease embeddings and performing high-speed similarity searches for the disease matching agent.

-   **Development & Deployment:**
    -   **Package Manager (Backend):** `pip` with `requirements.txt` or `Poetry`.
    -   **Package Manager (Frontend):** `npm` or `yarn`.
    -   **Containerization:** Docker (using `docker-compose` for local development).
