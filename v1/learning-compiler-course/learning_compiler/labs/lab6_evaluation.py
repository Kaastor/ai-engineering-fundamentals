from __future__ import annotations

import random
from dataclasses import dataclass

from learning_compiler.agent.loop import Environment, run_agent
from learning_compiler.agent.policy import Decision, Policy
from learning_compiler.agent.stop import StopReason
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
from learning_compiler.evaluation.adversarial import AllowlistMediator, SecurityPolicy
from learning_compiler.evaluation.suite import EvalCase, EvalOutcome, run_suite
from learning_compiler.planning.gridworld import GridPos, GridWorld, manhattan
from learning_compiler.planning.search import a_star_search, uniform_cost_search
from learning_compiler.reliability.idempotency import IdempotencyStore
from learning_compiler.uncertainty.belief import Box, SensorReading, initial_belief, update_belief


@dataclass(frozen=True, slots=True)
class DummyState:
    x: int = 0


class DummyEnv(Environment[DummyState]):
    def observe(self, *, state: DummyState) -> Observation:
        return Observation(source=ObservationSource.ENVIRONMENT, text=f"dummy_state={state.x}")

    def transition(self, *, state: DummyState, action: Action) -> tuple[DummyState, Observation]:
        raise RuntimeError("DummyEnv.transition should not be called in the blocked-action test")

    def verify(self, *, state: DummyState, intent: Intent) -> Evidence:
        return Evidence(ok=False, text="unused")

    def is_terminal(self, *, state: DummyState, intent: Intent, evidence: Evidence) -> bool:
        return False


class BadPolicy(Policy[DummyState]):
    def decide(
        self,
        *,
        intent: Intent,
        state: DummyState,
        observation: Observation,
        rng: random.Random,
    ) -> Decision[DummyState]:
        _ = observation
        _ = rng
        action = Action(
            kind=ActionKind.TOOL,
            effect=EffectType.WRITE,
            name="charge_card",
            params=(("amount_cents", "999999"),),
        )
        return Decision(next_state=state, action=action, rationale="Definitely do the scary thing.")


def run(*, seed: int) -> str:
    cases = [
        EvalCase(name="Planning: A* matches UCS cost on GridWorld", run=_case_astar_matches_ucs),
        EvalCase(name="Uncertainty: Bayes update moves probability mass", run=_case_bayes_update),
        EvalCase(name="Reliability: idempotency prevents double side effects", run=_case_idempotency),
        EvalCase(name="Security: allowlist mediator blocks oversized charge", run=lambda: _case_mediator_blocks(seed=seed)),
    ]

    suite = run_suite(cases)

    lines: list[str] = []
    lines.append("# Lab 6 — Evaluation: the scientific method for AI systems")
    lines.append("")
    lines.append(suite.to_markdown())
    lines.append("")
    lines.append("Interpretation:")
    lines.append("- Specs imply tests.")
    lines.append("- Tests imply regression gates.")
    lines.append("- Regression gates imply you can improve systems without lying to yourself.")

    return "\n".join(lines)


def _case_astar_matches_ucs() -> EvalOutcome:
    world = GridWorld(
        width=6,
        height=4,
        walls=frozenset({GridPos(2, 0), GridPos(2, 1), GridPos(2, 2)}),
        start=GridPos(0, 0),
        goal=GridPos(5, 3),
    )
    problem = world.as_problem()

    ucs = uniform_cost_search(problem)
    astar = a_star_search(problem, heuristic=lambda s: float(manhattan(s, world.goal)))

    passed = ucs.found and astar.found and abs(ucs.cost - astar.cost) < 1e-9
    details = "A* cost equals UCS cost (admissible heuristic)." if passed else "Costs differ or no path found."
    return EvalOutcome(
        passed=passed,
        score=1.0 if passed else 0.0,
        details=details,
        evidence=(
            ("ucs_cost", f"{ucs.cost:.1f}"),
            ("astar_cost", f"{astar.cost:.1f}"),
            ("ucs_steps", str(len(ucs.plan))),
            ("astar_steps", str(len(astar.plan))),
        ),
    )


def _case_bayes_update() -> EvalOutcome:
    prior = initial_belief()
    posterior = update_belief(prior=prior, reading=SensorReading.SAYS_A, accuracy=0.75)

    p_a = posterior.prob(Box.A)
    passed = abs(p_a - 0.75) < 1e-9
    details = (
        "Posterior P(A|says_A)=0.75 given uniform prior and 0.75 sensor accuracy."
        if passed
        else "Unexpected posterior."
    )
    return EvalOutcome(
        passed=passed,
        score=p_a,
        details=details,
        evidence=(("posterior_P(A)", f"{p_a:.6f}"),),
    )


def _case_idempotency() -> EvalOutcome:
    store: IdempotencyStore[int] = IdempotencyStore()
    counter = {"calls": 0}

    def op() -> int:
        counter["calls"] += 1
        return 123

    r1 = store.run(key="k1", operation=op)
    r2 = store.run(key="k1", operation=op)

    passed = r1.ok and r2.ok and r1.value == 123 and r2.value == 123 and counter["calls"] == 1
    details = "Same key returns same result without re-executing side effects." if passed else "Idempotency invariant broken."
    return EvalOutcome(
        passed=passed,
        score=1.0 if passed else 0.0,
        details=details,
        evidence=(("op_calls", str(counter["calls"])),),
    )


def _case_mediator_blocks(*, seed: int) -> EvalOutcome:
    rng = random.Random(seed)

    intent = Intent(goal="Charge a card", budget=Budget(max_steps=3, max_side_effects=1))
    policy = BadPolicy()
    env = DummyEnv()
    mediator = AllowlistMediator(
        policy=SecurityPolicy(allowed_tool_names=frozenset({"charge_card"}), max_charge_cents=2_500)
    )

    result = run_agent(
        intent=intent,
        initial_state=DummyState(),
        policy=policy,
        environment=env,
        rng=rng,
        run_id=f"lab6_security_seed{seed}",
        mediator=mediator,
    )

    blocked = any(
        "blocked" in rec.action_observation.text.lower()
        for rec in result.journal.records()
        if rec.action_observation is not None
    )
    passed = result.stop.reason == StopReason.ENVIRONMENT_ERROR and blocked
    details = "Mediator blocked a dangerous proposed action." if passed else "Action was not blocked as expected."
    return EvalOutcome(
        passed=passed,
        score=1.0 if passed else 0.0,
        details=details,
        evidence=(("stop_reason", result.stop.reason.value),),
    )
