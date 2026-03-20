from app.agent_graph.graph import symptom_analysis_graph
def run_test_case(title, input_data):
    print(f"\n===== {title} =====")

    result = symptom_analysis_graph.invoke(input_data)

    final_matches = result.get("final_matches", [])

    for i, disease in enumerate(final_matches, 1):
        print(f"{i}. {disease.disease_name} → Score: {disease.match_score}")

if __name__ == "__main__":
    
    # ✅ Test 1: Only symptoms
    test_1 = {
        "symptoms": "bone pain, frequent fractures, blue sclera"
    }

    # ✅ Test 2: With clinical data
    test_2 = {
        "symptoms": "bone pain, frequent fractures, blue sclera",
        "age": 5,
        "sex": "Male",
        "family_history": "Yes",
        "consanguinity": "No",
        "symptom_onset": "Infancy",
        "genetic_testing": "COL1A1"
    }

    run_test_case("Test 1: Symptoms Only", test_1)
    run_test_case("Test 2: With Clinical Data", test_2)