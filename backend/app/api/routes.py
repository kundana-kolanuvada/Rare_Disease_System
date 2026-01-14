from fastapi import APIRouter
from typing import List

from app.services.matcher import match_diseases
from app.models.schemas import DiseaseMatch, SymptomRequest

router = APIRouter()

@router.post("/diagnose", response_model=List[DiseaseMatch])
def diagnose_endpoint(request: SymptomRequest):
    """
    Receives raw symptom text and returns top disease matches.
    """
    return match_diseases(
        symptom_text=request.text,
        top_k=request.top_k
    )
