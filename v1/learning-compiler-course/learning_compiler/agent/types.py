from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias


KeyVal: TypeAlias = tuple[str, str]


class EffectType(str, Enum):
    """A coarse type for side effects.

    This is intentionally simple for teaching: the point is that "read" vs "write"
    is a systems boundary, not a vibes boundary.
    """

    READ = "read"
    WRITE = "write"
    COMPUTE = "compute"


class ActionKind(str, Enum):
    """Closed set of action kinds used across labs.

    Labs may define additional domain-specific actions, but they should go through the
    same *typed* channel (new Enum member, not a free-form string).
    """

    MOVE = "move"
    ASK = "ask"
    TOOL = "tool"
    NOOP = "noop"


class ObservationSource(str, Enum):
    ENVIRONMENT = "environment"
    TOOL = "tool"
    USER = "user"
    SYSTEM = "system"


@dataclass(frozen=True, slots=True)
class Budget:
    max_steps: int
    max_side_effects: int


@dataclass(frozen=True, slots=True)
class Intent:
    """What the agent is trying to do, and under what constraints."""

    goal: str
    budget: Budget


@dataclass(frozen=True, slots=True)
class Action:
    """Something the agent proposes the system do."""

    kind: ActionKind
    effect: EffectType
    name: str
    params: tuple[KeyVal, ...] = ()

    def param(self, key: str) -> str | None:
        for k, v in self.params:
            if k == key:
                return v
        return None


@dataclass(frozen=True, slots=True)
class Plan:
    """A sequence of actions with an optional cost estimate."""

    steps: tuple[Action, ...]
    estimated_cost: float | None = None


@dataclass(frozen=True, slots=True)
class Observation:
    """A piece of information the agent receives (not truth-by-default)."""

    source: ObservationSource
    text: str
    data: tuple[KeyVal, ...] = ()


@dataclass(frozen=True, slots=True)
class Evidence:
    """Verification artifact: did the action have the intended effect?"""

    ok: bool
    text: str
    data: tuple[KeyVal, ...] = ()
