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

# --- Subagent 1: Symptom Analysis Agent ---
# We create this agent using create_agent as instructed.
symptom_subagent = create_agent(
    model=llm, 
    tools=[disease_vector_search_tool],
    system_prompt="""You are the Symptom Analysis Expert for Atlas Dx. 
    Your goal is to take raw patient symptoms and find the top 25 matching diseases.
    
    INSTRUCTIONS:
    1. Use 'disease_vector_search_tool' directly with the patient's symptoms.
    2. Format the output as a concise list of disease names and scores.
    3. Return the results clearly."""
)

@tool
def call_symptom_agent(symptoms: str) -> str:
    """
    Expert in extracting medical symptoms and finding initial disease matches from the vector database.
    Use this tool first to get the initial pool of 25 diseases.
    """
    # Synchronous call to the subagent
    result = symptom_subagent.invoke({
        "messages": [HumanMessage(content=f"Analyze these symptoms and find matches: {symptoms}")]
    })
    
    # Extract the last message content which should be the final answer
    return result["messages"][-1].content


# --- Subagent 2: Clinical Reasoning Agent ---
# Wrapping this as a tool for the main supervisor
@tool
def call_clinical_reasoning_agent(matches_data: str, patient_info: str) -> str:
    """
    Expert in clinical refinement. Takes the initial 25 disease matches and adjusts their rankings 
    based on patient demographics like age of onset, genetics, and family history.
    Returns the final top 5 diseases.
    """
    prompt = f"""
    Review these initial matches: {matches_data}
    Patient Profile: {patient_info}
    
    Refine the ranking based on how well the patient's age and history match each disease's typical profile.
    Provide the final top 5 suggestions with brief reasoning for each.
    """
    response = llm.invoke(prompt)
    return response.content
