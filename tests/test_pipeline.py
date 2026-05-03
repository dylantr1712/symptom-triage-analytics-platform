from triage_app.models import ExtractionPayload, PipelineStatus, TriageLevel
from triage_app.pipeline import run_triage_pipeline


def test_pipeline_returns_insufficient_information_when_required_fields_missing():
    payload = ExtractionPayload(
        symptoms=["headache"],
        duration_bucket="unknown",
        age_years=31,
        severity_cues=[],
        missing_fields=["duration_bucket", "severity"],
    )

    result = run_triage_pipeline(payload)

    assert result.status == PipelineStatus.INSUFFICIENT_INFORMATION
    assert result.validation is not None
    assert result.decision is None


def test_pipeline_returns_follow_up_for_unmapped_symptoms():
    payload = ExtractionPayload(
        symptoms=["brain_fog"],
        duration_bucket="1_2_days",
        age_years=31,
        severity_cues=["mild"],
        missing_fields=[],
    )

    result = run_triage_pipeline(payload)

    assert result.status == PipelineStatus.INSUFFICIENT_INFORMATION
    assert "describe your symptoms" in result.validation.follow_up_question.lower()


def test_pipeline_returns_complete_decision_for_valid_payload():
    payload = ExtractionPayload(
        symptoms=["chest_pain", "shortness_of_breath"],
        duration_bucket="hours",
        age_years=55,
        severity_cues=["severe", "hard to breathe"],
        missing_fields=[],
    )

    result = run_triage_pipeline(payload)

    assert result.status == PipelineStatus.COMPLETE
    assert result.decision is not None
    assert result.decision.triage_level == TriageLevel.EMERGENCY
