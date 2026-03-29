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
    1. Use 'disease_vector_search_tool' ONCE with the provided symptoms.
    2. Format the output as a concise list of disease names and scores.
    3. Return the results clearly. Do not repeat the search if you already have results."""
)

@tool
def call_symptom_agent(structured_symptoms: str) -> str:
    """
    Expert in finding initial disease matches from the vector database using structured symptoms.
    Use this tool after symptoms have been extracted and normalized.
    """
    # Synchronous call to the subagent with explicit recursion limit
    result = symptom_subagent.invoke(
        {"messages": [HumanMessage(content=f"Find matches for these structured symptoms: {structured_symptoms}")]},
        config={"recursion_limit": 50}
    )
    
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
    1. Call 'deterministic_clinical_scorer_tool' ONCE with the matches and patient info to get accurate scores.
    2. Review those scores alongside your medical knowledge of onset, genetics, and inheritance.
    3. Return the final top 5 diseases with a brief clinical reasoning for each.
    4. Once you have the refined scores and reasoning, STOP and provide your final response. Do not call the tool again if you already have the refined scores.
    """
)

@tool
def call_clinical_reasoning_agent(matches_data: str, patient_info: str = "") -> str:
    """
    Expert in clinical refinement. Adjusts rankings based on demographics, genetics, and history.
    """
    # Increase recursion limit to 50 and specify it in config
    result = clinical_subagent.invoke(
        {"messages": [HumanMessage(content=f"Refine these matches: {matches_data}\n\nPatient Profile: {patient_info}")]},
        config={"recursion_limit": 50}
    )
    return result["messages"][-1].content

# --- Subagent 3: Clinical Analysis Expert (Merged Evidence + Recommendations) ---
@tool
def call_evidence_agent(top_matches: str, patient_info: str) -> str:
    """
    Expert in gathering medical evidence, explaining diagnostic reasoning, 
    and providing actionable next steps (tests, referrals, red flags).
    """
    prompt = f"""
    You are the Senior Clinical Analyst for Atlas Dx. 
    Review these top diagnostic suggestions: {top_matches}

    Patient Info:
    {patient_info}
    
    TASK:
    1. For each disease, provide key diagnostic criteria and explain why it fits this patient.
    2. Suggest specific differential diagnosis considerations.
    3. Provide actionable recommendations (tests, specialists, red flags).

    FORMAT INSTRUCTIONS:
    Return ONLY valid JSON. Do not include any text before or after the JSON.
    You MUST return your response as a JSON object with these exact keys:
    
    1. "report_text": A cohesive narrative summary of the clinical findings.
    2. "structured_results": A list of objects, each containing:
       - "name": Disease name
       - "score": Match percentage (use the provided scores)
       - "evidence_summary": 2-3 sentences on clinical fit.
    3. "recommendations": {{
        "tests": ["Specific test 1", "Specific test 2"],
        "referrals": ["Specialist 1", "Specialist 2"],
        "red_flags": ["Urgent sign 1", "Urgent sign 2"],
        "next_steps": ["Immediate next step 1", "Step 2"]
    }}
    """
    response = llm.invoke(prompt)
    return response.content