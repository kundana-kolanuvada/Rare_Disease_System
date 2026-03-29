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
    Your mission is to find the most likely rare disease diagnosis and provide evidence-based reasoning.

    STEP-BY-STEP WORKFLOW:
    1. Call 'call_extraction_agent' with the patient's raw symptoms to get normalized medical terms.
    2. Call 'call_symptom_agent' with the normalized terms to get 25 initial matches.
    3. Call 'call_clinical_reasoning_agent' with those matches and the patient's history.
    4. Call 'call_evidence_agent' with top_matches and patient_info.
    5. Return the final structured JSON output from the evidence agent.

    IMPORTANT RULES:
    - Always wait for the result of the previous step before moving to the next.
    - Do NOT skip any step.
    - Do NOT generate final answers yourself — rely on tools.
    - Ensure the final output is valid JSON (no extra text outside JSON).
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

    # --- Invoke supervisor agent with increased recursion limit ---
    response = atlas_dx_supervisor.invoke(
        {"messages": [HumanMessage(content=patient_description)]},
        config={"recursion_limit": 100}
    )

    last_msg_content = response["messages"][-1].content

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

    # --- Fallback ---
    return {
        "final_matches_text": last_msg_content,
        "structured_results": [],
        "recommendations": {}
    }