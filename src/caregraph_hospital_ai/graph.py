from langgraph.graph import StateGraph, START, END
from caregraph_hospital_ai.schemas import HospitalState
from caregraph_hospital_ai.nodes.intake import intake_validation
from caregraph_hospital_ai.nodes.triage import triage_demo, emergency_escalation
from caregraph_hospital_ai.nodes.summary_agent import summary_agent
from caregraph_hospital_ai.nodes.differential_agent import differential_agent
from caregraph_hospital_ai.nodes.medication_safety_agent import medication_safety_agent
from caregraph_hospital_ai.nodes.report_agent import report_agent
from caregraph_hospital_ai.routing import route_after_triage

def build_graph():
    builder = StateGraph(HospitalState)
    builder.add_node("intake_validation", intake_validation)
    builder.add_node("triage_demo", triage_demo)
    builder.add_node("emergency_escalation", emergency_escalation)
    builder.add_node("summary_agent", summary_agent)
    builder.add_node("differential_agent", differential_agent)
    builder.add_node("medication_safety_agent", medication_safety_agent)
    builder.add_node("report_agent", report_agent)
    builder.add_edge(START, "intake_validation")
    builder.add_edge("intake_validation", "triage_demo")
    builder.add_conditional_edges(
        "triage_demo", route_after_triage,
        {"emergency_escalation": "emergency_escalation", "summary_agent": "summary_agent"},
    )
    builder.add_edge("summary_agent", "differential_agent")
    builder.add_edge("differential_agent", "medication_safety_agent")
    builder.add_edge("medication_safety_agent", "report_agent")
    builder.add_edge("report_agent", END)
    builder.add_edge("emergency_escalation", END)
    return builder.compile()

graph = build_graph()

def run_analysis(payload: dict) -> dict:
    result = graph.invoke({**payload, "trace": [], "safety_flags": []})
    for key, default in [
        ("summary", ""), ("key_context", ""), ("differential", []),
        ("safety_flags", []), ("medication_note", ""), ("draft_report", {}),
        ("trace", []), ("missing_information", []),
    ]:
        result.setdefault(key, default)
    return result
