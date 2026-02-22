from __future__ import annotations

from pathlib import Path
import random

from learning_compiler.agent.executor import AgentExecutor
from learning_compiler.agent.hypotheses import Hypotheses
from learning_compiler.agent.orchestration import (
    apply_uncertainty_gate,
    at_least,
    finalize,
    make_decider,
    make_reliable_tools,
    step_snapshot,
    update_hypotheses_from_new_observations,
)
from learning_compiler.agent.policy import Policy, PolicyDecision
from learning_compiler.agent.state import AgentProfile, AgentResult, AgentRunConfig, AgentState, ResultStatus
from learning_compiler.agent.verifier import Verifier
from learning_compiler.journal.models import JournalKind
from learning_compiler.journal.writer import RunJournalWriter
from learning_compiler.sim.faults import FaultPlan
from learning_compiler.sim.scenario import ScenarioConfig, generate_scenario
from learning_compiler.sim.tools import RawSimTools
from learning_compiler.types import IncidentType, ScenarioSeed
from learning_compiler.utils.hashing import make_run_id
from learning_compiler.agent.actions import is_side_effect, ObserveMetrics


def run_agent(
    *, config: AgentRunConfig, out_dir: Path, incident_override: IncidentType | None = None
) -> AgentResult:
    """Run SimOpsBot for one seeded scenario and write a JSONL journal."""

    config.validate()
    out_dir.mkdir(parents=True, exist_ok=True)

    scenario = generate_scenario(ScenarioConfig(seed=ScenarioSeed(config.seed), incident_override=incident_override))

    run_id = make_run_id(seed=config.seed, profile=config.profile.value)
    journal_path = out_dir / f"run_seed{config.seed:06d}_{config.profile.value}.jsonl"

    faults = FaultPlan(seed=config.seed)
    raw_tools = RawSimTools(world=scenario.world, fault_plan=faults, seed=config.seed)
    tools = make_reliable_tools(raw=raw_tools, profile=config.profile)

    rng = random.Random(config.seed ^ 0xA6E17)
    state = AgentState(rng=rng, run_id=run_id, profile=config.profile, budget=config.budget)

    hypotheses = Hypotheses() if at_least(config.profile, AgentProfile.WEEK3) else None
    policy = Policy() if at_least(config.profile, AgentProfile.WEEK5) else None

    with RunJournalWriter(journal_path, run_id=run_id) as journal:
        executor = AgentExecutor(tools=tools, journal=journal)
        verifier = Verifier(tools=tools, journal=journal) if at_least(config.profile, AgentProfile.WEEK4) else None
        decider = make_decider(profile=config.profile, seed=config.seed)

        for step in range(1, config.budget.max_steps + 1):
            state.step_id = step
            journal.log(step_id=state.step_id, kind=JournalKind.STEP_START, payload=step_snapshot(state=state, hypotheses=hypotheses))

            if state.tool_calls >= state.budget.max_tool_calls:
                return finalize(
                    journal=journal,
                    state=state,
                    seed=config.seed,
                    status=ResultStatus.ABSTAINED,
                    summary="Tool-call budget exhausted.",
                    journal_path=journal_path,
                )

            decision = decider.decide(state=state, hypotheses=hypotheses)

            if decision.model_proposal is not None:
                journal.log(step_id=state.step_id, kind=JournalKind.MODEL_PROPOSAL, payload={"proposal": decision.model_proposal})
                journal.log(
                    step_id=state.step_id,
                    kind=JournalKind.VALIDATION,
                    payload={
                        "valid": decision.validation_error is None,
                        "error": decision.validation_error,
                        "chosen_action": decision.action.to_json(),
                    },
                )

            action = decision.action

            # Meeting 3: ask/observe-more under low confidence.
            action, gate_payload = apply_uncertainty_gate(state=state, action=action, hypotheses=hypotheses)
            if gate_payload is not None:
                journal.log(step_id=state.step_id, kind=JournalKind.POLICY, payload=gate_payload)

            # Meeting 5: policy guardrails.
            if policy is not None:
                have_any_metrics = any(obs.get("tool") == "get_metrics" for obs in state.observations)
                best_h = hypotheses.best() if hypotheses is not None else None
                outcome = policy.evaluate(
                    action=action,
                    side_effect_actions_so_far=state.side_effect_actions,
                    max_side_effect_actions=state.budget.max_side_effect_actions,
                    best_hypothesis=best_h,
                    have_any_metrics=have_any_metrics,
                )
                journal.log(
                    step_id=state.step_id,
                    kind=JournalKind.POLICY,
                    payload={
                        "policy": "guardrails",
                        "decision": outcome.decision.value,
                        "reason": outcome.reason,
                        "action": action.to_json(),
                        "fallback": outcome.fallback.to_json() if outcome.fallback is not None else None,
                    },
                )
                if outcome.decision is PolicyDecision.BLOCK:
                    state.unsafe_action_attempts += 1
                    action = outcome.fallback or ObserveMetrics(service="api", window_minutes=5)

            before_obs = len(state.observations)
            before_evid = len(state.evidence_ids)
            exec_result = executor.execute(action=action, state=state)
            update_hypotheses_from_new_observations(
                hypotheses=hypotheses, state=state, before_obs=before_obs, before_evid=before_evid
            )

            if exec_result.terminal:
                status = ResultStatus.ABSTAINED if exec_result.terminal_status == "abstained" else ResultStatus.FAILED
                summary = exec_result.terminal_summary or "Stopped."
                return finalize(
                    journal=journal,
                    state=state,
                    seed=config.seed,
                    status=status,
                    summary=summary,
                    journal_path=journal_path,
                )

            if verifier is not None and is_side_effect(action):
                ver = verifier.verify_recovery(state=state)
                if ver.recovered:
                    return finalize(
                        journal=journal,
                        state=state,
                        seed=config.seed,
                        status=ResultStatus.RESOLVED,
                        summary="Recovered and verified.",
                        journal_path=journal_path,
                    )

        return finalize(
            journal=journal,
            state=state,
            seed=config.seed,
            status=ResultStatus.ABSTAINED,
            summary="Step budget exhausted.",
            journal_path=journal_path,
        )
