import os
import json
from typing import List, Set, Dict
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

# --- RAG-based Symptom Extraction ---

# Initialize the Groq LLM
llm = ChatGroq(temperature=0, model_name="openai/gpt-oss-120b", groq_api_key=os.getenv("GROQ_API_KEY"))

# Define the prompt for symptom extraction
extraction_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a medical assistant specialized in extracting and normalizing symptoms from patient descriptions. "
            "Your goal is to identify all key symptoms and medical findings, and then normalize them into a concise, "
            "standardized list of medical terms. Output the result as a JSON list of strings."
            "\nExample Input: 'My 23-year-old daughter has loose joints, gets bruised easily, and her skin tears if you scratch it.'"
            "\nExample Output: ['joint hypermobility', 'easy bruising', 'skin fragility']"
            "\nEnsure the output is always a valid JSON list of strings, even if no symptoms are found (return an empty list)."
        ),
        ("human", "{symptom_text}"),
    ]
)

# Create the extraction chain
extraction_chain = extraction_prompt | llm | StrOutputParser()

def extract_structured_symptoms_rag(symptom_text: str) -> List[str]:
    """
    Extracts and normalizes symptoms from raw patient text using a RAG-based LLM approach.

    Args:
        symptom_text: The raw, unstructured text describing the patient's symptoms.

    Returns:
        A list of normalized symptom strings.
    """
    if not symptom_text:
        return []

    try:
        # Invoke the LLM chain to extract symptoms
        llm_output = extraction_chain.invoke({"symptom_text": symptom_text})
        
        # Attempt to parse the JSON output
        structured_symptoms = json.loads(llm_output)

        if not isinstance(structured_symptoms, list):
            raise ValueError("LLM did not return a JSON list.")

        # Ensure all elements in the list are strings
        if not all(isinstance(s, str) for s in structured_symptoms):
            raise ValueError("All elements in the JSON list must be strings.")

        return structured_symptoms
    except json.JSONDecodeError:
        print(f"Warning: LLM output could not be parsed as JSON: {llm_output}")
        return [] # Return empty list on parsing error
    except ValueError as e:
        print(f"Warning: Invalid LLM output format: {e} - Output: {llm_output}")
        return [] # Return empty list on format error
    except Exception as e:
        print(f"An unexpected error occurred during symptom extraction: {e}")
        return []


# --- Old Extraction Logic (commented out) ---
# from app.services.normalizer import normalize_hpo_ids

# """
# Extractor service:
# Converts raw user symptom text into a list of HPO IDs
# using simple substring matching.
# """

# def load_diseases(json_path):
#     with open(json_path, 'r', encoding='utf-8') as f:
#         return json.load(f)

# def map_symptoms_to_id() -> Dict[str, Set[str]]:
#     """
#     Builds a mapping:
#     symptom_name (lowercase) -> set of HPO IDs
#     """
#     symptom_map = dict()

#     for disease in DISEASES:
#         for term in disease["hpo_terms"]:
#             symptom_name = term["hpo_name"].lower()
#             hpo_id = term["hpo_id"]

#             if symptom_name not in symptom_map:
#                 symptom_map[symptom_name] = set()

#             symptom_map[symptom_name].add(hpo_id)

#     return symptom_map

# def preprocess_text(text: str) -> str:
#     """Replaces common user terms with more official HPO-like terms."""
#     synonym_map = {
#         "easy bruising": "bruising susceptibility",
#         "loose joints": "joint mobility",
#         "skin tears easily": "skin fragility",
#     }
    
#     processed_text = text.lower()
#     for user_term, official_term in synonym_map.items():
#         processed_text = processed_text.replace(user_term, official_term)
#     return processed_text

# def extract_hpo_ids_from_text(text: str) -> List[str]:
#     """
#     Extract HPO IDs from raw user text using a balanced word-matching logic
#     after text preprocessing.
#     """
#     processed_text = preprocess_text(text)
    
#     clean_text = re.sub(r'[^\w\s]', '', processed_text)
#     text_words = set(clean_text.split())
#     found_hpo_ids = set()

#     for symptom_name, hpo_ids in dict_symptom_to_id.items():
#         symptom_words = set(symptom_name.lower().split())
        
#         if not symptom_words:
#             continue

#         intersection_count = len(symptom_words.intersection(text_words))
        
#         if intersection_count == 0:
#             continue
        
#         match_ratio = intersection_count / len(symptom_words)
#         if match_ratio >= 0.5:
#             found_hpo_ids.update(hpo_ids)
    
#     return normalize_hpo_ids(list(found_hpo_ids))


# BASE_DIR = os.path.dirname(
#     os.path.dirname(
#         os.path.dirname(__file__)
#     )
# )

# DATA_PATH = os.path.join(BASE_DIR, "data", "diseases.json")

# DISEASES = load_diseases(DATA_PATH)

# dict_symptom_to_id = map_symptoms_to_id()
