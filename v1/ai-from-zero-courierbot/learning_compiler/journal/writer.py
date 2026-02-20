from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from learning_compiler.core.hashing import StableIdFactory
from learning_compiler.core.json import JsonValue, dumps_compact
from learning_compiler.journal.models import EventType, JournalEvent


@dataclass(slots=True)
class JsonlJournalWriter:
    """Append-only writer for a run journal (JSON Lines).

    The writer is deterministic: it never adds timestamps; it uses stable event IDs.
    """

    path: Path
    id_factory: StableIdFactory
    _fp: TextIO | None = None
    _seq: int = 0

    def __enter__(self) -> JsonlJournalWriter:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fp = self.path.open("w", encoding="utf-8")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        if self._fp is not None:
            self._fp.close()
        self._fp = None

    @property
    def seq(self) -> int:
        return self._seq

    def write(self, event_type: EventType, payload: JsonValue) -> JournalEvent:
        if self._fp is None:
            raise RuntimeError("journal writer is not opened")

        event = JournalEvent(
            event_type=event_type,
            seq=self._seq,
            event_id=self.id_factory.event_id(seq=self._seq),
            payload=payload,
        )
        self._fp.write(dumps_compact(event.to_json()) + "\n")
        self._seq += 1
        return event
