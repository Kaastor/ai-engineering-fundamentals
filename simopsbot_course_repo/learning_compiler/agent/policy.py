from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from learning_compiler.agent.actions import (
    ActRestart,
    ActRollback,
    Action,
    AskUser,
    ObserveHealth,
    ObserveLogs,
    ObserveMetrics,
    RunbookSearch,
)
from learning_compiler.agent.hypotheses import Hypothesis
from learning_compiler.types import ConfidenceLevel, ServiceName


class PolicyDecision(StrEnum):
    ALLOW = "allow"
    BLOCK = "block"


@dataclass(slots=True, frozen=True)
class PolicyOutcome:
    decision: PolicyDecision
    reason: str
    fallback: Action | None = None


@dataclass(slots=True, frozen=True)
class Policy:
    """Tiny policy guardrail layer (Meeting 5).

    Policy is enforced *outside the model*.

    Intentional teaching choices:
    - rollback(db, ...) is forbidden (too dangerous in real ops)
    - side-effect actions are rate-limited
    - if blocked, degrade safely (observe/ask/stop)
    """

    allowed_services: tuple[ServiceName, ...] = ("api", "db")

    def evaluate(
        self,
        *,
        action: Action,
        side_effect_actions_so_far: int,
        max_side_effect_actions: int,
        best_hypothesis: Hypothesis | None,
        have_any_metrics: bool,
    ) -> PolicyOutcome:
        # Always allow observation + asking.
        if isinstance(action, (ObserveMetrics, ObserveLogs, ObserveHealth, RunbookSearch, AskUser)):
            return PolicyOutcome(decision=PolicyDecision.ALLOW, reason="allowed")

        # Rate limit side effects.
        if side_effect_actions_so_far >= max_side_effect_actions:
            return PolicyOutcome(
                decision=PolicyDecision.BLOCK,
                reason="side-effect budget exceeded",
                fallback=AskUser(question="Side-effect budget exceeded. Provide guidance or increase budget."),
            )

        if isinstance(action, ActRestart):
            if action.service not in self.allowed_services:
                return PolicyOutcome(
                    decision=PolicyDecision.BLOCK,
                    reason=f"service not allowed: {action.service}",
                    fallback=ObserveHealth(service="api"),
                )
            return PolicyOutcome(decision=PolicyDecision.ALLOW, reason="restart allowed")

        if isinstance(action, ActRollback):
            if action.service != "api":
                return PolicyOutcome(
                    decision=PolicyDecision.BLOCK,
                    reason="rollback is only allowed for api (db rollback forbidden)",
                    fallback=ObserveMetrics(service="db", window_minutes=5),
                )
            if not have_any_metrics:
                return PolicyOutcome(
                    decision=PolicyDecision.BLOCK,
                    reason="rollback requires at least one metrics observation",
                    fallback=ObserveMetrics(service="api", window_minutes=5),
                )
            if best_hypothesis is not None and best_hypothesis.confidence is ConfidenceLevel.LOW:
                return PolicyOutcome(
                    decision=PolicyDecision.BLOCK,
                    reason="low confidence: rollback requires medium/high confidence",
                    fallback=ObserveLogs(service="api", n=10),
                )
            return PolicyOutcome(decision=PolicyDecision.ALLOW, reason="rollback allowed")

        # FINAL action is handled by loop; default deny for unknown.
        return PolicyOutcome(
            decision=PolicyDecision.BLOCK,
            reason="unknown or forbidden action",
            fallback=ObserveMetrics(service="api", window_minutes=5),
        )
