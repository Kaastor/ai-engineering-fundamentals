from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from learning_compiler.agent.types import Action, Intent, Observation


StateT = TypeVar("StateT")


@dataclass(frozen=True, slots=True)
class Decision(Generic[StateT]):
    """A policy output.

    The agent *proposes* an action; the system is responsible for validation and execution.
    """

    next_state: StateT
    action: Action | None
    rationale: str
    stop: bool = False


class Policy(Protocol[StateT]):
    def decide(
        self,
        *,
        intent: Intent,
        state: StateT,
        observation: Observation,
        rng: random.Random,
    ) -> Decision[StateT]:
        """Produce the next action (or stop), possibly updating agent state."""
