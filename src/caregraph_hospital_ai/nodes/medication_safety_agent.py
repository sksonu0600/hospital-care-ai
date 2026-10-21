
import json

from langchain_core.messages import SystemMessage, HumanMessage

from caregraph_hospital_ai.llm import get_llm
from caregraph_hospital_ai.schemas import HospitalState


def medication_safety_agent(state: HospitalState) -> dict:
    llm = get_llm()

    response = llm.invoke(
        [
            SystemMessage(
                content="""
You are a clinical medication decision-support assistant.

Your role is to help a qualified clinician consider medication-related
questions using only the supplied synthetic case information.

Rules:
- Never claim that a diagnosis is confirmed.
- Do not invent patient information, drug references, or evidence.
- Do not present an unverified medication as definitely appropriate.
- Consider age, symptoms, allergies, current medicines, medical history,
  and available laboratory results.
- Identify possible contraindications, interactions, and missing safety data.
- If information is insufficient, say so explicitly.
- Do not recommend an exact dose or treatment regimen.
- Do not recommend antibiotics or prescription medicines without sufficient
  clinical context.
- Distinguish general options from patient-specific conclusions.
- Require independent verification by a qualified clinician.

Return valid JSON with these keys:
summary, options_to_consider, rationale, safety_concerns,
missing_information, clinician_review_required.

Mention a medicine or medicine category only when there is a defensible
basis. Otherwise explain what information is needed first.
"""
            ),
            HumanMessage(
                content=f"""
PATIENT CASE

Age: {state.get('age', 'Not provided')}
Symptoms: {state.get('symptoms', 'Not provided')}
Medical history: {state.get('history', 'Not provided')}
Current medicines: {state.get('medications', 'Not provided')}
Allergies: {state.get('allergies', 'Unknown')}
Laboratory results: {state.get('labs', 'Not provided')}

Generate cautious medication decision-support information for clinician
review. Do not treat missing information as a negative finding.
"""
            ),
        ]
    )

    try:
        recommendation = json.loads(response.content)

        if not isinstance(recommendation, dict):
            raise ValueError("Expected a JSON object.")

    except (json.JSONDecodeError, TypeError, ValueError):
        recommendation = {
            "summary": "The model output could not be validated.",
            "options_to_consider": [],
            "rationale": "No reliable medication assessment is available.",
            "safety_concerns": ["Structured output validation failed."],
            "missing_information": [
                "Qualified clinician assessment is required."
            ],
            "clinician_review_required": True,
        }

    # Normalize existing safety flags to a list.
    existing_flags = state.get("safety_flags") or []

    if isinstance(existing_flags, str):
        existing_flags = [existing_flags]
    elif not isinstance(existing_flags, list):
        existing_flags = []

    # Add safety concerns returned by the medication agent.
    new_flags = recommendation.get("safety_concerns") or []

    if isinstance(new_flags, str):
        new_flags = [new_flags]
    elif not isinstance(new_flags, list):
        new_flags = []

    combined_flags = existing_flags + new_flags

    return {
        "medication_recommendation": recommendation,
        "medication_note": recommendation.get(
            "summary",
            "Medication review is required.",
        ),
        "safety_flags": combined_flags,
        "trace": list(state.get("trace") or [])
        + ["medication_safety_agent_openai"],
    }
