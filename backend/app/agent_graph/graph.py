from langgraph.graph import StateGraph, END
from app.agent_graph.state import AgentState
from app.agent_graph.tools import disease_vector_search_tool


def disease_search_node(state: AgentState):

    symptom_text = state["symptoms"]
    top_k = state.get("top_k", 5)

    results = disease_vector_search_tool.invoke({
        "symptom_text": symptom_text,
        "top_k": top_k
    })

    return {
        "matched_diseases": results
    }


def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("disease_search", disease_search_node)
    workflow.set_entry_point("disease_search")
    workflow.add_edge("disease_search", END)
    return workflow.compile()


symptom_analysis_graph = build_graph()