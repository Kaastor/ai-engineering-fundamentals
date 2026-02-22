from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

from learning_compiler.types import JSONValue, RunId


class JournalKind(StrEnum):
    STEP_START = "step_start"
    OBSERVATION = "observation"
    MODEL_PROPOSAL = "model_proposal"
    VALIDATION = "validation"
    POLICY = "policy"
    ACTION = "action"
    VERIFY = "verify"
    FINAL = "final"
    ERROR = "error"


JournalPayload: TypeAlias = dict[str, JSONValue]


@dataclass(slots=True, frozen=True)
class JournalEvent:
    """One JSONL line in the run journal.

    Design goals:
    - replayable (enough info to understand decisions)
    - stable IDs (for evidence linking + deterministic tests)
    - small + readable (students will read these by hand)
    """

    event_id: str
    run_id: RunId
    step_id: int
    kind: JournalKind
    payload: JournalPayload
