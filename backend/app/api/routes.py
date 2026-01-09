from fastapi import APIRouter
from app.services.matcher import match_diseases
from app.services.extractor import extract_hpo_ids_from_text
from app.models.schemas import MatchRequest, DiseaseMatch, SymptomRequest
from typing import List

router = APIRouter()

@router.post("/match", response_model=List[DiseaseMatch])
def match_endpoint(request: MatchRequest):
    results = match_diseases(
        user_hpo_ids=request.hpo_ids,
        top_k=request.top_k
    )
    return results
 
@router.post("/api/v1/diagnose", response_model=List[DiseaseMatch])
def diagnose_endpoint(request: SymptomRequest):
    hpo_ids = extract_hpo_ids_from_text(request.text)

    results = match_diseases(
        user_hpo_ids=hpo_ids,
        top_k=request.top_k
    )

    return results