from __future__ import annotations

from triage_app.models import DurationBucket, ExtractionPayload, NormalizedExtraction, SeverityLevel
from triage_app.symptom_vocabulary import (
    MODERATE_CUE_KEYWORDS,
    SEVERE_CUE_KEYWORDS,
    SYMPTOM_ALIASES,
    SUPPORTED_SYMPTOMS,
)


def normalize_extraction(payload: ExtractionPayload) -> NormalizedExtraction:
    normalized_symptoms: list[str] = []
    unmapped_symptoms: list[str] = []
    for symptom in payload.symptoms:
        normalized = symptom.strip().lower().replace(" ", "_")
        normalized = SYMPTOM_ALIASES.get(normalized, normalized)
        if normalized in SUPPORTED_SYMPTOMS:
            normalized_symptoms.append(normalized)
        else:
            unmapped_symptoms.append(normalized)

    severity, reasons = derive_severity(payload.severity_cues, normalized_symptoms)

    return NormalizedExtraction(
        normalized_symptoms=normalized_symptoms,
        unmapped_symptoms=unmapped_symptoms,
        duration_bucket=DurationBucket(payload.duration_bucket),
        severity=severity,
        age_years=payload.age_years or 0,
        severity_reasons=reasons,
    )


def derive_severity(
    severity_cues: list[str],
    normalized_symptoms: list[str],
) -> tuple[SeverityLevel, list[str]]:
    lowered_cues = [cue.strip().lower() for cue in severity_cues]
    reasons: list[str] = []

    if any(cue in SEVERE_CUE_KEYWORDS for cue in lowered_cues):
        reasons.append("matched explicit severe cue")
        return SeverityLevel.SEVERE, reasons

    if {"chest_pain", "shortness_of_breath"} & set(normalized_symptoms):
        reasons.append("high-risk respiratory or chest symptom present")
        return SeverityLevel.SEVERE, reasons

    if any(cue in MODERATE_CUE_KEYWORDS for cue in lowered_cues):
        reasons.append("matched explicit moderate cue")
        return SeverityLevel.MODERATE, reasons

    if lowered_cues:
        reasons.append("defaulted to mild based on non-red-flag cues")
        return SeverityLevel.MILD, reasons

    reasons.append("no severity cues available")
    return SeverityLevel.UNKNOWN, reasons
