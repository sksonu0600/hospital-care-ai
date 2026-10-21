from caregraph_hospital_ai.schemas import HospitalState

def intake_validation(state: HospitalState) -> dict:
    missing = []
    for key, label in [
        ("symptoms", "Presenting symptoms"),
        ("history", "Relevant medical history"),
        ("medications", "Current medication list"),
        ("allergies", "Allergy status"),
    ]:
        if not str(state.get(key, "")).strip():
            missing.append(f"{label} not provided; do not assume it is negative.")
    if not str(state.get("case_id", "")).strip():
        missing.append("Case reference is missing.")
    return {
        "missing_information": missing,
        "trace": list(state.get("trace", [])) + ["intake_validation"],
    }
