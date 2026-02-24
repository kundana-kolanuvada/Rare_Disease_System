from pydantic import BaseModel,Field
from typing import List, Optional

class SymptomRequest(BaseModel):
    # Core input
    symptoms: str = Field(..., description="Raw text description of patient symptoms.")
    top_k: int = 5

    # Patient demographics
    age: Optional[int] = None
    sex: Optional[str] = None
    ethnicity: Optional[str] = None
    country: Optional[str] = None

    # Medical history
    family_history: Optional[str] = Field(None, alias="familyHistory")
    family_history_description: Optional[str] = Field(None, alias="familyHistoryDescription")
    symptom_onset: Optional[str] = Field(None, alias="symptomOnset")
    previous_diagnoses: Optional[str] = Field(None, alias="previousDiagnoses")
    previous_tests: Optional[str] = Field(None, alias="previousTests")

    class Config:
        populate_by_name = True # Allows using camelCase from frontend and converting to snake_case

class MatchRequest(BaseModel):
    hpo_ids: List[str]
    top_k: int = 5

class MatchedTerm(BaseModel):
    hpo_id: str
    hpo_name: str

class DiseaseMatch(BaseModel):
    disease_name: str
    match_score: float
    matched_terms: List[MatchedTerm]
 