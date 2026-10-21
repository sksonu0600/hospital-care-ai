from caregraph_hospital_ai.schemas import HospitalState
from caregraph_hospital_ai.services.demo_rules import detect_demo_red_flags

def triage_demo(state: HospitalState) -> dict:
    return {
        "emergency_flags": detect_demo_red_flags(state),
        "trace": list(state.get("trace", [])) + ["triage_demo"],
    }

def emergency_escalation(state: HospitalState) -> dict:
    flags = list(state.get("emergency_flags", []))
    return {
        "summary": (
            "A demo keyword rule was triggered. This is not a validated triage decision. "
            "A real system must route potential emergencies to qualified staff using approved protocols."
        ),
        "safety_flags": flags + [
            "Demo escalation path triggered; this application does not contact emergency services."
        ],
        "review_required": True,
        "trace": list(state.get("trace", [])) + ["emergency_escalation"],
    }
