from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, Sequence, TypeVar

from learning_compiler.agent.types import Action, Evidence, Observation
from learning_compiler.util.hashing import stable_sha256_hex


StateT = TypeVar("StateT")


@dataclass(frozen=True, slots=True)
class JournalRecord:
    """One full agent-loop iteration (a 'turn').

    We store only deterministic, JSON-serializable data so traces can be hashed
    and compared in tests.
    """

    step_index: int
    state_digest: str
    observation: Observation
    decision_rationale: str
    proposed_action: Action | None
    action_observation: Observation | None
    evidence: Evidence | None
    next_state_digest: str


@dataclass(slots=True)
class RunJournal(Generic[StateT]):
    """A deterministic run journal (black-box recorder)."""

    run_id: str
    _records: list[JournalRecord] = field(default_factory=list)

    def append(self, record: JournalRecord) -> None:
        self._records.append(record)

    def records(self) -> Sequence[JournalRecord]:
        return tuple(self._records)

    def trace_hash(self) -> str:
        """Stable hash of the run's journal contents."""

        return stable_sha256_hex({"run_id": self.run_id, "records": self._records})
