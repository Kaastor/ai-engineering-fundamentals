from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from learning_compiler.agent.journal import JournalRecord, RunJournal
from learning_compiler.agent.policy import Decision, Policy
from learning_compiler.agent.stop import StopOutcome, StopReason
from learning_compiler.agent.types import Action, EffectType, Evidence, Intent, Observation, ObservationSource
from learning_compiler.util.hashing import stable_sha256_hex


StateT = TypeVar("StateT")


class Environment(Protocol[StateT]):
    """An environment the agent can interact with.

    This is deliberately small: an environment is just "a thing you can observe and act upon",
    plus a verifier.
    """

    def observe(self, *, state: StateT) -> Observation: ...
    def transition(self, *, state: StateT, action: Action) -> tuple[StateT, Observation]: ...
    def verify(self, *, state: StateT, intent: Intent) -> Evidence: ...
    def is_terminal(self, *, state: StateT, intent: Intent, evidence: Evidence) -> bool: ...


@dataclass(frozen=True, slots=True)
class MediationResult:
    allowed: bool
    reason: str


class ActionMediator(Protocol):
    """System-side policy enforcement (not model-side)."""

    def mediate(self, *, intent: Intent, action: Action, step_index: int) -> MediationResult: ...


@dataclass(frozen=True, slots=True)
class RunResult(Generic[StateT]):
    final_state: StateT
    stop: StopOutcome
    journal: RunJournal[StateT]
    side_effects_used: int


class AllowAllMediator:
    def mediate(self, *, intent: Intent, action: Action, step_index: int) -> MediationResult:
        return MediationResult(allowed=True, reason="allowed")


def run_agent(
    *,
    intent: Intent,
    initial_state: StateT,
    policy: Policy[StateT],
    environment: Environment[StateT],
    rng: random.Random,
    run_id: str,
    mediator: ActionMediator | None = None,
) -> RunResult[StateT]:
    """Run an agent loop with explicit budgets and journaling.

    The agent (policy) proposes; the system (mediator + environment) disposes.
    """

    med = mediator or AllowAllMediator()

    journal: RunJournal[StateT] = RunJournal(run_id=run_id)
    state = initial_state
    side_effects_used = 0

    for step_index in range(intent.budget.max_steps):
        state_digest = stable_sha256_hex(state)

        observation = environment.observe(state=state)
        decision: Decision[StateT]
        try:
            decision = policy.decide(intent=intent, state=state, observation=observation, rng=rng)
        except Exception as exc:  # noqa: BLE001 - lab code wants the exception surfaced as outcome
            stop = StopOutcome(reason=StopReason.POLICY_ERROR, detail=f"{type(exc).__name__}: {exc}")
            return RunResult(
                final_state=state,
                stop=stop,
                journal=journal,
                side_effects_used=side_effects_used,
            )

        if decision.stop or decision.action is None:
            record = JournalRecord(
                step_index=step_index,
                state_digest=state_digest,
                observation=observation,
                decision_rationale=decision.rationale,
                proposed_action=decision.action,
                action_observation=None,
                evidence=None,
                next_state_digest=stable_sha256_hex(decision.next_state),
            )
            journal.append(record)
            stop = StopOutcome(reason=StopReason.NO_ACTION, detail="policy stopped or proposed no action")
            return RunResult(
                final_state=decision.next_state,
                stop=stop,
                journal=journal,
                side_effects_used=side_effects_used,
            )

        # Budget: side effects.
        if decision.action.effect == EffectType.WRITE:
            if side_effects_used + 1 > intent.budget.max_side_effects:
                stop = StopOutcome(
                    reason=StopReason.BUDGET_EXHAUSTED,
                    detail="side-effect budget exhausted",
                )
                return RunResult(
                    final_state=state,
                    stop=stop,
                    journal=journal,
                    side_effects_used=side_effects_used,
                )
            side_effects_used += 1

        # System mediation (policy enforcement outside the agent).
        mediation = med.mediate(intent=intent, action=decision.action, step_index=step_index)
        if not mediation.allowed:
            blocked_obs = Observation(
                source=ObservationSource.SYSTEM,
                text=f"Action blocked by system policy: {mediation.reason}",
            )
            evidence = Evidence(ok=False, text="blocked by mediator")
            record = JournalRecord(
                step_index=step_index,
                state_digest=state_digest,
                observation=observation,
                decision_rationale=decision.rationale,
                proposed_action=decision.action,
                action_observation=blocked_obs,
                evidence=evidence,
                next_state_digest=stable_sha256_hex(decision.next_state),
            )
            journal.append(record)
            stop = StopOutcome(reason=StopReason.ENVIRONMENT_ERROR, detail="action blocked")
            return RunResult(
                final_state=decision.next_state,
                stop=stop,
                journal=journal,
                side_effects_used=side_effects_used,
            )

        # Execute in the environment.
        try:
            next_state, action_observation = environment.transition(state=decision.next_state, action=decision.action)
        except Exception as exc:  # noqa: BLE001
            stop = StopOutcome(
                reason=StopReason.ENVIRONMENT_ERROR, detail=f"{type(exc).__name__}: {exc}"
            )
            return RunResult(
                final_state=decision.next_state,
                stop=stop,
                journal=journal,
                side_effects_used=side_effects_used,
            )

        evidence = environment.verify(state=next_state, intent=intent)
        record = JournalRecord(
            step_index=step_index,
            state_digest=state_digest,
            observation=observation,
            decision_rationale=decision.rationale,
            proposed_action=decision.action,
            action_observation=action_observation,
            evidence=evidence,
            next_state_digest=stable_sha256_hex(next_state),
        )
        journal.append(record)

        if environment.is_terminal(state=next_state, intent=intent, evidence=evidence):
            stop = StopOutcome(reason=StopReason.GOAL_REACHED, detail="environment terminal condition met")
            return RunResult(
                final_state=next_state,
                stop=stop,
                journal=journal,
                side_effects_used=side_effects_used,
            )

        state = next_state

    stop = StopOutcome(reason=StopReason.BUDGET_EXHAUSTED, detail="step budget exhausted")
    return RunResult(
        final_state=state,
        stop=stop,
        journal=journal,
        side_effects_used=side_effects_used,
    )
