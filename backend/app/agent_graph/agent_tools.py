import os
import json
from langchain.tools import tool
from typing import List, Dict, Any
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from app.agent_graph.llm import get_llm
from app.agent_graph.tools import disease_vector_search_tool
from app.models.schemas import DiseaseMatch

llm = get_llm()

# --- Subagent 0: Extraction Agent ---
from app.services.extractor import extract_structured_symptoms_rag

@tool
def call_extraction_agent(raw_text: str) -> str:
    """
    Expert at extracting and normalizing medical symptoms from messy patient descriptions.
    Use this tool FIRST to turn raw text into a structured list of medical terms.
    """
    extracted = extract_structured_symptoms_rag(raw_text)
    return ", ".join(extracted) if extracted else "No clear symptoms found."

# --- Subagent 1: Symptom Analysis Agent ---
# We create this agent using create_agent as instructed.
symptom_subagent = create_agent(
    model=llm, 
    tools=[disease_vector_search_tool],
    system_prompt="""You are the Symptom Analysis Expert for Atlas Dx. 
    Your goal is to take normalized medical symptoms and find the top 25 matching diseases.
    
    INSTRUCTIONS:
    1. Use 'disease_vector_search_tool' with the provided symptoms.
    2. Format the output as a concise list of disease names and scores.
    3. Return the results clearly."""
)

@tool
def call_symptom_agent(structured_symptoms: str) -> str:
    """
    Expert in finding initial disease matches from the vector database using structured symptoms.
    Use this tool after symptoms have been extracted and normalized.
    """
    # Synchronous call to the subagent
    result = symptom_subagent.invoke({
        "messages": [HumanMessage(content=f"Find matches for these structured symptoms: {structured_symptoms}")]
    })
    
    # Extract the last message content which should be the final answer
    return result["messages"][-1].content


# --- Subagent 2: Clinical Reasoning Agent ---
from app.agent_graph.tools import deterministic_clinical_scorer_tool

clinical_subagent = create_agent(
    model=llm,
    tools=[deterministic_clinical_scorer_tool],
    system_prompt="""You are the Clinical Refinement Expert for Atlas Dx.
    Your goal is to take a list of diseases and refine their ranking based on patient history.
    
    INSTRUCTIONS:
    1. Call 'deterministic_clinical_scorer_tool' with the matches and patient info to get accurate scores.
    2. Review those scores alongside your medical knowledge of onset, genetics, and inheritance.
    3. Return the final top 5 diseases with a brief clinical reasoning for each.
    """
)

@tool
def call_clinical_reasoning_agent(matches_data: str, patient_info: str) -> str:
    """
    Expert in clinical refinement. Adjusts rankings based on demographics, genetics, and history.
    """
    result = clinical_subagent.invoke({
        "messages": [HumanMessage(content=f"Refine these matches: {matches_data}\n\nPatient Profile: {patient_info}")]
    })
    return result["messages"][-1].content

# --- Subagent 3: Evidence Agent ---
@tool
def call_evidence_agent(top_matches: str) -> str:
    """
    Expert in gathering medical evidence and explaining why specific diseases match the symptoms.
    Provides transparency and reduces the 'black box' nature of the AI.
    """
    prompt = f"""
    Review these top diagnostic suggestions: {top_matches}
    
    For each disease, provide:
    1. Key diagnostic criteria from medical literature (Orphanet, PubMed).
    2. Why this patient's presentation specifically fits these criteria.
    3. Potential differential diagnosis considerations.
    
    FORMAT INSTRUCTIONS:
    You MUST return your response as a JSON object with two keys:
    1. "report_text": A full, professional medical report in markdown.
    2. "structured_results": A list of objects, each with "name", "score", and "evidence_summary".
    
    Ensure the JSON is valid and escaped correctly.
    """
    response = llm.invoke(prompt)
    return response.content
