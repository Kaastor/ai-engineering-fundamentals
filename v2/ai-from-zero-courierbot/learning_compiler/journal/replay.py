"""Replay reader for run journals."""
from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from learning_compiler.core.json import JsonValue


@dataclass(frozen=True, slots=True)
class ReplayEvent:
    type: str
    seq: int
    event_id: str
    payload: JsonValue


def read_jsonl(path: Path) -> Iterator[ReplayEvent]:
    with path.open("r", encoding="utf-8") as fp:
        for line in fp:
            raw = json.loads(line)
            yield ReplayEvent(
                type=str(raw["type"]),
                seq=int(raw["seq"]),
                event_id=str(raw["event_id"]),
                payload=raw["payload"],
            )
