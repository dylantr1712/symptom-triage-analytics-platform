from __future__ import annotations

from triage_app.models import ExtractionPayload, ValidationResult, ValidationStatus


def validate_extraction(payload: ExtractionPayload) -> ValidationResult:
    missing_fields = list(payload.missing_fields)

    if not payload.symptoms:
        missing_fields.append("symptoms")
    if payload.duration_bucket == "unknown" and "duration_bucket" not in missing_fields:
        missing_fields.append("duration_bucket")
    if payload.age_years is None and "age_years" not in missing_fields:
        missing_fields.append("age_years")
    if not payload.severity_cues and "severity" not in missing_fields:
        missing_fields.append("severity")

    if payload.age_years is not None and payload.age_years < 18:
        return ValidationResult(
            status=ValidationStatus.UNSUPPORTED,
            missing_fields=[],
            follow_up_question=(
                "This adult-only version does not support people under 18. "
                "Please use an adult triage workflow or contact a clinician."
            ),
        )

    if missing_fields:
        return ValidationResult(
            status=ValidationStatus.INSUFFICIENT_INFORMATION,
            missing_fields=missing_fields,
            follow_up_question=_build_follow_up_question(missing_fields),
        )

    return ValidationResult(
        status=ValidationStatus.VALID,
        missing_fields=[],
        follow_up_question="",
    )


def _build_follow_up_question(missing_fields: list[str]) -> str:
    prompts: list[str] = []
    if "symptoms" in missing_fields:
        prompts.append("what symptoms are you having")
    if "duration_bucket" in missing_fields:
        prompts.append("how long you have had these symptoms")
    if "severity" in missing_fields:
        prompts.append("whether the symptoms feel mild, moderate, or severe")
    if "age_years" in missing_fields:
        prompts.append("How old are you")

    if not prompts:
        return "Please share a little more detail so I can continue."

    if len(prompts) == 1:
        return f"Please tell me {prompts[0]}."

    prefix = ", ".join(prompts[:-1])
    return f"Please tell me {prefix}, and {prompts[-1]}."

