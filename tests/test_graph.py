from caregraph_hospital_ai.graph import run_analysis

def test_summary_path_runs_for_synthetic_case():
    result = run_analysis({
        "case_id": "SYNTH-TEST", "age": 34, "symptoms": "cough and fever",
        "history": "not supplied", "medications": "not provided",
        "allergies": "unknown", "labs": "none",
    })
    assert "summary_agent" in result["trace"]
    assert result["differential"]
    assert result["review_required"] is True

def test_demo_red_flag_routes_to_escalation():
    result = run_analysis({
        "case_id": "SYNTH-RED", "age": 52, "symptoms": "severe chest pain",
        "history": "", "medications": "", "allergies": "unknown", "labs": "",
    })
    assert "emergency_escalation" in result["trace"]
    assert result["safety_flags"]
