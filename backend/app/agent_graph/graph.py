from langgraph.graph import StateGraph, END
from app.agent_graph.state import AgentState
from app.agent_graph.tools import disease_vector_search_tool

# Node: Disease Search
def disease_search_node(state: AgentState):
    """
    This node receives symptoms from state,
    calls the disease search tool,
    and returns results.
    """
    symptoms = state["symptoms"]
    results = disease_vector_search_tool(symptoms)
    return {
        "results": results
    }

# Build the Graph
def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("disease_search", disease_search_node)
    workflow.set_entry_point("disease_search")
    workflow.add_edge("disease_search", END)
    return workflow.compile()

symptom_analysis_graph = build_graph()