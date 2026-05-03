from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Protocol

from triage_app.models import SessionEvent


class EventStorage(Protocol):
    def write_event(self, event: SessionEvent) -> None:
        ...


class LocalJsonlStorage:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write_event(self, event: SessionEvent) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.to_dict()))
            handle.write("\n")


class SnowflakeStorage:
    def __init__(
        self,
        connection_parameters: dict[str, str],
        connection_factory: Callable[..., Any] | None = None,
    ) -> None:
        self.connection_parameters = connection_parameters
        self.connection_factory = connection_factory or self._default_connection_factory

    def write_event(self, event: SessionEvent) -> None:
        connection = self.connection_factory(**self.connection_parameters)
        cursor = connection.cursor()
        database = self.connection_parameters["database"]
        raw_schema = self.connection_parameters.get("raw_schema", self.connection_parameters["schema"])

        try:
            cursor.execute(
                (
                    f"insert into {database}.{raw_schema}.triage_sessions "
                    "(session_id, created_at, raw_text, age_years, duration_bucket, severity, "
                    "triage_level, pipeline_status, validation_status, follow_up_question, "
                    "explanation, next_step, raw_openai_response, unmapped_symptoms, "
                    "severity_reasons, app_version) "
                    "select %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
                    "parse_json(%s), parse_json(%s), %s"
                ),
                (
                    event.session_id,
                    event.created_at,
                    event.raw_text,
                    event.normalized.age_years if event.normalized else event.extraction.age_years,
                    event.normalized.duration_bucket.value if event.normalized else event.extraction.duration_bucket,
                    event.normalized.severity.value if event.normalized else None,
                    event.decision.triage_level.value if event.decision else None,
                    event.pipeline_status.value,
                    event.validation.status.value if event.validation else None,
                    event.validation.follow_up_question if event.validation else None,
                    event.decision.explanation if event.decision else None,
                    event.decision.next_step if event.decision else None,
                    event.raw_openai_response,
                    json.dumps(event.normalized.unmapped_symptoms if event.normalized else []),
                    json.dumps(event.normalized.severity_reasons if event.normalized else []),
                    event.app_version,
                ),
            )

            if event.decision:
                for rule in event.decision.rules_triggered:
                    cursor.execute(
                        (
                            f"insert into {database}.{raw_schema}.triage_rule_hits "
                            "(session_id, rule_id, rule_name, matched_on, created_at) "
                            "select %s, %s, %s, parse_json(%s), %s"
                        ),
                        (
                            event.session_id,
                            rule.rule_id,
                            rule.rule_name,
                            json.dumps(rule.matched_on),
                            event.created_at,
                        ),
                    )

            if event.normalized:
                for symptom_code in event.normalized.normalized_symptoms:
                    cursor.execute(
                        (
                            f"insert into {database}.{raw_schema}.triage_session_symptoms "
                            "(session_id, symptom_code, created_at) values (%s, %s, %s)"
                        ),
                        (
                            event.session_id,
                            symptom_code,
                            event.created_at,
                        ),
                    )

            connection.commit()
        finally:
            cursor.close()
            connection.close()

    @staticmethod
    def _default_connection_factory(**connection_parameters):
        try:
            import snowflake.connector
        except ImportError as exc:
            raise RuntimeError(
                "snowflake-connector-python is not installed. Install dependencies before using Snowflake storage."
            ) from exc

        return snowflake.connector.connect(**connection_parameters)


def build_storage_from_env() -> EventStorage:
    required = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA"),
        "raw_schema": os.getenv("SNOWFLAKE_RAW_SCHEMA", "RAW"),
        "role": os.getenv("SNOWFLAKE_ROLE"),
    }
    if all(required.values()):
        return SnowflakeStorage(required)

    log_path = Path("local_data") / "session_events.jsonl"
    return LocalJsonlStorage(log_path)
