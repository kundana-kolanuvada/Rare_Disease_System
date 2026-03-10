from app.services.clinical_scorer import refine_matches
from app.models.schemas import DiseaseMatch, MatchedTerm

def mock_disease(name, score, onset="", inheritance="", genes=""):
    """Helper to create a mock DiseaseMatch object."""
    return DiseaseMatch(
        disease_name=name,
        match_score=score,
        matched_terms=[MatchedTerm(hpo_id="HP:0001", hpo_name="Sample Symptom")],
        onset=onset,
        inheritance=inheritance,
        genes=genes
    )

def run_test():
    print("=== CLINICAL SCORER VERIFICATION ===\n")

    # TEST 1: THE GENE MATCH (THE "KILL SWITCH")
    print("Scenario 1: Genetic Variant Match")
    # Disease has gene COL1A1. Initial symptom match is low (0.4)
    d1 = mock_disease("Osteogenesis Imperfecta", 0.4, genes="COL1A1, COL1A2")
    
    # User provides COL1A1 in genetic testing
    results = refine_matches([d1], age=20, sex="Female", family_history="No", 
                             consanguinity="No", symptom_onset="Adult", 
                             genetic_testing="COL1A1", main_symptoms="")
    
    print(f"  Disease: {d1.disease_name}")
    print(f"  Initial Score: 0.4")
    print(f"  Refined Score: {results[0].match_score} (Expected: ~0.8 due to 2.0x boost)")
    print("-" * 40)

    # TEST 2: THE AGE PENALTY
    print("Scenario 2: Age of Onset Mismatch")
    # Disease only starts in Infancy. Initial match is high (0.9)
    d2 = mock_disease("Infantile Metabolic Syndrome", 0.9, onset="Infancy, Neonatal")
    
    # User is an Adult (25 years old)
    results = refine_matches([d2], age=25, sex="Male", family_history="No", 
                             consanguinity="No", symptom_onset="Adult", 
                             genetic_testing="", main_symptoms="")
    
    print(f"  Disease: {d2.disease_name}")
    print(f"  Initial Score: 0.9")
    print(f"  Refined Score: {results[0].match_score} (Expected: < 0.7 due to 0.7x penalty)")
    print("-" * 40)

    # TEST 3: CONSANGUINITY BOOST
    print("Scenario 3: Consanguinity + Recessive Inheritance")
    # Disease is Autosomal Recessive. Initial match is moderate (0.6)
    d3 = mock_disease("Rare Recessive Disorder", 0.6, inheritance="Autosomal recessive")
    
    # User reports parents are related
    results = refine_matches([d3], age=5, sex="Female", family_history="No", 
                             consanguinity="Yes", symptom_onset="Childhood", 
                             genetic_testing="", main_symptoms="")
    
    print(f"  Disease: {d3.disease_name}")
    print(f"  Initial Score: 0.6")
    print(f"  Refined Score: {results[0].match_score} (Expected: ~0.84 due to 1.4x boost)")
    print("-" * 40)

if __name__ == "__main__":
    run_test()
