from __future__ import annotations

from triage_app.models import (
    DurationBucket,
    NormalizedExtraction,
    SeverityLevel,
    TriageDecision,
    TriageLevel,
    TriggeredRule,
)
from triage_app.symptom_vocabulary import LOW_RISK_SYMPTOMS


def evaluate_triage(normalized: NormalizedExtraction) -> TriageDecision:
    emergency_rules = _match_emergency_rules(normalized)
    if emergency_rules:
        return TriageDecision(
            triage_level=TriageLevel.EMERGENCY,
            headline="Seek urgent medical care now.",
            explanation=(
                "Your symptoms match one or more emergency risk rules in this triage flow."
            ),
            next_step=(
                "Go to the nearest emergency department or call emergency services if "
                "symptoms are worsening."
            ),
            rules_triggered=emergency_rules,
            explanation_trace=_build_trace(normalized, emergency_rules, TriageLevel.EMERGENCY),
        )

    gp_rules = _match_gp_rules(normalized)
    if gp_rules:
        return TriageDecision(
            triage_level=TriageLevel.SEE_GP,
            headline="Book a GP or urgent primary care review.",
            explanation=(
                "Your symptoms are not in the emergency rule set, but they do match "
                "conditions that should be assessed by a clinician."
            ),
            next_step="Arrange a GP review soon, especially if symptoms are getting worse.",
            rules_triggered=gp_rules,
            explanation_trace=_build_trace(normalized, gp_rules, TriageLevel.SEE_GP),
        )

    self_care_rules = _match_self_care_rules(normalized)
    return TriageDecision(
        triage_level=TriageLevel.SELF_CARE,
        headline="Self-care is reasonable based on the current information.",
        explanation=(
            "Your symptoms fit the low-risk, short-duration branch of this triage flow."
        ),
        next_step=(
            "Monitor your symptoms and seek medical advice if they become more severe "
            "or last longer."
        ),
        rules_triggered=self_care_rules,
        explanation_trace=_build_trace(normalized, self_care_rules, TriageLevel.SELF_CARE),
    )


def _match_emergency_rules(normalized: NormalizedExtraction) -> list[TriggeredRule]:
    rules: list[TriggeredRule] = []
    symptoms = set(normalized.normalized_symptoms)

    if "shortness_of_breath" in symptoms and normalized.severity == SeverityLevel.SEVERE:
        rules.append(
            TriggeredRule(
                rule_id="ER001",
                rule_name="severe_shortness_of_breath",
                matched_on={"symptoms": ["shortness_of_breath"], "severity": normalized.severity.value},
            )
        )
    if "chest_pain" in symptoms and normalized.severity == SeverityLevel.SEVERE:
        rules.append(
            TriggeredRule(
                rule_id="ER002",
                rule_name="severe_chest_pain",
                matched_on={"symptoms": ["chest_pain"], "severity": normalized.severity.value},
            )
        )
    if "confusion" in symptoms:
        rules.append(
            TriggeredRule(
                rule_id="ER003",
                rule_name="confusion_present",
                matched_on={"symptoms": ["confusion"]},
            )
        )
    if "seizure" in symptoms:
        rules.append(
            TriggeredRule(
                rule_id="ER004",
                rule_name="seizure_present",
                matched_on={"symptoms": ["seizure"]},
            )
        )
    if "loss_of_consciousness" in symptoms:
        rules.append(
            TriggeredRule(
                rule_id="ER005",
                rule_name="loss_of_consciousness_present",
                matched_on={"symptoms": ["loss_of_consciousness"]},
            )
        )
    if "heavy_bleeding" in symptoms:
        rules.append(
            TriggeredRule(
                rule_id="ER006",
                rule_name="heavy_bleeding_present",
                matched_on={"symptoms": ["heavy_bleeding"]},
            )
        )
    return rules


def _match_gp_rules(normalized: NormalizedExtraction) -> list[TriggeredRule]:
    rules: list[TriggeredRule] = []
    symptoms = set(normalized.normalized_symptoms)

    if (
        normalized.severity == SeverityLevel.MODERATE
        and normalized.duration_bucket in {DurationBucket.THREE_TO_SEVEN_DAYS, DurationBucket.OVER_1_WEEK}
    ):
        rules.append(
            TriggeredRule(
                rule_id="GP001",
                rule_name="moderate_long_duration_symptoms",
                matched_on={
                    "severity": normalized.severity.value,
                    "duration_bucket": normalized.duration_bucket.value,
                },
            )
        )
    if "vomiting" in symptoms and normalized.duration_bucket != DurationBucket.HOURS:
        rules.append(
            TriggeredRule(
                rule_id="GP002",
                rule_name="persistent_vomiting",
                matched_on={
                    "symptoms": ["vomiting"],
                    "duration_bucket": normalized.duration_bucket.value,
                },
            )
        )
    if "fever" in symptoms and normalized.duration_bucket in {
        DurationBucket.THREE_TO_SEVEN_DAYS,
        DurationBucket.OVER_1_WEEK,
    }:
        rules.append(
            TriggeredRule(
                rule_id="GP003",
                rule_name="persistent_fever",
                matched_on={
                    "symptoms": ["fever"],
                    "duration_bucket": normalized.duration_bucket.value,
                },
            )
        )
    if "worsening_symptoms" in symptoms:
        rules.append(
            TriggeredRule(
                rule_id="GP004",
                rule_name="worsening_non_emergency_symptoms",
                matched_on={"symptoms": ["worsening_symptoms"]},
            )
        )
    return rules


def _match_self_care_rules(normalized: NormalizedExtraction) -> list[TriggeredRule]:
    low_risk = set(normalized.normalized_symptoms).issubset(LOW_RISK_SYMPTOMS)
    short_duration = normalized.duration_bucket in {
        DurationBucket.HOURS,
        DurationBucket.ONE_TO_TWO_DAYS,
    }
    if low_risk and short_duration and normalized.severity == SeverityLevel.MILD:
        return [
            TriggeredRule(
                rule_id="SC001",
                rule_name="mild_short_duration_low_risk_symptoms",
                matched_on={
                    "symptoms": normalized.normalized_symptoms,
                    "duration_bucket": normalized.duration_bucket.value,
                    "severity": normalized.severity.value,
                },
            )
        ]

    return [
        TriggeredRule(
            rule_id="SC000",
            rule_name="default_self_care_fallback",
            matched_on={"reason": "no emergency or GP rules matched"},
        )
    ]


def _build_trace(
    normalized: NormalizedExtraction,
    rules: list[TriggeredRule],
    level: TriageLevel,
) -> list[str]:
    trace = [f"Detected normalized symptom: {symptom}" for symptom in normalized.normalized_symptoms]
    trace.append(f"Severity normalized to {normalized.severity.value}")
    trace.append(f"Duration bucket normalized to {normalized.duration_bucket.value}")
    trace.append(f"Evaluated rules in priority order and selected {level.value}")
    trace.extend([f"Triggered rule: {rule.rule_id} ({rule.rule_name})" for rule in rules])
    return trace

