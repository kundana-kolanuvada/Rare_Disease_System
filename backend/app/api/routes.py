from fastapi import APIRouter
from typing import List

from app.models.schemas import DiseaseMatch, SymptomRequest
from app.agent_graph.graph import invoke_atlas_dx

router = APIRouter()


@router.post("/diagnose")
def diagnose_endpoint(request: SymptomRequest):

    # Invoke the agentic supervisor
    result = invoke_atlas_dx({
        "symptoms": request.symptoms,
        "main_symptoms": request.main_symptoms,
        "top_k": request.top_k,
        "age": request.age,
        "sex": request.sex,
        "ethnicity": request.ethnicity,
        "country": request.country,
        "family_history": request.family_history,
        "family_history_description": request.family_history_description,
        "consanguinity": request.consanguinity,
        "symptom_onset": request.symptom_onset,
        "genetic_testing": request.genetic_testing,
        "previous_diagnoses": request.previous_diagnoses,
        "previous_tests": request.previous_tests
    })

    # Return the final text report or structured matches if we implement parsing
    return result
