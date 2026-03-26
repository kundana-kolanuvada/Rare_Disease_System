import os
os.environ["LANGCHAIN_TRACING_V2"] = "false"
from langchain.tools import tool
from app.services.matcher import match_diseases
from typing import List

@tool
def disease_vector_search_tool(symptom_text: str, top_k: int = 25) -> str:
    """
    Performs a vector-based similarity search to find rare diseases matching the provided symptom text.
    Returns a concise string of the top matching diseases and their similarity scores.
    """
    raw_matches = match_diseases(symptom_text=symptom_text, top_k=top_k)
    
    # Format as a concise string to save significant tokens
    # LangGraph's create_agent factory creates very large internal states, 
    # so we MUST keep tool outputs as small as possible.
    results = []
    for m in raw_matches[:top_k]:
        results.append(f"- {m['disease_name']} (ORPHA:{m['orpha_code']}, Score: {m['match_score']})")
        
    return "\n".join(results) if results else "No matches found."
