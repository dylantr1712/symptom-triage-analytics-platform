from triage_app.models import (
    DurationBucket,
    NormalizedExtraction,
    SeverityLevel,
    TriageLevel,
)
from triage_app.triage import evaluate_triage


def test_triage_returns_emergency_for_severe_chest_pain_and_shortness_of_breath():
    normalized = NormalizedExtraction(
        normalized_symptoms=["chest_pain", "shortness_of_breath"],
        unmapped_symptoms=[],
        duration_bucket=DurationBucket.HOURS,
        severity=SeverityLevel.SEVERE,
        age_years=42,
        severity_reasons=["explicit severe cue"],
    )

    decision = evaluate_triage(normalized)

    assert decision.triage_level == TriageLevel.EMERGENCY
    assert {rule.rule_id for rule in decision.rules_triggered} >= {"ER001", "ER002"}


def test_triage_returns_self_care_for_short_mild_low_risk_symptoms():
    normalized = NormalizedExtraction(
        normalized_symptoms=["sore_throat"],
        unmapped_symptoms=[],
        duration_bucket=DurationBucket.HOURS,
        severity=SeverityLevel.MILD,
        age_years=29,
        severity_reasons=["mild cue"],
    )

    decision = evaluate_triage(normalized)

    assert decision.triage_level == TriageLevel.SELF_CARE


def test_triage_returns_see_gp_for_moderate_long_duration_symptoms():
    normalized = NormalizedExtraction(
        normalized_symptoms=["cough"],
        unmapped_symptoms=[],
        duration_bucket=DurationBucket.OVER_1_WEEK,
        severity=SeverityLevel.MODERATE,
        age_years=29,
        severity_reasons=["interferes with sleep"],
    )

    decision = evaluate_triage(normalized)

    assert decision.triage_level == TriageLevel.SEE_GP
    assert any(rule.rule_id == "GP001" for rule in decision.rules_triggered)


def test_emergency_rules_override_gp_rules():
    normalized = NormalizedExtraction(
        normalized_symptoms=["shortness_of_breath", "cough"],
        unmapped_symptoms=[],
        duration_bucket=DurationBucket.OVER_1_WEEK,
        severity=SeverityLevel.SEVERE,
        age_years=61,
        severity_reasons=["high-risk respiratory symptom present"],
    )

    decision = evaluate_triage(normalized)

    assert decision.triage_level == TriageLevel.EMERGENCY
    assert any(rule.rule_id == "ER001" for rule in decision.rules_triggered)
