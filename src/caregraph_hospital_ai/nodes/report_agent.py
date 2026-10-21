from caregraph_hospital_ai.schemas import HospitalState

def report_agent(state: HospitalState) -> dict:
    report = {
        "case_id": state.get("case_id"),
        "summary": state.get("summary", ""),
        "differential": state.get("differential", []),
        "safety_flags": state.get("safety_flags", []),
        "medication_note": state.get("medication_note", ""),
        "review_required": True,
        "disclaimer": "Synthetic educational output only; not a diagnosis or prescription.",
    }
    return {
        "draft_report": report,
        "trace": list(state.get("trace", [])) + ["report_agent"],
    }
