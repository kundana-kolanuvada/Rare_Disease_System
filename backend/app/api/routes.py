from fastapi import APIRouter
from app.services.matcher import match_diseases
from app.models.schemas import MatchRequest, DiseaseMatch
from typing import List

router = APIRouter()

@router.post("/match", response_model=List[DiseaseMatch])
def match_endpoint(request: MatchRequest):
    results = match_diseases(
        user_hpo_ids=request.hpo_ids,
        top_k=request.top_k
    )
    return results
