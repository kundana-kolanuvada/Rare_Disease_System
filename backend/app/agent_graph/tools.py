import os
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from langchain.tools import tool
from app.services.matcher import match_diseases
from typing import List
from app.services.clinical_scorer import refine_matches
from app.models.schemas import DiseaseMatch
import re


# --- Tool 1: Vector Search ---
@tool
def disease_vector_search_tool(symptom_text: str, top_k: int = 15) -> str:
    """
    Search for rare diseases in the vector database based on patient symptoms.
    Returns a formatted string of top matches including ORPHA codes and similarity scores.
    """
    matches = match_diseases(symptom_text, top_k=top_k)

    results = []
    for m in matches:
        metadata_parts = [
            f"ORPHA:{m['orpha_code']}",
            f"Score: {m['match_score']}"
        ]

        if m.get('onset'):
            metadata_parts.append(f"Onset: {m['onset']}")
        if m.get('inheritance'):
            metadata_parts.append(f"Inheritance: {m['inheritance']}")
        if m.get('genes'):
            metadata_parts.append(f"Genes: {m['genes']}")

        metadata_str = ", ".join(metadata_parts)
        results.append(f"- {m['disease_name']} ({metadata_str})")

    return "\n".join(results) if results else "No matches found."


# --- Tool 2: Deterministic Clinical Scorer ---
@tool
def deterministic_clinical_scorer_tool(matches_json: str, patient_info: str) -> str:
    """
    Calculates rule-based clinical fit scores for a list of diseases.
    """
    if not matches_json:
        return "Error: Empty matches input."

    initial_matches = []
    
    # --- Try parsing as JSON or Python list first (Llama-3.1-8b often sends one of these) ---
    clean_input = matches_json.strip()
    if clean_input.startswith('[') or 'id' in clean_input or 'orpha_code' in clean_input:
        try:
            import ast
            import json
            
            # Extract the list/array part
            list_match = re.search(r'\[.*\]', clean_input, re.DOTALL)
            if list_match:
                match_str = list_match.group()
                try:
                    # Try as standard JSON first
                    data = json.loads(match_str)
                except json.JSONDecodeError:
                    # Fallback to ast.literal_eval for Python-style strings (single quotes)
                    data = ast.literal_eval(match_str)
                
                if isinstance(data, list):
                    for item in data:
                        orpha = str(item.get('orpha_code') or item.get('id', '')).replace('ORPHA:', '')
                        name = item.get('disease_name') or item.get('name', 'Unknown')
                        score = item.get('match_score') or item.get('score', 0.5)
                        initial_matches.append(
                            DiseaseMatch(
                                disease_name=name,
                                orpha_code=orpha,
                                match_score=float(score),
                                matched_terms=[]
                            )
                        )
        except Exception as e:
            # If both fail, we still have the regex fallback
            pass

    # --- Fallback to Regex for line-by-line format ---
    if not initial_matches:
        lines = clean_input.split('\n')
        for line in lines:
            # Flexible regex to catch name, orpha code, and score in almost any format
            orpha_match = re.search(r'ORPHA:?(\d+)', line, re.IGNORECASE)
            # Look for any number between 0 and 100 as the score
            score_match = re.search(r'(?:Score|Match|Probability):?\s*([\d.]+)', line, re.IGNORECASE)
            # Disease name is usually at the start of the line
            name_match = re.search(r'[-*]\s*([^(\n]+)', line)

            if orpha_match:
                orpha_code = orpha_match.group(1)
                disease_name = name_match.group(1).strip() if name_match else "Unknown Disease"
                
                # Extract score, convert to decimal if it's a percentage
                raw_s = score_match.group(1) if score_match else "0.5" # Keep 0.5 only as last resort
                f_score = float(raw_s)
                if f_score > 1: f_score = f_score / 100.0
                
                initial_matches.append(
                    DiseaseMatch(
                        disease_name=disease_name,
                        orpha_code=orpha_code,
                        match_score=f_score,
                        matched_terms=[]
                    )
                )

    if not initial_matches:
        return f"Error: Could not parse matches from: {matches_json[:100]}"

    def get_val(pattern, text):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else None

    # Robust patient info parsing (handles JSON or text)
    age = get_val(r"age[\s\":]*(\d+)", patient_info)
    sex = get_val(r"sex[\s\":]*(\w+)", patient_info)
    onset = get_val(r"onset[\s\":]*([^,\n\"}]+)", patient_info)
    fam_hist = get_val(r"(?:family_history|Family History)[\s\":]*([^,\n\"}]+)", patient_info)
    consang = get_val(r"(?:consanguinity|Consanguinity)[\s\":]*([^,\n\"}]+)", patient_info)
    genetics = get_val(r"(?:genetic_testing|Genetic testing)[\s\":]*([^,\n\"}]+)", patient_info)

    def safe_strip(val):
        return val.strip() if val else None

    # Apply safe strip to all
    age = safe_strip(age)
    sex = safe_strip(sex)
    onset = safe_strip(onset)
    fam_hist = safe_strip(fam_hist)
    consang = safe_strip(consang)
    genetics = safe_strip(genetics)


    refined = refine_matches(
        matches=initial_matches,
        age=int(age) if age and age.isdigit() else None,
        sex=sex,
        family_history=fam_hist,
        consanguinity=consang,
        symptom_onset=onset,
        genetic_testing=genetics,
        main_symptoms=None,
        top_k=5
    )

    results = ["DETERMINISTIC RE-RANKING:"]
    for m in refined:
        results.append(f"- {m.disease_name} (New Score: {m.match_score})")

    return "\n".join(results)