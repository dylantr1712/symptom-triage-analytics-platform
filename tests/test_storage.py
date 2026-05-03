import json

from triage_app.models import (
    ExtractionPayload,
    NormalizedExtraction,
    PipelineStatus,
    SessionEvent,
    SeverityLevel,
    TriageDecision,
    TriageLevel,
    TriggeredRule,
    ValidationResult,
    ValidationStatus,
    DurationBucket,
)
from triage_app.storage import LocalJsonlStorage, SnowflakeStorage


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
    assert payload["pipeline_status"] == "COMPLETE"
    assert payload["decision"]["triage_level"] == "EMERGENCY"


class RecordingCursor:
    def __init__(self):
        self.executed = []

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def close(self):
        return None


class RecordingConnection:
    def __init__(self):
        self.cursor_instance = RecordingCursor()
        self.committed = False

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        self.committed = True

    def close(self):
        return None


def test_snowflake_storage_writes_session_rule_and_symptom_rows():
    connection = RecordingConnection()
    storage = SnowflakeStorage(
        connection_parameters={
            "database": "TRIAGE_PLATFORM",
            "schema": "ANALYTICS",
            "raw_schema": "RAW",
        },
        connection_factory=lambda **_: connection,
    )
    event = SessionEvent.create(
        session_id="session-123",
        raw_text="I have chest pain",
        extraction=ExtractionPayload(
            symptoms=["chest_pain", "shortness_of_breath"],
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
            normalized_symptoms=["chest_pain", "shortness_of_breath"],
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
                    rule_id="ER001",
                    rule_name="severe_shortness_of_breath",
                    matched_on={"symptoms": ["shortness_of_breath"]},
                )
            ],
            explanation_trace=["Triggered rule ER001"],
        ),
        pipeline_status=PipelineStatus.COMPLETE,
        raw_openai_response='{"symptoms":["chest_pain"]}',
        app_version="test-version",
    )

    storage.write_event(event)

    assert connection.committed is True
    assert len(connection.cursor_instance.executed) == 4

    session_insert, session_params = connection.cursor_instance.executed[0]
    assert "insert into TRIAGE_PLATFORM.RAW.triage_sessions" in session_insert
    assert "parse_json(%s)" in session_insert
    assert session_params[0] == "session-123"
    assert session_params[7] == "COMPLETE"

    rule_insert, rule_params = connection.cursor_instance.executed[1]
    assert "insert into TRIAGE_PLATFORM.RAW.triage_rule_hits" in rule_insert
    assert "select %s, %s, %s, parse_json(%s), %s" in rule_insert
    assert rule_params[1] == "ER001"

    symptom_insert, symptom_params = connection.cursor_instance.executed[2]
    assert "insert into TRIAGE_PLATFORM.RAW.triage_session_symptoms" in symptom_insert
    assert symptom_params[1] == "chest_pain"
