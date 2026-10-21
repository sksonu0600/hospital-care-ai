
from langchain_core.messages import SystemMessage, HumanMessage

from caregraph_hospital_ai.schemas import HospitalState
from caregraph_hospital_ai.llm import get_llm


def summary_agent(state: HospitalState) -> dict:
    llm = get_llm()

    response = llm.invoke([
        SystemMessage(content="""
You are a clinical documentation assistant.

Summarize only the patient information supplied.
Do not invent symptoms, examination findings, diagnoses, or test results.
Explicitly identify missing information and uncertainty.
Do not prescribe medicines.
This output requires review by a qualified clinician.
"""),
        HumanMessage(content=f"""
Age: {state.get('age', 'Not provided')}
Symptoms: {state.get('symptoms', 'Not provided')}
History: {state.get('history', 'Not provided')}
Current medications: {state.get('medications', 'Not provided')}
Allergies: {state.get('allergies', 'Unknown')}
Laboratory results: {state.get('labs', 'Not provided')}

Produce a concise clinical summary and key context.
""")
    ])

    return {
        "summary": response.content,
        "key_context": (
            f"Current medicines: {state.get('medications') or 'Not provided'}. "
            f"Allergies: {state.get('allergies') or 'Unknown'}."
        ),
        "trace": list(state.get("trace", [])) + ["summary_agent_openai"],
    }
