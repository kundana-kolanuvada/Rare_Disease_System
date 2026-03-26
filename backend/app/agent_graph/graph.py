from langchain.agents import create_agent
from app.agent_graph.agent_tools import call_symptom_agent, call_clinical_reasoning_agent
from app.agent_graph.llm import get_llm
from langchain_core.messages import HumanMessage

llm = get_llm()

# --- Main Agent: The Supervisor ---
# Created with create_agent and using the subagent tools.
atlas_dx_supervisor = create_agent(
    model=llm,
    tools=[call_symptom_agent, call_clinical_reasoning_agent],
    system_prompt="""You are the Lead Diagnostic Supervisor for Atlas Dx.
    Your mission is to find the most likely rare disease diagnosis.
    
    STEP-BY-STEP WORKFLOW:
    1. Call 'call_symptom_agent' with the patient's symptoms to get 25 initial matches.
    2. Call 'call_clinical_reasoning_agent' with those matches and the patient's history.
    3. Present the final diagnosis clearly in a professional medical report format.
    
    Synchronous Operation: Wait for the result of the first agent before calling the next one."""
)

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
    
    # Get the last message from the result
    return {
        "final_matches_text": response["messages"][-1].content
    }
