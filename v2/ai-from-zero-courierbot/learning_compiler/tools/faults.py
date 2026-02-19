"""Deterministic fault injection.

Fault injection is central to the reliability/evaluation labs:
we intentionally make tools fail in repeatable ways so students can debug using journals.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum

from learning_compiler.core.hashing import stable_hash_int
from learning_compiler.tools.contracts import ToolName


class FaultType(str, Enum):
    TIMEOUT = "timeout"
    MALFORMED = "malformed"
    EXCEPTION = "exception"


@dataclass(frozen=True, slots=True)
class FaultPlan:
    seed: int
    fault_rate: float = 0.15
    timeout_fraction: float = 0.33
    malformed_fraction: float = 0.33
    exception_fraction: float = 0.34

    def fault_for_call(self, *, tool: ToolName, call_id: str, attempt: int) -> FaultType | None:
        """Returns a fault type for this call, or None for a clean call."""

        # Derive a deterministic random number from stable hashing.
        r = _stable_unit_float([str(self.seed), tool.value, call_id, str(attempt), "fault"])
        if r >= self.fault_rate:
            return None

        which = _stable_unit_float([str(self.seed), tool.value, call_id, str(attempt), "which"])
        if which < self.timeout_fraction:
            return FaultType.TIMEOUT
        if which < self.timeout_fraction + self.malformed_fraction:
            return FaultType.MALFORMED
        return FaultType.EXCEPTION


def _stable_unit_float(parts: Iterable[str]) -> float:
    # 24 bits is plenty for a stable float in [0, 1).
    i = stable_hash_int(parts, bits=24)
    return i / float(1 << 24)
