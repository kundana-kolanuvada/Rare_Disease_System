import re
import os
import json
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

def preprocess_text(text: str) -> str:
    """Replaces common user terms with more official HPO-like terms."""
    # This map is crucial for bridging conversational language to medical terms
    synonym_map = {
        "easy bruising": "bruising susceptibility",
        "loose joints": "joint mobility",
        "skin tears easily": "skin fragility",
    }
    
    processed_text = text.lower()
    for user_term, official_term in synonym_map.items():
        processed_text = processed_text.replace(user_term, official_term)
    return processed_text

def extract_hpo_ids_from_text(text: str) -> List[str]:
    """
    Extract HPO IDs from raw user text using a balanced word-matching logic
    after text preprocessing.
    """
    processed_text = preprocess_text(text)
    
    # Remove punctuation
    clean_text = re.sub(r'[^\w\s]', '', processed_text)
    text_words = set(clean_text.split())
    found_hpo_ids = set()

    for symptom_name, hpo_ids in dict_symptom_to_id.items():
        symptom_words = set(symptom_name.lower().split())
        
        if not symptom_words:
            continue

        intersection_count = len(symptom_words.intersection(text_words))
        
        if intersection_count == 0:
            continue
        
        # Require at least 50% of the words in the symptom name to match.
        # This is a good balance between being too strict and too noisy.
        match_ratio = intersection_count / len(symptom_words)
        if match_ratio >= 0.5:
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
