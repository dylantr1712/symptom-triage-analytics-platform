from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class DurationBucket(str, Enum):
    HOURS = "hours"
    ONE_TO_TWO_DAYS = "1_2_days"
    THREE_TO_SEVEN_DAYS = "3_7_days"
    OVER_1_WEEK = "over_1_week"
    UNKNOWN = "unknown"


class SeverityLevel(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    UNKNOWN = "unknown"


class ValidationStatus(str, Enum):
    VALID = "VALID"
    INSUFFICIENT_INFORMATION = "INSUFFICIENT_INFORMATION"
    UNSUPPORTED = "UNSUPPORTED"


class TriageLevel(str, Enum):
    SELF_CARE = "SELF_CARE"
    SEE_GP = "SEE_GP"
    EMERGENCY = "EMERGENCY"


class PipelineStatus(str, Enum):
    COMPLETE = "COMPLETE"
    INSUFFICIENT_INFORMATION = "INSUFFICIENT_INFORMATION"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(slots=True)
class ExtractionPayload:
    symptoms: list[str]
    duration_bucket: str
    age_years: int | None
    severity_cues: list[str]
    missing_fields: list[str]
    raw_evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ValidationResult:
    status: ValidationStatus
    missing_fields: list[str]
    follow_up_question: str


@dataclass(slots=True)
class NormalizedExtraction:
    normalized_symptoms: list[str]
    unmapped_symptoms: list[str]
    duration_bucket: DurationBucket
    severity: SeverityLevel
    age_years: int
    severity_reasons: list[str]


@dataclass(slots=True)
class TriggeredRule:
    rule_id: str
    rule_name: str
    matched_on: dict[str, Any]


@dataclass(slots=True)
class TriageDecision:
    triage_level: TriageLevel
    headline: str
    explanation: str
    next_step: str
    rules_triggered: list[TriggeredRule]
    explanation_trace: list[str]


@dataclass(slots=True)
class PipelineResult:
    status: PipelineStatus
    validation: ValidationResult | None
    normalized: NormalizedExtraction | None
    decision: TriageDecision | None


@dataclass(slots=True)
class SessionEvent:
    session_id: str
    created_at: str
    raw_text: str
    extraction: ExtractionPayload
    validation: ValidationResult | None
    normalized: NormalizedExtraction | None
    decision: TriageDecision | None

    @classmethod
    def create(
        cls,
        session_id: str,
        raw_text: str,
        extraction: ExtractionPayload,
        validation: ValidationResult | None,
        normalized: NormalizedExtraction | None,
        decision: TriageDecision | None,
    ) -> "SessionEvent":
        return cls(
            session_id=session_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            raw_text=raw_text,
            extraction=extraction,
            validation=validation,
            normalized=normalized,
            decision=decision,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

