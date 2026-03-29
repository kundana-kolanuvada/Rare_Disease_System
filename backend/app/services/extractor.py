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
        structured_symptoms = json.loads(llm_output)

        if not isinstance(structured_symptoms, list):
            raise ValueError("LLM did not return a JSON list.")
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
