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
        # User onset is a single value like "Infancy"
        # Disease onset is a comma-separated string like "Infancy, Childhood"
        if symptom_onset.lower() in disease.onset.lower():
            multiplier *= 1.3  # 30% boost for matching the expected onset window
        else:
            multiplier *= 0.7  # 30% penalty for onset mismatch

    # 2. Genetic Variant Match (Extremely High Importance - The "Kill Switch")
    if genetic_testing and disease.genes:
        # Check if any mentioned gene (e.g., COL1A1) is in the disease metadata
        user_genes = [g.strip().upper() for g in genetic_testing.replace(',', ' ').split()]
        disease_genes = [g.strip().upper() for g in disease.genes.split(',')]
        
        if any(gene in disease_genes for gene in user_genes if gene):
            multiplier *= 2.0  # Double the score if the specific gene matches

    # 3. Inheritance & Family History
    if disease.inheritance:
        inh = disease.inheritance.lower()
        # Consanguinity (Parents related) -> Boost Recessive diseases
        if consanguinity == "Yes" and "recessive" in inh:
            multiplier *= 1.4
            
        # Family History -> Boost Dominant or X-linked
        if family_history == "Yes":
            if "dominant" in inh:
                multiplier *= 1.3
            elif "x-linked" in inh and sex == "Male":
                multiplier *= 1.5 # Stronger boost for males with X-linked history

    # 4. Main Symptom Weighting (Frequency)
    # Note: In a production version, we would parse the symptom-specific frequency here.
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
        
        # Calculate new score
        match.match_score = round(min(0.99, match.match_score * multiplier), 4)
        refined_list.append(match)
    
    # Re-sort based on refined score
    refined_list.sort(key=lambda x: x.match_score, reverse=True)
    
    # Return final requested amount (usually top 5)
    return refined_list[:top_k]
