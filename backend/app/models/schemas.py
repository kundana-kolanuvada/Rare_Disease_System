from pydantic import BaseModel
from typing import List

class MatchRequest(BaseModel):
    hpo_ids: List[str]
    top_k: int = 5

class DiseaseMatch(BaseModel):
    disease_name: str
    match_score: float
    matched_hpo_ids: List[str]
