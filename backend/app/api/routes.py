from fastapi import APIRouter
from typing import List

from app.models.schemas import DiseaseMatch, SymptomRequest
from app.agent_graph.graph import symptom_analysis_graph

router = APIRouter()


@router.post("/diagnose", response_model=List[DiseaseMatch])
def diagnose_endpoint(request: SymptomRequest):

    result = symptom_analysis_graph.invoke({
        "symptoms": request.symptoms,
        "top_k": request.top_k,
        "age": request.age,
        "sex": request.sex,
        "ethnicity": request.ethnicity,
        "country": request.country,
        "family_history": request.family_history,
        "family_history_description": request.family_history_description,
        "symptom_onset": request.symptom_onset,
        "previous_diagnoses": request.previous_diagnoses,
        "previous_tests": request.previous_tests
    })

    return result["matched_diseases"]