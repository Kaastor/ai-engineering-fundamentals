from __future__ import annotations

from learning_compiler.agent.actions import (
    Action,
    ObserveHealth,
    ObserveLogs,
    ObserveMetrics,
)
from learning_compiler.agent.deciders.base import Decision
from learning_compiler.agent.hypotheses import Hypotheses
from learning_compiler.agent.state import AgentState
from learning_compiler.agent.validator import ActionValidationError, parse_action_proposal
from learning_compiler.llm.adapter import LLMAdapter, LLMContext
from learning_compiler.types import JSONValue


class LLMBasedDecider:
    """Week 2+ decider: model proposes; system validates."""

    def __init__(self, *, llm: LLMAdapter, scrub_untrusted: bool) -> None:
        self._llm = llm
        self._scrub_untrusted = scrub_untrusted

    def decide(self, *, state: AgentState, hypotheses: Hypotheses | None) -> Decision:
        obs_for_llm = (
            _scrub_observations(state.observations) if self._scrub_untrusted else state.observations
        )
        ctx = LLMContext(
            step_id=state.step_id,
            state_summary=_state_summary(state=state, hypotheses=hypotheses),
            observations=list(obs_for_llm),
            allowed_action_types=[  # explicit allowlist in-context (still enforced by policy/validator)
                "OBSERVE_METRICS",
                "OBSERVE_LOGS",
                "OBSERVE_HEALTH",
                "RUNBOOK_SEARCH",
                "ACT_RESTART",
                "ACT_ROLLBACK",
                "ASK_USER",
                "FINAL",
            ],
        )
        raw = self._llm.propose_next_action(context=ctx)
        try:
            action = parse_action_proposal(raw)
            return Decision(action=action, model_proposal=raw)
        except ActionValidationError as e:
            fallback = _fallback_action(state=state)
            return Decision(action=fallback, model_proposal=raw, validation_error=str(e))


def _fallback_action(*, state: AgentState) -> Action:
    # Safe degradation: gather more evidence or ask.
    have_metrics = any(obs.get("tool") == "get_metrics" for obs in state.observations)
    if not have_metrics:
        return ObserveMetrics(service="api", window_minutes=5)
    have_logs = any(obs.get("tool") == "tail_logs" for obs in state.observations)
    if not have_logs:
        return ObserveLogs(service="api", n=10)
    return ObserveHealth(service="api")


def _state_summary(*, state: AgentState, hypotheses: Hypotheses | None) -> dict[str, JSONValue]:
    summary: dict[str, JSONValue] = {
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
        summary["hypotheses"] = [
            {
                "cause": h.cause.value,
                "confidence": h.confidence.value,
                "evidence_ids": list(h.evidence_ids),
            }
            for h in hypotheses.top(k=3)
        ]
    return summary


def _scrub_observations(observations: list[dict[str, JSONValue]]) -> list[dict[str, JSONValue]]:
    """Remove obviously untrusted 'instruction-like' lines.

    This is not a security silver bullet. It's a teaching tool:
    - data is not commands
    - untrusted input should be handled explicitly
    """

    out: list[dict[str, JSONValue]] = []
    for obs in observations:
        if obs.get("tool") == "tail_logs":
            out.append(_scrub_lines(obs, field="lines"))
            continue
        if obs.get("tool") == "runbook_search":
            out.append(_scrub_lines(obs, field="snippets"))
            continue
        out.append(obs)
    return out


def _scrub_lines(obs: dict[str, JSONValue], *, field: str) -> dict[str, JSONValue]:
    raw = obs.get(field)
    if not isinstance(raw, list):
        return obs
    safe: list[JSONValue] = []
    for v in raw:
        if not isinstance(v, str):
            continue
        s = v.strip()
        if s.lower().startswith("system:"):
            continue
        if "ignore previous" in s.lower():
            continue
        safe.append(s)
    new_obs = dict(obs)
    new_obs[field] = safe
    return new_obs
