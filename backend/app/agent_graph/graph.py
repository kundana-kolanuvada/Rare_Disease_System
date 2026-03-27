from langchain.agents import create_agent
from app.agent_graph.agent_tools import call_extraction_agent, call_symptom_agent, call_clinical_reasoning_agent, call_evidence_agent
from app.agent_graph.llm import get_llm
from langchain_core.messages import HumanMessage

llm = get_llm()

# --- Main Agent: The Supervisor ---
# Created with create_agent and using the subagent tools.
atlas_dx_supervisor = create_agent(
    model=llm,
    tools=[call_extraction_agent, call_symptom_agent, call_clinical_reasoning_agent, call_evidence_agent],
    system_prompt="""You are the Lead Diagnostic Supervisor for Atlas Dx.
    Your mission is to find the most likely rare disease diagnosis and provide evidence-based reasoning.
    
    STEP-BY-STEP WORKFLOW:
    1. Call 'call_extraction_agent' with the patient's raw symptoms to get normalized medical terms.
    2. Call 'call_symptom_agent' with the normalized terms to get 25 initial matches.
    3. Call 'call_clinical_reasoning_agent' with those matches and the patient's history.
    4. Call 'call_evidence_agent' with the top refined matches to gather supporting evidence.
    5. Present the final diagnosis clearly in a professional medical report format, including the evidence.
    
    Synchronous Operation: Always wait for the result of the previous agent before calling the next one."""
)

import json
import re

def invoke_atlas_dx(input_data: dict):
    # Combine patient info for the supervisor
    patient_description = f"""
    Symptoms: {input_data.get('symptoms')}
    Demographics: Age {input_data.get('age')}, Sex {input_data.get('sex')}
    History: Onset {input_data.get('symptom_onset')}, Family History {input_data.get('family_history')}, 
    Consanguinity {input_data.get('consanguinity')}, Genetic testing {input_data.get('genetic_testing')}
    """
    
    # We call .invoke() on the supervisor agent
    response = atlas_dx_supervisor.invoke({
        "messages": [HumanMessage(content=patient_description)]
    })
    
    last_msg_content = response["messages"][-1].content
    
    # Attempt to extract JSON from the last message (sometimes LLMs wrap JSON in code blocks)
    try:
        json_match = re.search(r'\{.*\}', last_msg_content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return {
                "final_matches_text": data.get("report_text", last_msg_content),
                "structured_results": data.get("structured_results", [])
            }
    except Exception:
        pass

    # Fallback if parsing fails
    return {
        "final_matches_text": last_msg_content,
        "structured_results": []
    }
