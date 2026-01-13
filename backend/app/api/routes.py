from fastapi import APIRouter
from app.services.matcher import match_diseases  # new advanced matcher
from app.models.schemas import MatchRequest, DiseaseMatch, SymptomRequest
from typing import List

router = APIRouter()

# Existing HPO-based matching endpoint
@router.post("/match", response_model=List[DiseaseMatch])
def match_endpoint(request: MatchRequest):
    results = match_diseases(
        user_hpo_ids=request.hpo_ids,
        top_k=request.top_k
    )
    return results

# Updated diagnose endpoint to use advanced matcher with raw text
@router.post("/api/v1/diagnose", response_model=List[DiseaseMatch])
def diagnose_endpoint(request: SymptomRequest):
    """
    Receives raw symptom text and returns top disease matches.
    """
    # Pass raw text directly to the advanced matcher
    results = match_diseases(
        symptom_text=request.text,
        top_k=request.top_k
    )

    return results
