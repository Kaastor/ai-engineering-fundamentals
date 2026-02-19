"""Run journal event models.

The journal is the course's *evidence artifact*: every run produces a deterministic JSONL file
that can be inspected, diffed, and replayed.

We keep the journal schema small on purpose. Students should be able to open the JSONL and understand it.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from learning_compiler.core.json import JsonValue


class EventType(str, Enum):
    RUN_START = "run_start"
    STEP = "step"
    RUN_END = "run_end"
    VIOLATION = "violation"


@dataclass(frozen=True, slots=True)
class JournalEvent:
    """A single JSONL journal event."""

    event_type: EventType
    seq: int
    event_id: str
    payload: JsonValue

    def to_json(self) -> JsonValue:
        obj: dict[str, JsonValue] = {
            "type": self.event_type.value,
            "seq": self.seq,
            "event_id": self.event_id,
            "payload": self.payload,
        }
        return obj
