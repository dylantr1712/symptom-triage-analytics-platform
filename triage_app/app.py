from __future__ import annotations

import os
import uuid

import streamlit as st

from triage_app.extractor import OpenAIExtractionClient, StubExtractionClient, SymptomExtractor
from triage_app.models import PipelineStatus, SessionEvent
from triage_app.pipeline import run_triage_pipeline
from triage_app.storage import build_storage_from_env


def build_extractor() -> SymptomExtractor:
    if os.getenv("OPENAI_API_KEY"):
        return SymptomExtractor(OpenAIExtractionClient())
    return SymptomExtractor(StubExtractionClient())


def render_app() -> None:
    st.set_page_config(page_title="Symptom Triage Platform", layout="centered")
    st.title("Symptom Triage Platform")
    st.caption("Rule-based triage with AI extraction only. This is not a diagnosis tool.")

    user_text = st.text_area(
        "Describe your symptoms",
        placeholder="Example: I am 42 and I have had severe chest pain and shortness of breath since this morning.",
        height=160,
    )

    if st.button("Assess symptoms", type="primary") and user_text.strip():
        extractor = build_extractor()
        storage = build_storage_from_env()
        session_id = str(uuid.uuid4())

        try:
            extraction_result = extractor.extract(user_text)
            pipeline_result = run_triage_pipeline(extraction_result.payload)
            event = SessionEvent.create(
                session_id=session_id,
                raw_text=user_text,
                extraction=extraction_result.payload,
                validation=pipeline_result.validation,
                normalized=pipeline_result.normalized,
                decision=pipeline_result.decision,
            )
            storage.write_event(event)
        except ValueError as exc:
            st.error(f"Extraction failed: {exc}")
            return
        except RuntimeError as exc:
            st.error(str(exc))
            return
        except Exception as exc:
            st.error(f"Storage failed: {exc}")
            return

        st.subheader("Result")
        if pipeline_result.status == PipelineStatus.COMPLETE and pipeline_result.decision:
            decision = pipeline_result.decision
            st.success(decision.headline)
            st.write(decision.explanation)
            st.write(f"**Next step:** {decision.next_step}")
            st.write("**Triggered rules:**")
            for rule in decision.rules_triggered:
                st.write(f"- `{rule.rule_id}` {rule.rule_name}")
            st.write("**Explanation trace:**")
            for line in decision.explanation_trace:
                st.write(f"- {line}")
        else:
            st.warning(pipeline_result.validation.follow_up_question if pipeline_result.validation else "More information is needed.")

        with st.expander("Structured extraction"):
            st.json(extraction_result.payload.raw_evidence | {
                "symptoms": extraction_result.payload.symptoms,
                "duration_bucket": extraction_result.payload.duration_bucket,
                "age_years": extraction_result.payload.age_years,
                "severity_cues": extraction_result.payload.severity_cues,
                "missing_fields": extraction_result.payload.missing_fields,
            })


if __name__ == "__main__":
    render_app()
