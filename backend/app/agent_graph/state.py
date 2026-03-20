from typing import TypedDict, List, Optional
from app.models.schemas import DiseaseMatch

class AgentState(TypedDict, total=False):
    symptoms: str
    main_symptoms: Optional[str]
    top_k: int
    age: Optional[int]
    sex: Optional[str]
    ethnicity: Optional[str]
    country: Optional[str]
    family_history: Optional[str]
    family_history_description: Optional[str]
    consanguinity: Optional[str]
    symptom_onset: Optional[str]
    genetic_testing: Optional[str]
    previous_diagnoses: Optional[str]
    previous_tests: Optional[str]

    # Agent-generated
    structured_symptoms: List[str]
    matches: List[DiseaseMatch]         

    # Final output
    final_matches: List[DiseaseMatch] 