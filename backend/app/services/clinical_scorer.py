from typing import List, Dict, Optional
from app.models.schemas import DiseaseMatch

def calculate_clinical_fit(
    disease: DiseaseMatch,
    age: Optional[int],
    sex: Optional[str],
    family_history: Optional[str],
    consanguinity: Optional[str],
    symptom_onset: Optional[str],
    genetic_testing: Optional[str],
    main_symptoms: Optional[str]
) -> float:
    """
    Calculates a 'Clinical Fit' multiplier based on demographics and history.
    """
    multiplier = 1.0
    
    # 1. Age of Onset Match (High Importance)
    if symptom_onset and disease.onset:
        if symptom_onset.lower() in disease.onset.lower():
            multiplier *= 1.5  # Boost from 1.3
        else:
            multiplier *= 0.6  # Penalty from 0.7

    # 2. Genetic Variant Match 
    if genetic_testing and disease.genes:
        # Check if any mentioned gene (e.g., COL1A1) is in the disease metadata
        user_genes = [g.strip().upper() for g in genetic_testing.replace(',', ' ').split()]
        disease_genes = [g.strip().upper() for g in disease.genes.split(',')]
        
        if any(gene in disease_genes for gene in user_genes if gene):
            multiplier *= 4.0 # Huge boost for genetic match

    # 3. Inheritance & Family History
    if disease.inheritance:
        inh = disease.inheritance.lower()
        # Consanguinity (Parents related) -> Boost Recessive diseases
        if consanguinity == "Yes" and "recessive" in inh:
            multiplier *= 1.8
            
        # Family History -> Boost Dominant or X-linked
        if family_history == "Yes":
            if "dominant" in inh:
                multiplier *= 1.6
            elif "x-linked" in inh and sex == "Male":
                multiplier *= 1.8 # Stronger boost for males with X-linked history

    # 4. Main Symptom Weighting (Frequency)
    return multiplier

def refine_matches(
    matches: List[DiseaseMatch],
    age: Optional[int],
    sex: Optional[str],
    family_history: Optional[str],
    consanguinity: Optional[str],
    symptom_onset: Optional[str],
    genetic_testing: Optional[str],
    main_symptoms: Optional[str],
    top_k: int = 5
) -> List[DiseaseMatch]:
    """
    Re-ranks and narrows down the initial wide pool (25) to the final top results.
    """
    refined_list = []
    
    for match in matches:
        multiplier = calculate_clinical_fit(
            match, age, sex, family_history, 
            consanguinity, symptom_onset, 
            genetic_testing, main_symptoms
        )
        
        # Calculate new score (Stay as decimal)
        raw_score = match.match_score * multiplier
        match.match_score = round(min(0.99, raw_score), 4)
        refined_list.append(match)
    
    # Re-sort based on refined score
    refined_list.sort(key=lambda x: x.match_score, reverse=True)
    
    # Return final requested amount
    return refined_list[:top_k]
