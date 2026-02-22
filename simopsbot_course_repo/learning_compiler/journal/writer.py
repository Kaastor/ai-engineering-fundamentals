from __future__ import annotations

from pathlib import Path
from types import TracebackType
from typing import Mapping

from learning_compiler.journal.models import JournalEvent, JournalKind
from learning_compiler.types import JSONValue, RunId
from learning_compiler.utils.hashing import stable_short_hash
from learning_compiler.utils.json import write_jsonl_line


class RunJournalWriter:
    """Append-only JSONL journal writer.

    Design goals:
    - Deterministic output (no wall-clock time).
    - Stable event IDs so we can reference evidence by ID.
    """

    def __init__(self, path: Path, *, run_id: RunId) -> None:
        self._path = path
        self._run_id = run_id
        self._fp = path.open("w", encoding="utf-8")
        self._seq = 0

    @property
    def path(self) -> Path:
        return self._path

    @property
    def run_id(self) -> RunId:
        return self._run_id

    def log(self, *, step_id: int, kind: JournalKind, payload: Mapping[str, JSONValue]) -> str:
        self._seq += 1
        event_id = stable_short_hash(f"{self._run_id}:{self._seq}:{step_id}:{kind}", length=12)
        event = JournalEvent(
            event_id=event_id,
            run_id=self._run_id,
            step_id=step_id,
            kind=kind,
            payload=dict(payload),
        )
        write_jsonl_line(self._fp, _event_to_json(event))
        return event_id

    def close(self) -> None:
        self._fp.close()

    def __enter__(self) -> "RunJournalWriter":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()


def _event_to_json(event: JournalEvent) -> dict[str, JSONValue]:
    return {
        "event_id": event.event_id,
        "run_id": str(event.run_id),
        "step_id": event.step_id,
        "kind": event.kind.value,
        "payload": event.payload,
    }
