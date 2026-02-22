from __future__ import annotations

from dataclasses import dataclass

from learning_compiler.agent.actions import (
    ActRestart,
    ActRollback,
    Action,
    AskUser,
    Final,
    ObserveHealth,
    ObserveLogs,
    ObserveMetrics,
    RunbookSearch,
)
from learning_compiler.agent.tools_wrapped import ReliableTools, make_idempotency_key
from learning_compiler.journal.models import JournalKind
from learning_compiler.journal.writer import RunJournalWriter
from learning_compiler.sim.faults import ToolError
from learning_compiler.types import JSONValue, ToolName
from learning_compiler.agent.state import AgentState


@dataclass(slots=True, frozen=True)
class ExecutorResult:
    terminal: bool
    terminal_status: str | None = None  # resolved/abstained/failed chosen by loop
    terminal_summary: str | None = None


class AgentExecutor:
    def __init__(self, *, tools: ReliableTools, journal: RunJournalWriter) -> None:
        self._tools = tools
        self._journal = journal

    def execute(self, *, action: Action, state: AgentState) -> ExecutorResult:
        if isinstance(action, ObserveMetrics):
            return self._observe_metrics(action=action, state=state)
        if isinstance(action, ObserveLogs):
            return self._observe_logs(action=action, state=state)
        if isinstance(action, ObserveHealth):
            return self._observe_health(action=action, state=state)
        if isinstance(action, RunbookSearch):
            return self._observe_runbook(action=action, state=state)
        if isinstance(action, ActRestart):
            return self._act_restart(action=action, state=state)
        if isinstance(action, ActRollback):
            return self._act_rollback(action=action, state=state)
        if isinstance(action, AskUser):
            self._journal.log(
                step_id=state.step_id,
                kind=JournalKind.ACTION,
                payload={"action": action.to_json()},
            )
            return ExecutorResult(terminal=True, terminal_status="abstained", terminal_summary=action.question)
        if isinstance(action, Final):
            self._journal.log(
                step_id=state.step_id,
                kind=JournalKind.FINAL,
                payload=action.to_json(),
            )
            return ExecutorResult(terminal=True, terminal_status="abstained", terminal_summary=action.summary)

        raise AssertionError(f"Unhandled action: {action}")

    # ---- observation helpers ----

    def _observe_metrics(self, *, action: ObserveMetrics, state: AgentState) -> ExecutorResult:
        state.bump_tool_calls(1)
        try:
            obs = self._tools.get_metrics(service=action.service, window_minutes=action.window_minutes)
        except ToolError as e:
            self._log_tool_error(state=state, tool=ToolName.GET_METRICS, error=str(e))
            return ExecutorResult(terminal=False)
        obs_json = obs.to_json()
        payload: dict[str, JSONValue] = {"observation": obs_json}
        event_id = self._journal.log(
            step_id=state.step_id,
            kind=JournalKind.OBSERVATION,
            payload=payload,
        )
        state.record_observation(obs_json, evidence_event_id=event_id)
        return ExecutorResult(terminal=False)

    def _observe_logs(self, *, action: ObserveLogs, state: AgentState) -> ExecutorResult:
        state.bump_tool_calls(1)
        try:
            obs = self._tools.tail_logs(service=action.service, n=action.n)
        except ToolError as e:
            self._log_tool_error(state=state, tool=ToolName.TAIL_LOGS, error=str(e))
            return ExecutorResult(terminal=False)
        obs_json = obs.to_json()
        payload: dict[str, JSONValue] = {"observation": obs_json}
        event_id = self._journal.log(
            step_id=state.step_id,
            kind=JournalKind.OBSERVATION,
            payload=payload,
        )
        state.record_observation(obs_json, evidence_event_id=event_id)
        return ExecutorResult(terminal=False)

    def _observe_health(self, *, action: ObserveHealth, state: AgentState) -> ExecutorResult:
        state.bump_tool_calls(1)
        try:
            obs = self._tools.health_check(service=action.service)
        except ToolError as e:
            self._log_tool_error(state=state, tool=ToolName.HEALTH_CHECK, error=str(e))
            return ExecutorResult(terminal=False)
        obs_json = obs.to_json()
        payload: dict[str, JSONValue] = {"observation": obs_json}
        event_id = self._journal.log(
            step_id=state.step_id,
            kind=JournalKind.OBSERVATION,
            payload=payload,
        )
        state.record_observation(obs_json, evidence_event_id=event_id)
        return ExecutorResult(terminal=False)

    def _observe_runbook(self, *, action: RunbookSearch, state: AgentState) -> ExecutorResult:
        state.bump_tool_calls(1)
        try:
            obs = self._tools.runbook_search(query=action.query)
        except ToolError as e:
            self._log_tool_error(state=state, tool=ToolName.RUNBOOK_SEARCH, error=str(e))
            return ExecutorResult(terminal=False)
        obs_json = obs.to_json()
        payload: dict[str, JSONValue] = {"observation": obs_json}
        event_id = self._journal.log(
            step_id=state.step_id,
            kind=JournalKind.OBSERVATION,
            payload=payload,
        )
        state.record_observation(obs_json, evidence_event_id=event_id)
        return ExecutorResult(terminal=False)

    # ---- side effects ----

    def _act_restart(self, *, action: ActRestart, state: AgentState) -> ExecutorResult:
        state.bump_side_effect_actions(1)
        key = make_idempotency_key(
            run_id=state.run_id, step_id=state.step_id, tool=ToolName.RESTART, service=action.service
        )
        result = self._tools.restart(service=action.service, idempotency_key=key)
        state.bump_tool_calls(result.tool_calls)

        attempts_json: list[JSONValue] = [a.to_json() for a in result.attempts]
        payload: dict[str, JSONValue] = {
            "action": action.to_json(),
            "idempotency_key": str(key),
            "attempts": attempts_json,
        }
        if result.receipt is not None:
            payload["receipt"] = result.receipt.to_json()
        if result.final_error is not None:
            payload["error"] = result.final_error

        self._journal.log(step_id=state.step_id, kind=JournalKind.ACTION, payload=payload)
        return ExecutorResult(terminal=False)

    def _act_rollback(self, *, action: ActRollback, state: AgentState) -> ExecutorResult:
        state.bump_side_effect_actions(1)
        key = make_idempotency_key(
            run_id=state.run_id, step_id=state.step_id, tool=ToolName.ROLLBACK, service=action.service
        )
        result = self._tools.rollback(service=action.service, version=action.version, idempotency_key=key)
        state.bump_tool_calls(result.tool_calls)

        attempts_json: list[JSONValue] = [a.to_json() for a in result.attempts]
        payload: dict[str, JSONValue] = {
            "action": action.to_json(),
            "idempotency_key": str(key),
            "attempts": attempts_json,
        }
        if result.receipt is not None:
            payload["receipt"] = result.receipt.to_json()
        if result.final_error is not None:
            payload["error"] = result.final_error

        self._journal.log(step_id=state.step_id, kind=JournalKind.ACTION, payload=payload)
        return ExecutorResult(terminal=False)

    def _log_tool_error(self, *, state: AgentState, tool: ToolName, error: str) -> None:
        self._journal.log(
            step_id=state.step_id,
            kind=JournalKind.ERROR,
            payload={"tool": tool.value, "error": error},
        )
