from typing import TypedDict, List
from app.models.schemas import DiseaseMatch

class AgentState(TypedDict):
    """
    Represents the state of our agent. It's a dictionary that will be passed between nodes in the graph.
    """
    # Inputs from the user
    symptoms: str
    top_k: int
    age: Optional[int]
    sex: Optional[str]
    ethnicity: Optional[str]
    country: Optional[str]
    family_history: Optional[str]
    family_history_description: Optional[str]
    symptom_onset: Optional[str]
    previous_diagnoses: Optional[str]
    previous_tests: Optional[str]

    # Agent-generated data
    structured_symptoms: List[str]
    matched_diseases: List[DiseaseMatch]
