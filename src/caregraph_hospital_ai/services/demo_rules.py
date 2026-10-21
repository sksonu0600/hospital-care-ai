from caregraph_hospital_ai.schemas import HospitalState

def detect_demo_red_flags(state: HospitalState) -> list[str]:
    text = f"{state.get('symptoms', '')} {state.get('labs', '')}".lower()
    terms = ("severe chest pain", "difficulty breathing", "unconscious", "stroke symptoms")
    return [
        f"Demo keyword matched: '{term}'. Seek immediate assessment by qualified staff."
        for term in terms if term in text
    ]

def make_demo_differential(state: HospitalState) -> list[dict[str, str]]:
    text = f"{state.get('symptoms', '')} {state.get('labs', '')}".lower()
    items = []
    if any(t in text for t in ("fever", "cough", "sore throat")):
        items.append({
            "condition": "Infectious or inflammatory cause (broad category)",
            "rationale": "Symptoms alone cannot establish a cause; clinical examination and appropriate testing are required.",
            "evidence_status": "Insufficient for diagnosis",
        })
    if any(t in text for t in ("fatigue", "tiredness", "weakness")):
        items.append({
            "condition": "Multiple possible causes of fatigue",
            "rationale": "Fatigue is nonspecific; history, sleep, medicines and clinician-selected investigations may be relevant.",
            "evidence_status": "Insufficient for diagnosis",
        })
    if not items:
        items.append({
            "condition": "No specific condition inferred by demo rules",
            "rationale": "The demo avoids inferring a diagnosis from limited text.",
            "evidence_status": "Not assessed",
        })
    return items
