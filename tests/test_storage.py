import json

from triage_app.models import (
    ExtractionPayload,
    NormalizedExtraction,
    SessionEvent,
    SeverityLevel,
    TriageDecision,
    TriageLevel,
    TriggeredRule,
    ValidationResult,
    ValidationStatus,
    DurationBucket,
)
from triage_app.storage import LocalJsonlStorage


def test_local_storage_writes_session_event_jsonl(tmp_path):
    storage = LocalJsonlStorage(tmp_path / "session_events.jsonl")
    event = SessionEvent.create(
        session_id="session-123",
        raw_text="I have chest pain",
        extraction=ExtractionPayload(
            symptoms=["chest_pain"],
            duration_bucket="hours",
            age_years=45,
            severity_cues=["severe"],
            missing_fields=[],
        ),
        validation=ValidationResult(
            status=ValidationStatus.VALID,
            missing_fields=[],
            follow_up_question="",
        ),
        normalized=NormalizedExtraction(
            normalized_symptoms=["chest_pain"],
            unmapped_symptoms=[],
            duration_bucket=DurationBucket.HOURS,
            severity=SeverityLevel.SEVERE,
            age_years=45,
            severity_reasons=["matched explicit severe cue"],
        ),
        decision=TriageDecision(
            triage_level=TriageLevel.EMERGENCY,
            headline="Seek urgent medical care now.",
            explanation="Emergency rule matched.",
            next_step="Attend emergency care.",
            rules_triggered=[
                TriggeredRule(
                    rule_id="ER002",
                    rule_name="severe_chest_pain",
                    matched_on={"symptoms": ["chest_pain"]},
                )
            ],
            explanation_trace=["Triggered rule ER002"],
        ),
    )

    storage.write_event(event)

    payload = json.loads((tmp_path / "session_events.jsonl").read_text().strip())
    assert payload["session_id"] == "session-123"
    assert payload["decision"]["triage_level"] == "EMERGENCY"
