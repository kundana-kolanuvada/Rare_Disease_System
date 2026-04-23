import os
import json
from langchain.tools import tool
from typing import List, Dict, Any
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from app.agent_graph.llm import get_llm, get_fast_llm
from app.agent_graph.tools import disease_vector_search_tool
from app.models.schemas import DiseaseMatch

llm = get_llm()
fast_llm = get_fast_llm()

# --- Subagent 0: Extraction Agent ---
from app.services.extractor import extract_structured_symptoms_rag

@tool
def call_extraction_agent(raw_text: str) -> str:
    """
    Expert at extracting and normalizing medical symptoms.
    """
    print("\n[DEBUG] Supervisor -> Extraction Agent: Starting extraction...")
    extracted = extract_structured_symptoms_rag(raw_text)
    print(f"[DEBUG] Extraction Agent -> Finished. Symptoms found: {len(extracted)}")
    # Just return the joined symptoms, no prefix
    return ", ".join(extracted) if extracted else "No clear symptoms found."

# --- Subagent 1: Symptom Analysis Agent ---
symptom_subagent = create_agent(
    model=fast_llm, 
    tools=[disease_vector_search_tool],
    system_prompt="""You are the Symptom Analysis Expert. 
    1. Call 'disease_vector_search_tool' once.
    2. Respond ONLY with the EXACT list provided by the tool. 
    3. DO NOT add diseases that were not in the tool's output.
    4. DO NOT summarize. Provide the raw list with ORPHA codes and scores.
    """
)


@tool
def call_symptom_agent(structured_symptoms: str) -> str:
    """
    Expert in finding initial disease matches.
    """
    print(f"\n[DEBUG] Supervisor -> Symptom Agent: Finding matches for: {structured_symptoms[:50]}...")
    result = symptom_subagent.invoke(
        {"messages": [HumanMessage(content=f"Find top 15 matches for: {structured_symptoms}")]},
        config={"recursion_limit": 30}
    )
    print("[DEBUG] Symptom Agent -> Finished matching.")
    return result['messages'][-1].content


# --- Subagent 2: Clinical Reasoning Agent ---
from app.agent_graph.tools import deterministic_clinical_scorer_tool

clinical_subagent = create_agent(
    model=fast_llm,
    tools=[deterministic_clinical_scorer_tool],
    system_prompt="""You are the Clinical Refinement Expert.
    
    1. Call 'deterministic_clinical_scorer_tool' ONCE.
    2. Pass the list of diseases and patient profile exactly as provided.
    3. Respond ONLY with the tool's raw output.
    """
)

@tool
def call_clinical_reasoning_agent(matches_data: str, patient_info: str = "") -> str:
    """
    Expert in clinical refinement.
    """
    print("\n[DEBUG] Supervisor -> Clinical Reasoning Agent: Refining matches...")
    result = clinical_subagent.invoke(
        {"messages": [HumanMessage(content=f"Refine: {matches_data}\n\nProfile: {patient_info}")]},
        config={"recursion_limit": 30}
    )
    print("[DEBUG] Clinical Reasoning Agent -> Finished refinement.")
    return result['messages'][-1].content

# --- Subagent 3: Clinical Analysis Expert (Merged Evidence + Recommendations) ---
@tool
def call_evidence_agent(top_matches: str, patient_info: str) -> str:
    """
    Expert in gathering medical evidence, explaining diagnostic reasoning, 
    and providing actionable next steps (tests, referrals, red flags).
    """
    print("\n[DEBUG] Supervisor -> Evidence Agent: Generating final analysis...")
    prompt = f"""
    You are the Senior Clinical Analyst for Atlas Dx. 
    Review these top diagnostic suggestions: {top_matches}

    Patient Info:
    {patient_info}
    
    TASK:
    1. For each disease, provide key diagnostic criteria.
    2. Explain why this patient's symptoms fit, but DO NOT assume the patient has undergone tests or has genetic mutations unless they are explicitly listed in the 'Patient Info' section.
    3. If a gene is associated with the disease but not found in the patient, state it as a "Potential target for testing" rather than something the patient "has".
    4. Provide actionable recommendations (tests, specialists, red flags).

    FORMAT INSTRUCTIONS:
    Return ONLY valid JSON.
    
    IMPORTANT: The 'top_matches' input contains scores as decimals (e.g., 0.85). 
    You MUST convert these to a 0-100 percentage scale (e.g., 85.0) for the final "score" field.
    
    You MUST return your response as a JSON object with these exact keys:

    1. "report_text": A cohesive narrative summary of the clinical findings.
    2. "structured_results": A list of objects, each containing:
       - "name": Disease name
       - "score": Match percentage
       - "explanation": A brief, plain-language description of what the disease is.
       - "evidence": Detailed explanation of why this patient's symptoms match this disease.
       - "recommendations": {{
            "tests": ["Specific test 1", "Specific test 2"],
            "referrals": ["Specialist 1", "Specialist 2"],
            "red_flags": ["Urgent sign 1", "Urgent sign 2"],
            "next_steps": ["Immediate next step 1", "Step 2"]
         }}
    """
    response = llm.invoke(prompt)
    print("[DEBUG] Evidence Agent -> Final report generated.")
    return response.content