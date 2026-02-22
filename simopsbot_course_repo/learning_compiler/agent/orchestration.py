from __future__ import annotations

from pathlib import Path

from learning_compiler.agent.actions import (
    Action,
    Final,
    ObserveLogs,
    ObserveMetrics,
)
from learning_compiler.agent.deciders.base import Decider
from learning_compiler.agent.deciders.llm_based import LLMBasedDecider
from learning_compiler.agent.deciders.rule_based import RuleBasedDecider
from learning_compiler.agent.hypotheses import Hypotheses
from learning_compiler.agent.state import AgentProfile, AgentResult, AgentState, ResultStatus
from learning_compiler.journal.models import JournalKind
from learning_compiler.journal.writer import RunJournalWriter
from learning_compiler.llm.fake_model import FakeLLM
from learning_compiler.sim.tools import RawSimTools
from learning_compiler.types import ConfidenceLevel, JSONValue


def at_least(profile: AgentProfile, target: AgentProfile) -> bool:
    return _profile_rank(profile) >= _profile_rank(target)


def make_decider(*, profile: AgentProfile, seed: int) -> Decider:
    if profile is AgentProfile.WEEK1:
        return RuleBasedDecider()
    llm = FakeLLM(seed=seed)
    scrub = at_least(profile, AgentProfile.WEEK5)
    return LLMBasedDecider(llm=llm, scrub_untrusted=scrub)


def make_reliable_tools(*, raw: RawSimTools, profile: AgentProfile):
    from learning_compiler.agent.tools_wrapped import ReliableTools

    max_attempts = 3 if at_least(profile, AgentProfile.WEEK4) else 1
    return ReliableTools(raw=raw, max_attempts=max_attempts)


def step_snapshot(*, state: AgentState, hypotheses: Hypotheses | None) -> dict[str, JSONValue]:
    snap: dict[str, JSONValue] = {
        "step_id": state.step_id,
        "tool_calls": state.tool_calls,
        "side_effect_actions": state.side_effect_actions,
        "budget": {
            "max_steps": state.budget.max_steps,
            "max_tool_calls": state.budget.max_tool_calls,
            "max_side_effect_actions": state.budget.max_side_effect_actions,
        },
    }
    if hypotheses is not None:
        snap["hypotheses"] = [
            {
                "cause": h.cause.value,
                "confidence": h.confidence.value,
                "evidence_ids": list(h.evidence_ids),
            }
            for h in hypotheses.top(k=3)
        ]
    return snap


def apply_uncertainty_gate(
    *, state: AgentState, action: Action, hypotheses: Hypotheses | None
) -> tuple[Action, dict[str, JSONValue] | None]:
    """Meeting 3: override risky actions under low confidence."""

    if hypotheses is None:
        return action, None
    if not _is_side_effect(action):
        return action, None

    best = hypotheses.best()
    if best.confidence is not ConfidenceLevel.LOW:
        return action, None

    # Suggest a safer, evidence-gathering action.
    have_logs = any(obs.get("tool") == "tail_logs" for obs in state.observations)
    fallback: Action = ObserveMetrics(service="api", window_minutes=5) if have_logs else ObserveLogs(service="api", n=10)
    payload: dict[str, JSONValue] = {
        "policy": "uncertainty_gate",
        "decision": "override",
        "reason": "low confidence; gathering more evidence",
        "fallback_action": fallback.to_json(),
        "best_hypothesis": {
            "cause": best.cause.value,
            "confidence": best.confidence.value,
            "evidence_ids": list(best.evidence_ids),
        },
    }
    return fallback, payload


def update_hypotheses_from_new_observations(
    *, hypotheses: Hypotheses | None, state: AgentState, before_obs: int, before_evid: int
) -> None:
    if hypotheses is None:
        return
    new_obs = state.observations[before_obs:]
    new_evid = state.evidence_ids[before_evid:]
    for obs, evid in zip(new_obs, new_evid, strict=True):
        hypotheses.update_from_observation(obs=obs, evidence_event_id=evid)


def finalize(
    *,
    journal: RunJournalWriter,
    state: AgentState,
    seed: int,
    status: ResultStatus,
    summary: str,
    journal_path: Path,
) -> AgentResult:
    final = Final(summary=summary, evidence_refs=tuple(state.evidence_ids))
    journal.log(step_id=state.step_id, kind=JournalKind.FINAL, payload=final.to_json())
    return AgentResult(
        run_id=state.run_id,
        profile=state.profile,
        seed=seed,
        status=status,
        steps=state.step_id,
        final_summary=summary,
        journal_path=journal_path,
        unsafe_action_attempts=state.unsafe_action_attempts,
    )


def _profile_rank(profile: AgentProfile) -> int:
    return {
        AgentProfile.WEEK1: 1,
        AgentProfile.WEEK2: 2,
        AgentProfile.WEEK3: 3,
        AgentProfile.WEEK4: 4,
        AgentProfile.WEEK5: 5,
    }[profile]


def _is_side_effect(action: Action) -> bool:
    from learning_compiler.agent.actions import is_side_effect

    return is_side_effect(action)
