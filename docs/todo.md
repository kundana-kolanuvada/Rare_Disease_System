# Phase 2: Core MVP Development - Work Breakdown

This document divides the tasks for Phase 2, "Core MVP Development", into two balanced roles for a collaborative effort, with each teammate working on both frontend and backend components.

---

### **Part 1: Teammate 1 - Data Extraction & Frontend Service**

This role focuses on the core data transformation logic (extracting symptoms from text) and setting up the frontend infrastructure to handle the API communication state.

*   **1. Backend: Implement the HPO Symptom Extractor (Agent 1)**
    *   **File to Create/Modify:** `backend/app/services/extractor.py`
    *   **Goal:** Create a service that turns raw user text into a list of HPO IDs.
    *   **Implementation:**
        1.  Load `diseases.json` (located at `backend/data/diseases.json`) once when the module starts.
        2.  Create a dictionary that maps lowercase HPO symptom names to HPO IDs (e.g., `"joint hypermobility"` -> `"HP:0001382"`).
        3.  Create a function `extract_hpo_ids_from_text(text: str) -> List[str]`.
        4.  This function will take a string, convert it to lowercase, and find all known symptom names within it, collecting the corresponding HPO IDs.
        5.  Use the `normalize_hpo_ids` function from `backend/app/services/normalizer.py` to return a clean and unique list of HPO IDs.

*   **2. Frontend: Create the API service module**
    *   **File to Create:** `frontend/src/services/api.ts`
    *   **Goal:** Define the frontend "contract" for calling the backend.
    *   **Implementation:**
        1.  Using `axios`, create an asynchronous function `runDiagnostics(symptomsText: string)`.
        2.  This function will be responsible for making a `POST` request to the backend. Teammate 2 will build the endpoint, but you can assume it will be at `/api/v1/diagnose`.
        3.  The function should take the symptom text, send it in a JSON body (e.g., `{ "text": symptomsText }`), and be prepared to return the backend's response data.

*   **3. Frontend: Add loading and error state management**
    *   **File to Modify:** `frontend/src/pages/Diagnose.tsx`
    *   **Goal:** Prepare the UI to give users feedback during API calls.
    *   **Implementation:**
        1.  Add new state variables to the component: `isLoading` (boolean) and `error` (string or null).
        2.  In the JSX, add conditional logic:
            *   If `isLoading` is `true`, show a loading indicator.
            *   If `error` is not null, display a user-friendly error message.
        3.  The actual logic to set these states will be implemented by Teammate 2 when they connect the UI to the service you built.

---

### **Part 2: Teammate 2 - API Routing & Results Display**

This role focuses on wiring together the backend services into a usable endpoint and connecting the frontend UI to it to display the final results.

*   **4. Backend: Create the API endpoints and data schemas**
    *   **Files to Modify:** `backend/app/api/routes.py` and `backend/app/models/schemas.py`.
    *   **Goal:** Create the live API route that the frontend will call.
    *   **Implementation:**
        1.  In `schemas.py`, define Pydantic models for the API request (`SymptomRequest`) and response bodies. For example, the request model for `/api/v1/diagnose` will expect a `text: str`. The response model should align with the output of `matcher.py`.
        2.  In `routes.py`, create a `POST` endpoint `/api/v1/diagnose`.
        3.  This endpoint will use the `extract_hpo_ids_from_text` function (from Teammate 1's work) and the existing `match_diseases` function from `backend/app/services/matcher.py` to process the request and generate results.
        4.  Wire these services together: the endpoint function will take the request, call the extractor, then call the matcher with the extractor's output, and return the final list.

*   **5. Frontend: Connect the UI to the API service**
    *   **File to Modify:** `frontend/src/pages/Diagnose.tsx`
    *   **Goal:** Make the "Run Analysis" button trigger a real API call.
    *   **Implementation:**
        1.  Import the `runDiagnostics` function from the `api.ts` service (created by Teammate 1).
        2.  Find the handler function for the "Run Rare Disease Analysis" button.
        3.  Inside it, call `runDiagnostics` and handle the asynchronous response. Set the `isLoading` and `error` states (prepared by Teammate 1) appropriately before and after the call.
        4.  On a successful response, store the list of diseases in a new `results` state variable.

*   **6. Frontend: Implement dynamic rendering of disease match results**
    *   **File to Modify:** `frontend/src/pages/Diagnose.tsx`
    *   **Goal:** Show the actual data from the backend instead of the mock-up.
    *   **Implementation:**
        1.  In the JSX, find the hardcoded result card in the "Analysis Results" section.
        2.  Replace it with logic to map over the `results` state array. For each disease in the array, render a `result-card` component, populating it with the real name, score, and other details from the API response.

*   **7. Backend: Test the complete end-to-end backend endpoint**
    *   **Method:** Use FastAPI's `/docs` page or a tool like `curl`.
    *   **Goal:** As the person building the endpoint, ensure it works as expected before the frontend fully depends on it.
    *   **Implementation:** Send test requests with sample symptom descriptions and verify that the endpoint returns the expected JSON structure with a ranked list of diseases. This helps ensure a smooth integration with the frontend.
