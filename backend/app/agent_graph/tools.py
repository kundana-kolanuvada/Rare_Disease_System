import os
os.environ["LANGCHAIN_TRACING_V2"] = "false"
from langchain.tools import tool
from app.services.matcher import match_diseases
from typing import List

from app.services.clinical_scorer import refine_matches
from app.models.schemas import DiseaseMatch
import re

@tool
def disease_vector_search_tool(symptom_text: str, top_k: int = 25) -> str:
...
    return "\n".join(results) if results else "No matches found."

@tool
def deterministic_clinical_scorer_tool(matches_json: str, patient_info: str) -> str:
    """
    Calculates rule-based clinical fit scores for a list of diseases based on 
    patient demographics (age, sex, onset, inheritance).
    Use this to get grounded, non-hallucinated scores for clinical refinement.
    """
    # Parse matches
    initial_matches = []
    lines = matches_json.strip().split('\n')
    for line in lines:
        match = re.search(r'- (.*?) \(ORPHA:(\d+), Score: ([\d.]+)\)', line)
        if match:
            disease_name, orpha_code, score = match.groups()
            initial_matches.append(DiseaseMatch(
                disease_name=disease_name,
                orpha_code=orpha_code,
                match_score=float(score),
                matched_terms=[]
            ))

    # Parse patient info
    def get_val(pattern, text):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else None

    age = get_val(r"Age (\d+)", patient_info)
    sex = get_val(r"Sex (\w+)", patient_info)
    onset = get_val(r"Onset ([\w\s]+),", patient_info)
    fam_hist = get_val(r"Family History (\w+),", patient_info)
    consang = get_val(r"Consanguinity (\w+),", patient_info)
    genetics = get_val(r"Genetic testing ([\w\s,]+)", patient_info)

    if not initial_matches:
        return "Error: No initial matches provided."

    refined = refine_matches(
        matches=initial_matches,
        age=int(age) if age and age.isdigit() else None,
        sex=sex,
        family_history=fam_hist,
        consanguinity=consang,
        symptom_onset=onset,
        genetic_testing=genetics,
        main_symptoms=None,
        top_k=15
    )

    results = ["DETERMINISTIC RE-RANKING:"]
    for m in refined:
        results.append(f"- {m.disease_name} (New Score: {m.match_score})")
    
    return "\n".join(results)
