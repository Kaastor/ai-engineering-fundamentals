from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from learning_compiler.types import JSONValue


@dataclass(slots=True, frozen=True)
class LLMContext:
    """Context passed to the model.

    Keep this *structured* (not a free-form mega-prompt) so:
    - it's testable
    - it can be validated/scrubbed
    - it encourages "contracts over vibes"
    """

    step_id: int
    state_summary: dict[str, JSONValue]
    observations: list[dict[str, JSONValue]]
    allowed_action_types: list[str]

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "step_id": self.step_id,
            "state_summary": self.state_summary,
            "observations": self.observations,
            "allowed_action_types": self.allowed_action_types,
        }


class LLMAdapter(Protocol):
    def propose_next_action(self, *, context: LLMContext) -> str:
        """Return a JSON string describing the proposed next action."""

        raise NotImplementedError
