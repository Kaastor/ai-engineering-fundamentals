from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StopReason(str, Enum):
    GOAL_REACHED = "goal_reached"
    BUDGET_EXHAUSTED = "budget_exhausted"
    NO_ACTION = "no_action"
    POLICY_ERROR = "policy_error"
    ENVIRONMENT_ERROR = "environment_error"


@dataclass(frozen=True, slots=True)
class StopOutcome:
    reason: StopReason
    detail: str
