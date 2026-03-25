from langgraph.graph import StateGraph, END
from app.agent_graph.state import AgentState
from app.agent_graph.tools import disease_vector_search_tool
from app.services.extractor import extract_structured_symptoms_rag
from app.services.clinical_scorer import refine_matches
from app.agent_graph.llm import get_llm

llm = get_llm()

def symptom_analysis_agent(state: AgentState):
    raw_symptoms = state["symptoms"]

    structured = extract_structured_symptoms_rag(raw_symptoms)

    if structured:
        symptoms_to_search = ", ".join(structured)
    else:
        symptoms_to_search = raw_symptoms

    results = disease_vector_search_tool.invoke({
        "symptom_text": symptoms_to_search,
        "top_k": 25
    })

    state["structured_symptoms"] = structured
    state["matches"] = results
    return state

def clinical_reasoning_agent(state: AgentState):
    matches = state.get("matches", [])

    final_matches = refine_matches(
        matches=matches,
        age=state.get("age"),
        sex=state.get("sex"),
        family_history=state.get("family_history"),
        consanguinity=state.get("consanguinity"),
        symptom_onset=state.get("symptom_onset"),
        genetic_testing=state.get("genetic_testing"),
        main_symptoms=state.get("symptoms"),
        top_k=5
    )

    state["final_matches"] = final_matches
    return state

def supervisor_agent(state: AgentState):

    prompt = f"""
You are a medical workflow supervisor.

Decide which agent to call next.

Available:
- symptom_agent → if symptoms need processing
- clinical_agent → if matches exist but need refinement
- end → if final results ready

Rules:
- If no matches → symptom_agent
- If matches exist but no final_matches → clinical_agent
- If final_matches exist → end

State:
{state}

Return ONLY one word:
symptom_agent
clinical_agent
end
"""

    decision = llm.invoke(prompt).content.strip().lower()

    return {
        "next_step": decision
    }

def build_graph():
    workflow = StateGraph(AgentState)

    # Nodes
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("symptom_agent", symptom_analysis_agent)
    workflow.add_node("clinical_agent", clinical_reasoning_agent)

    # Entry
    workflow.set_entry_point("supervisor")

    # Conditional routing
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["next_step"],
        {
            "symptom_agent": "symptom_agent",
            "clinical_agent": "clinical_agent",
            "end": END
        }
    )

    # Flow
    workflow.add_edge("symptom_agent", "supervisor")
    workflow.add_edge("clinical_agent", END)

    return workflow.compile()


symptom_analysis_graph = build_graph()