from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

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
    def __init__(self, connection_parameters: dict[str, str]) -> None:
        self.connection_parameters = connection_parameters

    def write_event(self, event: SessionEvent) -> None:
        raise NotImplementedError(
            "Snowflake wiring is intentionally deferred until account provisioning is complete."
        )
