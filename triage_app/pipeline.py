from __future__ import annotations

from triage_app.models import PipelineResult, PipelineStatus, ValidationResult, ValidationStatus
from triage_app.normalization import normalize_extraction
from triage_app.triage import evaluate_triage
from triage_app.validation import validate_extraction


def run_triage_pipeline(payload):
    validation = validate_extraction(payload)
    if validation.status == ValidationStatus.UNSUPPORTED:
        return PipelineResult(
            status=PipelineStatus.UNSUPPORTED,
            validation=validation,
            normalized=None,
            decision=None,
        )
    if validation.status == ValidationStatus.INSUFFICIENT_INFORMATION:
        return PipelineResult(
            status=PipelineStatus.INSUFFICIENT_INFORMATION,
            validation=validation,
            normalized=None,
            decision=None,
        )

    normalized = normalize_extraction(payload)
    if normalized.unmapped_symptoms:
        follow_up = ValidationResult(
            status=ValidationStatus.INSUFFICIENT_INFORMATION,
            missing_fields=["symptoms"],
            follow_up_question=(
                "Please describe your symptoms using simpler symptom words so I can match "
                "them to the supported triage vocabulary."
            ),
        )
        return PipelineResult(
            status=PipelineStatus.INSUFFICIENT_INFORMATION,
            validation=follow_up,
            normalized=normalized,
            decision=None,
        )

    decision = evaluate_triage(normalized)
    return PipelineResult(
        status=PipelineStatus.COMPLETE,
        validation=validation,
        normalized=normalized,
        decision=decision,
    )
