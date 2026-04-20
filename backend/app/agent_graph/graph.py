from langchain.agents import create_agent
from app.agent_graph.agent_tools import (
    call_extraction_agent,
    call_symptom_agent,
    call_clinical_reasoning_agent,
    call_evidence_agent
)
from app.agent_graph.llm import get_llm
from langchain_core.messages import HumanMessage
import json
import re

llm = get_llm()

# --- Main Agent: The Supervisor ---
atlas_dx_supervisor = create_agent(
    model=llm,
    tools=[
        call_extraction_agent,
        call_symptom_agent,
        call_clinical_reasoning_agent,
        call_evidence_agent
    ],
    system_prompt="""You are the Lead Diagnostic Supervisor for Atlas Dx.
    
    STRICT SEQUENTIAL WORKFLOW:
    1. Call 'call_extraction_agent' with raw symptoms. WAIT for result.
    2. Call 'call_symptom_agent' ONLY after you have the extracted symptoms.
    3. Call 'call_clinical_reasoning_agent' ONLY after you have the initial matches.
    4. Call 'call_evidence_agent' ONLY after you have the refined matches.
    5. FINISH: Once you have the JSON from 'call_evidence_agent', you MUST STOP and provide that JSON as your final answer.

    IMPORTANT RULES:
    - DO NOT call tools in parallel.
    - DO NOT call a tool until you have the required input from the previous tool.
    - DO NOT summarize the JSON. Your final answer must be ONLY the JSON object.
    """
)


def invoke_atlas_dx(input_data: dict):
    """
    Entry point for Atlas Dx diagnostic pipeline
    """

    # --- Build patient description ---
    patient_description = f"""
    Symptoms: {input_data.get('symptoms')}
    Demographics: Age {input_data.get('age')}, Sex {input_data.get('sex')}
    History: Onset {input_data.get('symptom_onset')}, Family History {input_data.get('family_history')}, 
    Consanguinity {input_data.get('consanguinity')}, Genetic testing {input_data.get('genetic_testing')}
    """

    print("\n[DEBUG] Supervisor -> Starting diagnostic pipeline...")
    response = atlas_dx_supervisor.invoke(
        {"messages": [HumanMessage(content=patient_description)]},
        config={"recursion_limit": 90}
    )

    last_msg_content = response["messages"][-1].content
    print(f"\n[DEBUG] Supervisor -> Pipeline Finished. Raw output length: {len(last_msg_content)}")

    # --- Extract JSON safely ---
    try:
        cleaned = last_msg_content.strip()
        cleaned = cleaned.replace("```json", "").replace("```", "")

        json_match = re.search(r'\{[\s\S]*\}', cleaned)

        if json_match:
            data = json.loads(json_match.group())

            return {
                "final_matches_text": data.get("report_text", last_msg_content),
                "structured_results": data.get("structured_results", []),
                "recommendations": data.get("recommendations", {})
            }
    except Exception as e:
        print("JSON parsing failed:", e)

    return {
        "final_matches_text": last_msg_content,
        "structured_results": [],
        "recommendations": {}
    }