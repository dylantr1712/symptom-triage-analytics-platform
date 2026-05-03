from triage_app.models import ExtractionPayload, ValidationStatus
from triage_app.validation import validate_extraction


def test_validation_requests_missing_fields_before_triage():
    payload = ExtractionPayload(
        symptoms=["sore_throat"],
        duration_bucket="unknown",
        age_years=None,
        severity_cues=[],
        missing_fields=["age_years", "severity"],
    )

    result = validate_extraction(payload)

    assert result.status == ValidationStatus.INSUFFICIENT_INFORMATION
    assert result.missing_fields == ["age_years", "severity", "duration_bucket"]
    assert "How old are you" in result.follow_up_question


def test_validation_routes_underage_users_out_of_scope():
    payload = ExtractionPayload(
        symptoms=["cough"],
        duration_bucket="hours",
        age_years=16,
        severity_cues=["moderate"],
        missing_fields=[],
    )

    result = validate_extraction(payload)

    assert result.status == ValidationStatus.UNSUPPORTED
    assert "adult" in result.follow_up_question.lower()
