from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
import random

from learning_compiler.types import Budget, DEFAULT_BUDGET, JSONValue, RunId


class AgentProfile(StrEnum):
    WEEK1 = "week1"
    WEEK2 = "week2"
    WEEK3 = "week3"
    WEEK4 = "week4"
    WEEK5 = "week5"


class ResultStatus(StrEnum):
    RESOLVED = "resolved"
    ABSTAINED = "abstained"
    FAILED = "failed"


@dataclass(slots=True, frozen=True)
class AgentRunConfig:
    seed: int
    profile: AgentProfile
    budget: Budget = DEFAULT_BUDGET

    def validate(self) -> None:
        if self.seed < 0:
            raise ValueError("seed must be non-negative")
        self.budget.validate()


@dataclass(slots=True)
class AgentState:
    """Mutable agent state (explicitly passed; no globals)."""

    rng: random.Random
    run_id: RunId
    profile: AgentProfile
    budget: Budget

    step_id: int = 0
    tool_calls: int = 0
    side_effect_actions: int = 0

    # A compact memory of observations for decision-making and/or LLM context.
    observations: list[dict[str, JSONValue]] = field(default_factory=list)

    # Evidence event IDs (observation/verify events) used for final summaries.
    evidence_ids: list[str] = field(default_factory=list)

    # Policy blocks (counted for eval)
    unsafe_action_attempts: int = 0

    def record_observation(self, obs_json: dict[str, JSONValue], *, evidence_event_id: str) -> None:
        self.observations.append(obs_json)
        self.evidence_ids.append(evidence_event_id)

    def bump_tool_calls(self, n: int = 1) -> None:
        self.tool_calls += n

    def bump_side_effect_actions(self, n: int = 1) -> None:
        self.side_effect_actions += n


@dataclass(slots=True, frozen=True)
class AgentResult:
    run_id: RunId
    profile: AgentProfile
    seed: int
    status: ResultStatus
    steps: int
    final_summary: str
    journal_path: Path
    unsafe_action_attempts: int

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "run_id": str(self.run_id),
            "profile": self.profile.value,
            "seed": self.seed,
            "status": self.status.value,
            "steps": self.steps,
            "final_summary": self.final_summary,
            "journal_path": str(self.journal_path),
            "unsafe_action_attempts": self.unsafe_action_attempts,
        }
