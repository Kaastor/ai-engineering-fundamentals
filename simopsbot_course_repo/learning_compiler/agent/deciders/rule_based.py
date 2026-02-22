from __future__ import annotations

from learning_compiler.agent.actions import (
    ActRestart,
    ActRollback,
    ObserveHealth,
    ObserveLogs,
    ObserveMetrics,
    RunbookSearch,
)
from learning_compiler.agent.deciders.base import Decision
from learning_compiler.agent.hypotheses import Hypotheses
from learning_compiler.agent.state import AgentState
from learning_compiler.types import JSONValue


class RuleBasedDecider:
    """Week 1 decider: a simple, explicit rule-based policy.

    This is intentionally not "smart".
    It exists to teach the loop + evidence discipline without GenAI yet.
    """

    def decide(self, *, state: AgentState, hypotheses: Hypotheses | None) -> Decision:
        _ = hypotheses  # unused in week1

        # 1) Gather baseline metrics if missing.
        api_metrics = _last_obs(state=state, tool="get_metrics", service="api")
        db_metrics = _last_obs(state=state, tool="get_metrics", service="db")
        if api_metrics is None:
            return Decision(action=ObserveMetrics(service="api", window_minutes=5))
        if db_metrics is None:
            return Decision(action=ObserveMetrics(service="db", window_minutes=5))

        # 2) If API error rate is high, rollback API.
        api_err = api_metrics.get("error_rate")
        if isinstance(api_err, (int, float)) and float(api_err) > 0.25:
            return Decision(action=ActRollback(service="api", version="v1"))

        # 3) If DB latency is high, restart DB.
        db_lat = db_metrics.get("latency_ms")
        if isinstance(db_lat, (int, float)) and float(db_lat) > 300.0:
            return Decision(action=ActRestart(service="db"))

        # 4) Look for timeouts in logs.
        api_logs = _last_obs(state=state, tool="tail_logs", service="api")
        if api_logs is None:
            return Decision(action=ObserveLogs(service="api", n=10))
        lines = api_logs.get("lines")
        if isinstance(lines, list) and any(
            isinstance(line, str) and "timeout" in line.lower() for line in lines
        ):
            return Decision(action=ActRestart(service="api"))

        # 5) If still unsure, use runbooks or health as extra evidence.
        if _last_obs(state=state, tool="runbook_search", service=None) is None:
            return Decision(action=RunbookSearch(query="incident response api db"))

        return Decision(action=ObserveHealth(service="api"))


def _last_obs(
    *, state: AgentState, tool: str, service: str | None
) -> dict[str, JSONValue] | None:
    for obs in reversed(state.observations):
        if obs.get("tool") != tool:
            continue
        if service is not None and obs.get("service") != service:
            continue
        return obs
    return None
