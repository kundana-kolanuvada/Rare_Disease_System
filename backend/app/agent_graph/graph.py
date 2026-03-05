from langgraph.graph import StateGraph, END
from app.agent_graph.state import AgentState
from app.agent_graph.tools import disease_vector_search_tool
from app.services.extractor import extract_structured_symptoms_rag


def symptom_extraction_node(state: AgentState):
    """
    Node to extract structured symptoms from raw text.
    """
    raw_symptoms = state["symptoms"]
    structured_symptoms = extract_structured_symptoms_rag(raw_symptoms)
    
    return {
        "structured_symptoms": structured_symptoms
    }


def disease_search_node(state: AgentState):
    """
    Node to search for diseases based on extracted symptoms.
    """
    # Use structured symptoms if available, otherwise fallback to raw text
    structured = state.get("structured_symptoms", [])
    if structured:
        symptoms_to_search = ", ".join(structured)
    else:
        symptoms_to_search = state["symptoms"]
        
    top_k = state.get("top_k", 5)

    results = disease_vector_search_tool.invoke({
        "symptom_text": symptoms_to_search,
        "top_k": top_k
    })

    return {
        "matched_diseases": results
    }


def build_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("extract_symptoms", symptom_extraction_node)
    workflow.add_node("disease_search", disease_search_node)
    
    # Set edges
    workflow.set_entry_point("extract_symptoms")
    workflow.add_edge("extract_symptoms", "disease_search")
    workflow.add_edge("disease_search", END)
    
    return workflow.compile()


symptom_analysis_graph = build_graph()
