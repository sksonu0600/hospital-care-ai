
import streamlit as st

from caregraph_hospital_ai.config import APP_NAME
from caregraph_hospital_ai.graph import run_analysis


DEMO_CASES = {
    "Demo A — Cough and fever (synthetic)": {
        "case_id": "SYNTH-001",
        "age": 34,
        "symptoms": "Fictional example: cough and fever for two days.",
        "history": "Not supplied in this synthetic scenario.",
        "medications": "Not provided",
        "allergies": "Unknown",
        "labs": "No laboratory results provided",
    },
    "Demo B — Fatigue (synthetic)": {
        "case_id": "SYNTH-002",
        "age": 46,
        "symptoms": "Fictional example: fatigue and low energy for several weeks.",
        "history": "Not supplied in this synthetic scenario.",
        "medications": "Not provided",
        "allergies": "Unknown",
        "labs": "No laboratory results provided",
    },
    "Demo C — Potential red flag (synthetic)": {
        "case_id": "SYNTH-003",
        "age": 52,
        "symptoms": "Fictional example: severe chest pain.",
        "history": "Not supplied in this synthetic scenario.",
        "medications": "Not provided",
        "allergies": "Unknown",
        "labs": "No laboratory results provided",
    },
}


st.set_page_config(page_title=APP_NAME, page_icon="🏥", layout="wide")
st.title("🏥 CareGraph AI")
st.subheader("AI-Powered Clinical Decision Support")
st.caption("Educational prototype powered by OpenAI and LangGraph.")

if "result" not in st.session_state:
    st.session_state.result = None

if "review_decision" not in st.session_state:
    st.session_state.review_decision = "Pending review"

if "review_notes" not in st.session_state:
    st.session_state.review_notes = ""

with st.sidebar:
    st.header("Workflow")
    st.markdown(
        "1. Intake validation\n"
        "2. Demo red-flag routing\n"
        "3. Clinical summary\n"
        "4. Differential considerations\n"
        "5. Medication-safety flags\n"
        "6. Draft report"
    )
    st.divider()
    st.caption("Synthetic data only. No vector database or RAG.")

mode = st.radio(
    "Case input",
    ["Load synthetic demo", "Enter synthetic case"],
    horizontal=True,
)

if mode == "Load synthetic demo":
    case_name = st.selectbox("Choose case", list(DEMO_CASES))
    data = DEMO_CASES[case_name]
else:
    data = {
        "case_id": "SYNTH-MANUAL",
        "age": 40,
        "symptoms": "",
        "history": "",
        "medications": "",
        "allergies": "",
        "labs": "",
    }

left, right = st.columns(2)

with left:
    st.markdown("### Synthetic Case Context")
    case_id = st.text_input("Synthetic case ID", data["case_id"])
    age = st.number_input(
        "Age", min_value=0, max_value=120, value=int(data["age"])
    )
    symptoms = st.text_area(
        "Symptoms / presenting complaint",
        data["symptoms"],
        height=110,
    )
    history = st.text_area(
        "Medical history", data["history"], height=80
    )

with right:
    st.markdown("### Additional Information")
    medications = st.text_area(
        "Current medications", data["medications"], height=70
    )
    allergies = st.text_area(
        "Allergies", data["allergies"], height=70
    )
    labs = st.text_area(
        "Observations / lab results", data["labs"], height=100
    )
    specialty = st.selectbox(
        "Specialty (label only)",
        [
            "General medicine",
            "Cardiology",
            "Respiratory",
            "Endocrinology",
        ],
    )

if st.button(
    "Run LangGraph analysis",
    type="primary",
    use_container_width=True,
):
    payload = {
        "case_id": case_id,
        "age": age,
        "symptoms": symptoms,
        "history": history,
        "medications": medications,
        "allergies": allergies,
        "labs": labs,
        "specialty": specialty,
    }

    try:
        with st.spinner("Executing graph..."):
            output = run_analysis(payload)

        if not isinstance(output, dict):
            st.session_state.result = None
            st.error(
                "The workflow did not return a dictionary. "
                "Check run_analysis() and the LangGraph nodes."
            )
        else:
            st.session_state.result = output
            st.session_state.review_decision = "Pending review"
            st.session_state.review_notes = ""

    except Exception as exc:
        st.session_state.result = None
        st.error(f"Analysis failed: {exc}")
        st.exception(exc)

result = st.session_state.result

if isinstance(result, dict):
    st.divider()
    st.markdown("## Results")

    trace = result.get("trace") or []
    safety_flags = result.get("safety_flags") or []

    metric_cols = st.columns(3)
    metric_cols[0].metric(
        "Graph nodes executed", len(trace)
    )
    metric_cols[1].metric(
        "Safety flags", len(safety_flags)
    )
    metric_cols[2].metric(
        "Clinician review", st.session_state.review_decision
    )

    tabs = st.tabs(
        [
            "Summary",
            "Differential",
            "Safety",
            "Draft report",
            "Graph trace",
        ]
    )

    # TAB 1: CLINICAL SUMMARY
    with tabs[0]:
        st.markdown("### Clinical Summary")
        st.write(
            result.get("summary") or "No summary available."
        )

        st.markdown("### Additional Context")
        st.write(
            result.get("key_context")
            or "No additional context available."
        )

        missing = result.get("missing_information") or []

        if missing:
            st.markdown("### Missing Information")
            for detail in missing:
                st.warning(detail)

    # TAB 2: DIFFERENTIAL ASSESSMENT
    with tabs[1]:
        st.markdown("### GPT Differential Assessment")

        assessment = result.get("differential_assessment") or {}

        st.write(
            assessment.get(
                "overall_assessment",
                "No assessment available.",
            )
        )

        differential = assessment.get("differential") or []

        if not differential:
            st.info(
                "No differential considerations are available."
            )

        for item in differential:
            if not isinstance(item, dict):
                continue

            with st.container(border=True):
                st.markdown(
                    f"**{item.get('condition', 'Unspecified')}**"
                )
                st.write(
                    item.get("rationale", "No rationale provided.")
                )

                st.caption(
                    "Evidence status: "
                    + str(
                        item.get(
                            "evidence_status",
                            "Not specified",
                        )
                    )
                )

                supporting = (
                    item.get("supporting_findings") or []
                )

                if supporting:
                    st.markdown("**Supporting findings**")
                    for finding in supporting:
                        st.write(f"- {finding}")

                conflicting = (
                    item.get("conflicting_findings") or []
                )

                if conflicting:
                    st.markdown("**Conflicting findings**")
                    for finding in conflicting:
                        st.write(f"- {finding}")

                missing_info = (
                    item.get("missing_information") or []
                )

                if missing_info:
                    st.markdown("**Information Needed**")
                    for detail in missing_info:
                        st.write(f"- {detail}")

        for detail in (
            assessment.get("overall_missing_information") or []
        ):
            st.warning(detail)

        for flag in (
            assessment.get("urgent_review_flags") or []
        ):
            st.error(flag)

        st.caption(
            "GPT-generated possibilities are not confirmed diagnoses "
            "and require qualified clinician review."
        )

    # TAB 3: MEDICATION SAFETY
    with tabs[2]:
        st.markdown("### Medication Safety")

        for flag in safety_flags:
            st.warning(flag)

        if not safety_flags:
            st.info(
                "No safety flags were returned. "
                "This does not establish clinical safety."
            )

        recommendation = (
            result.get("medication_recommendation") or {}
        )
        medication_note = result.get("medication_note") or ""

        if medication_note:
            st.write(medication_note)

        if recommendation:
            st.json(recommendation)
        else:
            st.info(
                "No medication assessment is available."
            )

        st.warning(
            "Educational POC using synthetic data only. "
            "Not validated for clinical use. "
            "Do not use for real-patient diagnosis or treatment."
        )

    # TAB 4: DRAFT REPORT AND SIMULATED REVIEW
    with tabs[3]:
        st.markdown("### Draft Report")
        st.json(result.get("draft_report") or {})

        st.markdown("### Simulated Clinician Review")

        choices = [
            "Pending review",
            "Approved with edits",
            "Rejected",
            "Escalate for further assessment",
        ]

        current_decision = st.session_state.get(
            "review_decision",
            "Pending review",
        )

        if current_decision not in choices:
            current_decision = "Pending review"

        decision = st.selectbox(
            "Review status",
            choices,
            index=choices.index(current_decision),
        )

        notes = st.text_area(
            "Review notes (session-only)",
            value=st.session_state.get("review_notes", ""),
        )

        if st.button("Save simulated review"):
            st.session_state.review_decision = decision
            st.session_state.review_notes = notes
            st.success(
                f"Saved to this Streamlit session: {decision}"
            )

        st.caption(
            "This is not a durable or authenticated clinical approval system."
        )

    # TAB 5: GRAPH TRACE
    with tabs[4]:
        st.markdown("### Executed Graph Nodes")

        if trace:
            for index, node in enumerate(trace, 1):
                st.write(f"{index}. `{node}`")
        else:
            st.info("No graph trace is available.")

elif result is not None:
    st.error(
        "The workflow returned an invalid result. "
        "Check run_analysis() and the LangGraph output."
    )

st.divider()
st.caption(
    "CareGraph AI • Local prototype • Synthetic data only • No RAG"
)
