from __future__ import annotations

import random
from dataclasses import dataclass

from learning_compiler.agent.loop import Environment, RunResult, run_agent
from learning_compiler.agent.policy import Decision, Policy
from learning_compiler.agent.types import (
    Action,
    ActionKind,
    Budget,
    EffectType,
    Evidence,
    Intent,
    Observation,
    ObservationSource,
)


@dataclass(frozen=True, slots=True)
class CounterState:
    value: int
    target: int


class CounterEnvironment(Environment[CounterState]):
    def observe(self, *, state: CounterState) -> Observation:
        return Observation(
            source=ObservationSource.ENVIRONMENT,
            text=f"counter={state.value} (target={state.target})",
        )

    def transition(self, *, state: CounterState, action: Action) -> tuple[CounterState, Observation]:
        if action.kind != ActionKind.MOVE:
            raise ValueError(f"Unsupported action kind: {action.kind}")

        delta_raw = action.param("delta")
        if delta_raw is None:
            raise ValueError("Missing delta param")
        delta = int(delta_raw)

        nxt = CounterState(value=state.value + delta, target=state.target)
        obs = Observation(
            source=ObservationSource.ENVIRONMENT,
            text=f"applied delta={delta}, counter={nxt.value}",
        )
        return nxt, obs

    def verify(self, *, state: CounterState, intent: Intent) -> Evidence:
        ok = state.value == state.target
        return Evidence(ok=ok, text="goal reached" if ok else "not yet")

    def is_terminal(self, *, state: CounterState, intent: Intent, evidence: Evidence) -> bool:
        return evidence.ok


class GreedyCounterPolicy(Policy[CounterState]):
    def decide(
        self,
        *,
        intent: Intent,
        state: CounterState,
        observation: Observation,
        rng: random.Random,
    ) -> Decision[CounterState]:
        # Deterministic, math-light "policy": step toward the target by 1 each loop.
        if state.value == state.target:
            return Decision(next_state=state, action=None, rationale="Already at target.", stop=True)

        delta = 1 if state.value < state.target else -1
        action = Action(
            kind=ActionKind.MOVE,
            effect=EffectType.COMPUTE,
            name="increment_or_decrement",
            params=(("delta", str(delta)),),
        )
        return Decision(next_state=state, action=action, rationale=f"Move counter by {delta} toward target.")


def run(*, seed: int) -> tuple[str, RunResult[CounterState]]:
    rng = random.Random(seed)
    intent = Intent(goal="Reach the target counter value.", budget=Budget(max_steps=20, max_side_effects=0))

    initial = CounterState(value=0, target=5)
    env = CounterEnvironment()
    policy = GreedyCounterPolicy()

    result = run_agent(
        intent=intent,
        initial_state=initial,
        policy=policy,
        environment=env,
        rng=rng,
        run_id=f"lab1_seed{seed}",
    )

    lines: list[str] = []
    lines.append("# Lab 1 — The Big Map: an agent loop you can debug")
    lines.append("")
    lines.append(f"Intent: {intent.goal}")
    lines.append(f"Budget: steps≤{intent.budget.max_steps}, side_effects≤{intent.budget.max_side_effects}")
    lines.append("")
    lines.append(f"Stop: {result.stop.reason.value} — {result.stop.detail}")
    lines.append(f"Trace hash: {result.journal.trace_hash()}")
    lines.append("")
    lines.append("## Journal (observe → decide → act → verify)")
    for rec in result.journal.records():
        action = "∅" if rec.proposed_action is None else f"{rec.proposed_action.name}{dict(rec.proposed_action.params)}"
        ok = "∅" if rec.evidence is None else ("ok" if rec.evidence.ok else "fail")
        lines.append(
            f"- step {rec.step_index}: obs='{rec.observation.text}' | action={action} | verify={ok}"
        )

    return "\n".join(lines), result
