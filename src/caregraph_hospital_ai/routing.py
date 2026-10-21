from caregraph_hospital_ai.schemas import HospitalState

def route_after_triage(state: HospitalState) -> str:
    return "emergency_escalation" if state.get("emergency_flags") else "summary_agent"
