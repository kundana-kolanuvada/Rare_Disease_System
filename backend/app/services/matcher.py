import json
import os

"""
This file is used to find the match percentage between the user symptoms and diseases symptoms 
that are available in diseases.json.
"""

def load_diseases(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


#Using jaccard similarity to check similarity between 2 diseases.
def jaccard_similarity(set_a, set_b):
    intersection = set_a & set_b
    union = set_a | set_b
    if not union:
        return 0.0
    return len(intersection) / len(union)

def match_diseases(user_hpo_ids, top_k = 5):

    if not user_hpo_ids:
        return []
    user_set = set(user_hpo_ids)
    results = []

    for disease in DISEASES:
        disease_hpo_ids = {
            term["hpo_id"] for term in disease.get("hpo_terms", [])
        }
        
        score = jaccard_similarity(user_set, disease_hpo_ids)
        if score > 0:
            results.append({
                "disease_name": disease["disease_name"],
                "match_score": round(score, 3),
                "matched_hpo_ids": list(user_set & disease_hpo_ids)
            })
        
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:top_k]


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

DATA_PATH = os.path.join(BASE_DIR, "data", "diseases.json")

DISEASES = load_diseases(DATA_PATH)



    