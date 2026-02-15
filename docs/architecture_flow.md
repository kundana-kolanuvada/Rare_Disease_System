# System Architecture Flow

This document provides a visual representation of the end-to-end data and execution flow for the agentic rare disease diagnostic system, from user input to the final analysis presented on the frontend.

graph TD
    subgraph "User on Frontend"
        A["1. User Enters Data <br/>(Symptoms, Demographics, History)"] --> B{"2. User Clicks Run Analysis"};
        B --> C["3. Frontend Sends API Request"];
        L["10. Frontend Renders <br/>Ranked Disease Cards"];
    end

    subgraph "Backend: FastAPI Application"
        D["4. API Endpoint in routes.py <br/>Receives Request"];
        E["5. RAG Extractor <br/>(extractor.py)"];
        F["6. LangGraph is Invoked <br/>with Initial State"];
        K["9. API Endpoint Formats <br/>and Sends JSON Response"];
    end

    subgraph "Backend: LangGraph Agentic Workflow"
        G["7. Symptom Analysis Agent <br/>(Executes Tool)"];
        H["disease_vector_search_tool <br/>(tools.py)"];
        I["...Future Agents... <br/>(e.g., Clinical Refiner)"];
    end

    subgraph "Backend: Data & Services"
        J["8. ChromaDB Vector Search <br/>(via matcher.py)"];
    end

    C --> D;
    D --> E;
    E -->|"Structured Symptoms"| F;
    F --> G;
    G --> H;
    H --> J;
    J -->|"Ranked Disease List"| H;
    H -->|"Results"| G;
    G -->|"Updated State with Matched Diseases"| I;
    I -->|"Final State"| F;
    F -->|"Returns Final State"| K;
    K --> L;