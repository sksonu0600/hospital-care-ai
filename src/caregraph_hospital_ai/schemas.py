from typing import Any
from typing_extensions import TypedDict

class HospitalState(TypedDict, total=False):
    case_id: str
    age: int
    symptoms: str
    history: str
    medications: str
    allergies: str
    labs: str
    specialty: str
    missing_information: list[str]
    emergency_flags: list[str]
    summary: str
    key_context: str
    differential: list[dict[str, str]]
    safety_flags: list[str]
    medication_note: str
    review_required: bool
    draft_report: dict[str, Any]
    trace: list[str]
    medication_recommendation: dict[str, Any]
    medication_note: str
    safety_flags: list[str]
    review_required: bool
    differential_assessment: dict[str, Any]