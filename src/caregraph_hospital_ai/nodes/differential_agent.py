
import json

from langchain_core.messages import SystemMessage, HumanMessage

from caregraph_hospital_ai.llm import get_llm
from caregraph_hospital_ai.schemas import HospitalState


def differential_agent(state: HospitalState) -> dict:
    llm = get_llm()

    response = llm.invoke([
        SystemMessage(content="""
You are a clinical differential-diagnosis decision-support assistant.

Analyze the patient information and suggest possible conditions for review
by a qualified clinician.

Requirements:
1. Use only the supplied patient information.
2. Never claim that a possible condition is confirmed.
3. Explain which findings support each possibility.
4. Identify contradictory findings when information is available.
5. Identify missing information and investigations a clinician may consider.
6. Do not invent symptoms, test results, medical history, or evidence.
7. Do not invent probabilities or confidence percentages.
8. If the information is insufficient, explicitly state that.
9. Do not prescribe medicines or recommend treatment regimens.
10. Consider urgent warning signs, but do not claim that this model
    replaces a validated triage process.

Return ONLY valid JSON using this structure:

{
  "overall_assessment": "Brief assessment of available information",
  "differential": [
    {
      "condition": "Possible condition or broad clinical category",
      "rationale": "Why it may be considered",
      "supporting_findings": ["Finding from supplied data"],
      "conflicting_findings": ["Conflicting evidence or not provided"],
      "evidence_status": "Limited information",
      "missing_information": ["Information needed for assessment"]
    }
  ],
  "overall_missing_information": ["Missing clinical information"],
  "urgent_review_flags": ["Potential concern, if supported by input"],
  "clinician_review_required": true
}

Use evidence_status values such as:
- "Supported by supplied findings"
- "Limited information"
- "Insufficient information"

If no meaningful differential can be generated, return an empty
differential list and explain why in overall_assessment.
"""),
        HumanMessage(content=f"""
PATIENT INFORMATION

Age: {state.get('age', 'Not provided')}
Symptoms: {state.get('symptoms', 'Not provided')}
Medical history: {state.get('history', 'Not provided')}
Current medications: {state.get('medications', 'Not provided')}
Allergies: {state.get('allergies', 'Unknown')}
Laboratory results: {state.get('labs', 'Not provided')}

Generate a cautious differential assessment for clinician review.
Do not treat missing information as evidence that a condition is absent.
""")
    ])

    try:
        result = json.loads(response.content)

        if not isinstance(result, dict):
            raise ValueError("Expected a JSON object")

        differential = result.get("differential", [])

        if not isinstance(differential, list):
            raise ValueError("Differential must be a list")

        # Validate the fields expected by the current UI.
        validated = []

        for item in differential:
            if not isinstance(item, dict):
                continue

            condition = item.get("condition")
            rationale = item.get("rationale")

            if not isinstance(condition, str) or not isinstance(rationale, str):
                continue

            validated.append({
                "condition": condition,
                "rationale": rationale,
                "supporting_findings": item.get("supporting_findings", []),
                "conflicting_findings": item.get("conflicting_findings", []),
                "evidence_status": item.get(
                    "evidence_status", "Limited information"
                ),
                "missing_information": item.get("missing_information", []),
            })

        result["differential"] = validated

    except (json.JSONDecodeError, ValueError, TypeError):
        result = {
            "overall_assessment": (
                "The model response could not be validated. "
                "No reliable differential output is available."
            ),
            "differential": [],
            "overall_missing_information": [],
            "urgent_review_flags": [],
            "clinician_review_required": True,
        }

    return {
        "differential": result["differential"],
        "differential_assessment": result,
        "trace": list(state.get("trace", []))
                  + ["differential_agent_openai"],
    }
