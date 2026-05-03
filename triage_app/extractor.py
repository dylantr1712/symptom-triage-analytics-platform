from __future__ import annotations

import json
import os
from dataclasses import dataclass
from textwrap import dedent
from typing import Any, Protocol

from triage_app.models import ExtractionPayload


EXTRACTION_PROMPT = dedent(
    """
    You extract structured symptom triage data from a user message.
    Return strict JSON only with these keys:
    - symptoms: array of normalized symptom codes
    - duration_bucket: one of hours, 1_2_days, 3_7_days, over_1_week, unknown
    - age_years: integer or null
    - severity_cues: array of short phrases quoted or paraphrased from the user
    - missing_fields: array containing any of symptoms, duration_bucket, age_years, severity
    - raw_evidence: object with optional evidence snippets

    Do not diagnose. Do not return prose outside JSON.
    """
).strip()

EXTRACTION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "symptoms": {
            "type": "array",
            "items": {"type": "string"},
        },
        "duration_bucket": {
            "type": "string",
            "enum": ["hours", "1_2_days", "3_7_days", "over_1_week", "unknown"],
        },
        "age_years": {
            "type": ["integer", "null"],
        },
        "severity_cues": {
            "type": "array",
            "items": {"type": "string"},
        },
        "missing_fields": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["symptoms", "duration_bucket", "age_years", "severity"],
            },
        },
        "raw_evidence": {
            "type": "object",
            "additionalProperties": True,
        },
    },
    "required": [
        "symptoms",
        "duration_bucket",
        "age_years",
        "severity_cues",
        "missing_fields",
        "raw_evidence",
    ],
}


class ChatCompletionClient(Protocol):
    def extract_json(self, prompt: str, user_text: str) -> str:
        ...


@dataclass(slots=True)
class ExtractionResult:
    payload: ExtractionPayload
    raw_response: str


class OpenAIExtractionClient:
    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        self.model = model

    def extract_json(self, prompt: str, user_text: str) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "The openai package is not installed. Install dependencies before using live extraction."
            ) from exc

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_text},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "symptom_triage_extraction",
                    "strict": True,
                    "schema": EXTRACTION_SCHEMA,
                }
            },
        )
        return response.output_text


class StubExtractionClient:
    def extract_json(self, prompt: str, user_text: str) -> str:
        lowered = user_text.lower()
        payload: dict[str, Any] = {
            "symptoms": [],
            "duration_bucket": "unknown",
            "age_years": None,
            "severity_cues": [],
            "missing_fields": [],
            "raw_evidence": {"user_text": user_text},
        }

        symptom_map = {
            "chest pain": "chest_pain",
            "shortness of breath": "shortness_of_breath",
            "hard to breathe": "shortness_of_breath",
            "trouble breathing": "shortness_of_breath",
            "cough": "cough",
            "sore throat": "sore_throat",
            "headache": "headache",
            "vomiting": "vomiting",
            "fever": "fever",
        }
        for phrase, code in symptom_map.items():
            if phrase in lowered and code not in payload["symptoms"]:
                payload["symptoms"].append(code)

        if "today" in lowered or "this morning" in lowered or "few hours" in lowered:
            payload["duration_bucket"] = "hours"
        elif "2 days" in lowered or "two days" in lowered:
            payload["duration_bucket"] = "1_2_days"
        elif "week" in lowered:
            payload["duration_bucket"] = "over_1_week"

        if "severe" in lowered or "hard to breathe" in lowered:
            payload["severity_cues"].append("severe")
        elif "moderate" in lowered:
            payload["severity_cues"].append("moderate")
        elif "mild" in lowered or "slight" in lowered:
            payload["severity_cues"].append("mild")

        age = _extract_first_int(lowered)
        payload["age_years"] = age

        if not payload["symptoms"]:
            payload["missing_fields"].append("symptoms")
        if payload["duration_bucket"] == "unknown":
            payload["missing_fields"].append("duration_bucket")
        if payload["age_years"] is None:
            payload["missing_fields"].append("age_years")
        if not payload["severity_cues"]:
            payload["missing_fields"].append("severity")

        return json.dumps(payload)


class SymptomExtractor:
    def __init__(self, client: ChatCompletionClient) -> None:
        self.client = client

    def extract(self, user_text: str) -> ExtractionResult:
        raw_response = self.client.extract_json(EXTRACTION_PROMPT, user_text)
        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise ValueError("Extraction response was not valid JSON.") from exc

        required_keys = {
            "symptoms",
            "duration_bucket",
            "age_years",
            "severity_cues",
            "missing_fields",
        }
        missing = required_keys.difference(parsed)
        if missing:
            raise ValueError(f"Extraction response missing required keys: {sorted(missing)}")

        payload = ExtractionPayload(
            symptoms=list(parsed["symptoms"]),
            duration_bucket=str(parsed["duration_bucket"]),
            age_years=parsed["age_years"],
            severity_cues=list(parsed["severity_cues"]),
            missing_fields=list(parsed["missing_fields"]),
            raw_evidence=dict(parsed.get("raw_evidence", {})),
        )
        return ExtractionResult(payload=payload, raw_response=raw_response)


def _extract_first_int(text: str) -> int | None:
    digits = []
    for token in text.replace(",", " ").split():
        if token.isdigit():
            digits.append(int(token))
    return digits[0] if digits else None
