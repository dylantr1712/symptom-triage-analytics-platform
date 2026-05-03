from triage_app.models import DurationBucket, ExtractionPayload, SeverityLevel
from triage_app.normalization import normalize_extraction


def test_normalization_derives_severe_from_red_flag_cues():
    payload = ExtractionPayload(
        symptoms=["chest_pain", "shortness_of_breath"],
        duration_bucket="hours",
        age_years=42,
        severity_cues=["severe", "hard to breathe", "tight chest"],
        missing_fields=[],
    )

    normalized = normalize_extraction(payload)

    assert normalized.severity == SeverityLevel.SEVERE
    assert normalized.duration_bucket == DurationBucket.HOURS


def test_normalization_marks_unknown_symptoms_for_follow_up():
    payload = ExtractionPayload(
        symptoms=["brain_fog"],
        duration_bucket="1_2_days",
        age_years=33,
        severity_cues=["mild"],
        missing_fields=[],
    )

    normalized = normalize_extraction(payload)

    assert normalized.normalized_symptoms == []
    assert normalized.unmapped_symptoms == ["brain_fog"]


def test_normalization_maps_common_symptom_aliases():
    payload = ExtractionPayload(
        symptoms=["breathless", "tight chest", "throwing up", "temperature"],
        duration_bucket="1_2_days",
        age_years=44,
        severity_cues=["moderate"],
        missing_fields=[],
    )

    normalized = normalize_extraction(payload)

    assert normalized.normalized_symptoms == [
        "shortness_of_breath",
        "chest_pain",
        "vomiting",
        "fever",
    ]
    assert normalized.unmapped_symptoms == []
