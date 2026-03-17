from langchain.tools import tool
from app.services.matcher import match_diseases
from app.models.schemas import DiseaseMatch
from typing import List

@tool
def disease_vector_search_tool(symptom_text: str, top_k: int = 25) -> List[DiseaseMatch]:
    """
    Performs a vector-based similarity search to find rare diseases matching the provided symptom text.

    This tool uses a ChromaDB vector store containing embeddings of rare diseases and their
    associated HPO terms. It identifies diseases with symptom profiles which are most similar to the
    input symptom text.

    Args:
        symptom_text: A detailed description of the patient's symptoms.
        top_k: The number of top matching diseases to retrieve. Defaults to 5.

    Returns:
        A list of DiseaseMatch objects, each containing the disease name,
        a match score (0-1, indicating similarity), and a list of matched HPO IDs.
    """
    raw_matches = match_diseases(symptom_text=symptom_text, top_k=top_k)
    return [DiseaseMatch(**match) for match in raw_matches]
