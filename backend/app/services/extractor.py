import json
import os
from typing import List, Set, Dict

from app.services.normalizer import normalize_hpo_ids


"""
Extractor service:
Converts raw user symptom text into a list of HPO IDs
using simple substring matching.
"""

def load_diseases(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def map_symptoms_to_id() -> Dict[str, Set[str]]:
    """
    Builds a mapping:
    symptom_name (lowercase) -> set of HPO IDs
    """
    symptom_map = dict()

    for disease in DISEASES:
        for term in disease["hpo_terms"]:
            symptom_name = term["hpo_name"].lower()
            hpo_id = term["hpo_id"]

            if symptom_name not in symptom_map:
                symptom_map[symptom_name] = set()

            symptom_map[symptom_name].add(hpo_id)

    return symptom_map

def extract_hpo_ids_from_text(text: str) -> List[str]:
    """
    Extract HPO IDs from raw user text using substring matching.
    """
    text = text.lower()
    found_hpo_ids = set()

    for symptom_name, hpo_ids in dict_symptom_to_id.items():
        if symptom_name in text:
            found_hpo_ids.update(hpo_ids)
    
    return normalize_hpo_ids(list(found_hpo_ids))


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

DATA_PATH = os.path.join(BASE_DIR, "data", "diseases.json")

DISEASES = load_diseases(DATA_PATH)

dict_symptom_to_id = map_symptoms_to_id()
