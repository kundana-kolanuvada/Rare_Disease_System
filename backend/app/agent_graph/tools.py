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
    """
    Search for rare diseases in the vector database based on patient symptoms.
    Returns a formatted string of top matches including ORPHA codes and similarity scores.
    """
    matches = match_diseases(symptom_text, top_k=top_k)
    
    results = []
    for m in matches:
        # We include all metadata in the string so the next agent can parse it if needed
        # Format: - Disease Name (ORPHA:123, Score: 0.85, Onset: Infancy, Inheritance: Autosomal dominant, Genes: GDI1)
        metadata_parts = [
            f"ORPHA:{m['orpha_code']}",
            f"Score: {m['match_score']}"
        ]
        if m.get('onset'): metadata_parts.append(f"Onset: {m['onset']}")
        if m.get('inheritance'): metadata_parts.append(f"Inheritance: {m['inheritance']}")
        if m.get('genes'): metadata_parts.append(f"Genes: {m['genes']}")
        
        metadata_str = ", ".join(metadata_parts)
        results.append(f"- {m['disease_name']} ({metadata_str})")
    
    return "\n".join(results) if results else "No matches found."

@tool
def deterministic_clinical_scorer_tool(matches_json: str, patient_info: str) -> str:
    """
    Calculates rule-based clinical fit scores for a list of diseases based on 
    patient demographics (age, sex, onset, inheritance).
    Use this to get grounded, non-hallucinated scores for clinical refinement.
    """
    # Parse matches using a more robust regex that handles optional metadata
    initial_matches = []
    lines = matches_json.strip().split('\n')
    for line in lines:
        # Example line: - Disease Name (ORPHA:123, Score: 0.85, Onset: Infancy, Inheritance: Autosomal dominant, Genes: GDI1)
        name_match = re.search(r'- (.*?) \(ORPHA:(\d+), Score: ([\d.]+)', line)
        if name_match:
            disease_name, orpha_code, score = name_match.groups()
            
            # Extract optional metadata from the parenthetical part
            onset = re.search(r'Onset: (.*?),', line) or re.search(r'Onset: (.*?)\)', line)
            inheritance = re.search(r'Inheritance: (.*?),', line) or re.search(r'Inheritance: (.*?)\)', line)
            genes = re.search(r'Genes: (.*?),', line) or re.search(r'Genes: (.*?)\)', line)

            initial_matches.append(DiseaseMatch(
                disease_name=disease_name,
                orpha_code=orpha_code,
                match_score=float(score),
                matched_terms=[],
                onset=onset.group(1).strip() if onset else None,
                inheritance=inheritance.group(1).strip() if inheritance else None,
                genes=genes.group(1).strip() if genes else None
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
