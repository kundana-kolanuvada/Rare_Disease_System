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
from app.services.clinical_scorer import refine_matches
from app.models.schemas import DiseaseMatch, MatchedTerm
import re

@tool
def call_clinical_reasoning_agent(matches_data: str, patient_info: str) -> str:
    """
    Expert in clinical refinement. Takes the initial 25 disease matches and adjusts their rankings 
    based on patient demographics like age of onset, genetics, and family history.
    Returns the final top 5 diseases.
    """
    # 1. Parse matches_data string back into DiseaseMatch objects for deterministic scoring
    # This is a heuristic parser to bridge the gap between tool-output-string and structured function
    initial_matches = []
    lines = matches_data.strip().split('\n')
    for line in lines:
        match = re.search(r'- (.*?) \(ORPHA:(\d+), Score: ([\d.]+)\)', line)
        if match:
            disease_name, orpha_code, score = match.groups()
            initial_matches.append(DiseaseMatch(
                disease_name=disease_name,
                orpha_code=orpha_code,
                match_score=float(score),
                matched_terms=[] # HPO terms not needed for clinical fit
            ))

    # 2. Extract patient metadata for the deterministic scorer
    # In a production system, we'd pass this as a structured dict
    def get_val(pattern, text):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else None

    age = get_val(r"Age (\d+)", patient_info)
    sex = get_val(r"Sex (\w+)", patient_info)
    onset = get_val(r"Onset ([\w\s]+),", patient_info)
    fam_hist = get_val(r"Family History (\w+),", patient_info)
    consang = get_val(r"Consanguinity (\w+),", patient_info)
    genetics = get_val(r"Genetic testing ([\w\s,]+)", patient_info)

    # 3. Get deterministic refined matches
    if initial_matches:
        deterministic_refined = refine_matches(
            matches=initial_matches,
            age=int(age) if age and age.isdigit() else None,
            sex=sex,
            family_history=fam_hist,
            consanguinity=consang,
            symptom_onset=onset,
            genetic_testing=genetics,
            main_symptoms=None,
            top_k=10 # Give LLM top 10 to choose from
        )
        
        grounded_context = "DETERMINISTIC SCORING RESULTS (Rule-based):\n"
        for i, m in enumerate(deterministic_refined):
            grounded_context += f"{i+1}. {m.disease_name} (Revised Score: {m.match_score})\n"
    else:
        grounded_context = "No initial matches found to refine."

    # 4. Final LLM Refinement
    prompt = f"""
    Review these initial matches: {matches_data}
    Patient Profile: {patient_info}
    
    {grounded_context}
    
    INSTRUCTIONS:
    1. Re-evaluate the diseases based on the deterministic scores AND your medical knowledge.
    2. Ensure the top 5 suggestions strictly align with the patient's 'Symptom Onset' and 'Inheritance Pattern'.
    3. If 'Genetic testing' mentions a gene, heavily prioritize diseases associated with that gene.
    4. Provide the final top 5 suggestions with brief clinical reasoning for each.
    """
    response = llm.invoke(prompt)
    return response.content

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
