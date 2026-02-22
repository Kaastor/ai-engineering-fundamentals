from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal, NewType, TypeAlias

# ---- Domain primitives (explicit, non-stringly-typed where it matters) ----

ServiceName: TypeAlias = Literal["api", "db"]
ScenarioSeed = NewType("ScenarioSeed", int)
RunId = NewType("RunId", str)
IdempotencyKey = NewType("IdempotencyKey", str)

# JSON is a boundary type: keep it explicit so "anything goes" doesn't leak inward.
JSONScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]


class IncidentType(StrEnum):
    API_BAD_DEPLOY = "api_bad_deploy"
    DB_SATURATION = "db_saturation"
    NETWORK_FLAKY = "network_flaky"


class ConfidenceLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ToolName(StrEnum):
    GET_METRICS = "get_metrics"
    TAIL_LOGS = "tail_logs"
    HEALTH_CHECK = "health_check"
    RUNBOOK_SEARCH = "runbook_search"
    RESTART = "restart"
    ROLLBACK = "rollback"


@dataclass(slots=True, frozen=True)
class Budget:
    """Budgets are explicit stop rules (determinism-friendly, no wall-clock)."""

    max_steps: int
    max_tool_calls: int
    max_side_effect_actions: int

    def validate(self) -> None:
        if self.max_steps <= 0:
            raise ValueError("max_steps must be positive")
        if self.max_tool_calls <= 0:
            raise ValueError("max_tool_calls must be positive")
        if self.max_side_effect_actions < 0:
            raise ValueError("max_side_effect_actions must be non-negative")


DEFAULT_BUDGET = Budget(max_steps=12, max_tool_calls=40, max_side_effect_actions=3)
