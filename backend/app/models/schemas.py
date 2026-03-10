from pydantic import BaseModel, Field
from typing import List, Optional

class SymptomRequest(BaseModel):
    # Core input
    symptoms: str = Field(..., description="Raw text description of patient symptoms.")
    main_symptoms: Optional[str] = Field(None, alias="mainSymptoms")
    top_k: int = 25 # Increased for wide-pool search

    # Patient demographics
    age: Optional[int] = None
    sex: Optional[str] = None
    ethnicity: Optional[str] = None
    country: Optional[str] = "N/A"

    # Medical history
    family_history: Optional[str] = Field(None, alias="familyHistory")
    family_history_description: Optional[str] = Field(None, alias="familyHistoryDescription")
    consanguinity: Optional[str] = "No"
    symptom_onset: Optional[str] = Field(None, alias="symptomOnset")
    genetic_testing: Optional[str] = Field(None, alias="geneticTesting")
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
    
    # Optional clinical metadata fields
    orpha_code: Optional[str] = None
    onset: Optional[str] = None
    inheritance: Optional[str] = None
    prevalence: Optional[str] = None
    genes: Optional[str] = None
