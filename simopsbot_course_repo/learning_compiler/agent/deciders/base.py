from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from learning_compiler.agent.actions import Action
from learning_compiler.agent.hypotheses import Hypotheses
from learning_compiler.agent.state import AgentState


@dataclass(slots=True, frozen=True)
class Decision:
    action: Action
    model_proposal: str | None = None
    validation_error: str | None = None


class Decider(Protocol):
    def decide(self, *, state: AgentState, hypotheses: Hypotheses | None) -> Decision:
        raise NotImplementedError
