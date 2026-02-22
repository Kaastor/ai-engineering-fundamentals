from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
from typing import Protocol

from learning_compiler.agent.state import AgentState
from learning_compiler.agent.tools_wrapped import ReliableTools
from learning_compiler.journal.models import JournalKind
from learning_compiler.journal.writer import RunJournalWriter
from learning_compiler.sim.faults import ToolError
from learning_compiler.types import JSONValue, ToolName


@dataclass(slots=True, frozen=True)
class VerificationResult:
    recovered: bool
    reason: str
    evidence_event_ids: tuple[str, ...]


class _Jsonable(Protocol):
    def to_json(self) -> dict[str, JSONValue]:
        raise NotImplementedError


class Verifier:
    """Meeting 4: verification after side effects."""

    def __init__(self, *, tools: ReliableTools, journal: RunJournalWriter) -> None:
        self._tools = tools
        self._journal = journal

    def verify_recovery(self, *, state: AgentState) -> VerificationResult:
        """Verify recovery using multiple samples to tolerate noise/delay."""

        evidence_ids: list[str] = []

        api_health = self._safe_verify_obs(
            state=state,
            tool=ToolName.HEALTH_CHECK,
            call=lambda: self._tools.health_check(service="api"),
            evidence_ids=evidence_ids,
        )
        db_health = self._safe_verify_obs(
            state=state,
            tool=ToolName.HEALTH_CHECK,
            call=lambda: self._tools.health_check(service="db"),
            evidence_ids=evidence_ids,
        )

        api_samples = [
            self._safe_verify_obs(
                state=state,
                tool=ToolName.GET_METRICS,
                call=lambda: self._tools.get_metrics(service="api", window_minutes=5),
                evidence_ids=evidence_ids,
            )
            for _ in range(2)
        ]
        db_samples = [
            self._safe_verify_obs(
                state=state,
                tool=ToolName.GET_METRICS,
                call=lambda: self._tools.get_metrics(service="db", window_minutes=5),
                evidence_ids=evidence_ids,
            )
            for _ in range(2)
        ]

        if api_health is None or db_health is None:
            return VerificationResult(
                recovered=False,
                reason="verification tool error (health)",
                evidence_event_ids=tuple(evidence_ids),
            )

        api_metrics = _pick_best_api_metrics(api_samples)
        db_metrics = _pick_best_db_metrics(db_samples)
        if api_metrics is None or db_metrics is None:
            return VerificationResult(
                recovered=False,
                reason="verification tool error (metrics)",
                evidence_event_ids=tuple(evidence_ids),
            )

        # Extract numbers defensively (these came from a noisy tool layer).
        api_ok = api_health.get("status") == "ok"
        db_ok = db_health.get("status") == "ok"
        api_err = api_metrics.get("error_rate")
        api_lat = api_metrics.get("latency_ms")
        db_lat = db_metrics.get("latency_ms")

        if not (api_ok and db_ok):
            return VerificationResult(
                recovered=False,
                reason="health not ok",
                evidence_event_ids=tuple(evidence_ids),
            )

        if not (
            isinstance(api_err, (int, float))
            and isinstance(api_lat, (int, float))
            and isinstance(db_lat, (int, float))
        ):
            return VerificationResult(
                recovered=False,
                reason="missing metric fields",
                evidence_event_ids=tuple(evidence_ids),
            )

        if float(api_err) >= 0.05:
            return VerificationResult(
                recovered=False,
                reason="api error rate still high",
                evidence_event_ids=tuple(evidence_ids),
            )
        if float(api_lat) >= 200.0:
            return VerificationResult(
                recovered=False,
                reason="api latency still high",
                evidence_event_ids=tuple(evidence_ids),
            )
        if float(db_lat) >= 140.0:
            return VerificationResult(
                recovered=False,
                reason="db latency still high",
                evidence_event_ids=tuple(evidence_ids),
            )

        return VerificationResult(recovered=True, reason="recovered", evidence_event_ids=tuple(evidence_ids))


    def _safe_verify_obs(
        self,
        *,
        state: AgentState,
        tool: ToolName,
        call: Callable[[], _Jsonable],
        evidence_ids: list[str],
    ) -> dict[str, JSONValue] | None:
        state.bump_tool_calls(1)
        try:
            obs = call()
        except ToolError as e:
            self._journal.log(
                step_id=state.step_id,
                kind=JournalKind.ERROR,
                payload={"tool": tool.value, "error": str(e)},
            )
            return None
        obs_json = obs.to_json()
        event_id = self._journal.log(
            step_id=state.step_id,
            kind=JournalKind.VERIFY,
            payload={"observation": obs_json},
        )
        state.record_observation(obs_json, evidence_event_id=event_id)
        evidence_ids.append(event_id)
        return obs_json


def _pick_best_api_metrics(samples: list[dict[str, JSONValue] | None]) -> dict[str, JSONValue] | None:
    """Pick the best API metrics sample (lowest error_rate)."""

    present = [s for s in samples if s is not None]
    if not present:
        return None

    def key(sample: dict[str, JSONValue]) -> float:
        v = sample.get("error_rate")
        if isinstance(v, (int, float)):
            return float(v)
        return 1.0

    return min(present, key=key)


def _pick_best_db_metrics(samples: list[dict[str, JSONValue] | None]) -> dict[str, JSONValue] | None:
    """Pick the best DB metrics sample (lowest latency_ms)."""

    present = [s for s in samples if s is not None]
    if not present:
        return None

    def key(sample: dict[str, JSONValue]) -> float:
        v = sample.get("latency_ms")
        if isinstance(v, (int, float)):
            return float(v)
        return 1e9

    return min(present, key=key)
