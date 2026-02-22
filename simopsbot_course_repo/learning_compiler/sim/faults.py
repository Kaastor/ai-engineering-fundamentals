from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import random

from learning_compiler.types import ToolName


class FaultKind(StrEnum):
    NONE = "none"
    TIMEOUT = "timeout"
    TRANSIENT = "transient"
    PERMANENT = "permanent"


class ToolError(Exception):
    """Base class for simulated tool failures."""

    def __init__(self, *, tool: ToolName, message: str) -> None:
        super().__init__(message)
        self.tool = tool
        self.message = message


class ToolTimeout(ToolError):
    pass


class ToolTransientError(ToolError):
    pass


class ToolPermanentError(ToolError):
    pass


@dataclass(slots=True, frozen=True)
class FaultProfile:
    timeout_rate: float
    transient_rate: float
    permanent_rate: float

    def validate(self) -> None:
        for name, v in [
            ("timeout_rate", self.timeout_rate),
            ("transient_rate", self.transient_rate),
            ("permanent_rate", self.permanent_rate),
        ]:
            if v < 0.0 or v > 1.0:
                raise ValueError(f"{name} must be in [0, 1]")
        total = self.timeout_rate + self.transient_rate + self.permanent_rate
        if total > 1.0:
            raise ValueError("sum of fault rates must be <= 1")


DEFAULT_FAULT_PROFILE = FaultProfile(timeout_rate=0.08, transient_rate=0.06, permanent_rate=0.01)


class FaultPlan:
    """Deterministic fault injection for tools.

    The plan is *order-dependent*: same seed + same sequence of tool calls ⇒ same failures.

    That is intentional. It makes:
    - debugging replayable
    - evaluations stable
    """

    def __init__(self, *, seed: int, profile: FaultProfile = DEFAULT_FAULT_PROFILE) -> None:
        profile.validate()
        self._profile = profile
        self._rng = random.Random(seed ^ 0xA17C_2026)
        self._call_index = 0

    @property
    def call_index(self) -> int:
        return self._call_index

    def maybe_raise(self, *, tool: ToolName) -> None:
        self._call_index += 1
        roll = self._rng.random()
        if roll < self._profile.timeout_rate:
            raise ToolTimeout(tool=tool, message=f"{tool.value} timed out")
        roll -= self._profile.timeout_rate
        if roll < self._profile.transient_rate:
            raise ToolTransientError(tool=tool, message=f"{tool.value} transient failure")
        roll -= self._profile.transient_rate
        if roll < self._profile.permanent_rate:
            raise ToolPermanentError(tool=tool, message=f"{tool.value} permanent failure")
