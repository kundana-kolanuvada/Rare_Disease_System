from langgraph.graph import StateGraph, END
from app.agent_graph.state import AgentState
from app.agent_graph.tools import disease_vector_search_tool
from app.services.extractor import extract_structured_symptoms_rag
from app.services.clinical_scorer import refine_matches


def symptom_analysis_agent(state: AgentState):
    """
    Agent that handles symptom understanding + disease matching.
    """

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

    return {
        "structured_symptoms": structured,
        "matches": results
    }


def clinical_reasoning_agent(state: AgentState):
    """
    Agent that refines results using clinical metadata.
    """

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

    return {
        "final_matches": final_matches
    }


def supervisor_agent(state: AgentState):
    """
    Decides which agent to call next.
    """

    # If no matches yet → go to symptom agent
    if not state.get("matches"):
        return "symptom_agent"

    # If matches exist but no final results → go to clinical agent
    if state.get("matches") and not state.get("final_matches"):
        return "clinical_agent"

    return "end"


def build_graph():
    workflow = StateGraph(AgentState)

    # Add agents
    workflow.add_node("symptom_agent", symptom_analysis_agent)
    workflow.add_node("clinical_agent", clinical_reasoning_agent)

    # Entry point
    workflow.set_entry_point("symptom_agent")

    # After symptom agent → decide next
    workflow.add_conditional_edges(
        "symptom_agent",
        supervisor_agent,
        {
            "clinical_agent": "clinical_agent",
            "end": END
        }
    )

    # After clinical agent → end
    workflow.add_edge("clinical_agent", END)

    return workflow.compile()


symptom_analysis_graph = build_graph()