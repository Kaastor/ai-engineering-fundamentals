from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from collections.abc import Callable

from learning_compiler.sim.faults import ToolError, ToolTimeout, ToolTransientError
from learning_compiler.sim.observations import (
    ActionReceipt,
    HealthObservation,
    LogsObservation,
    MetricsObservation,
    RunbookObservation,
)
from learning_compiler.sim.tools import RawSimTools
from learning_compiler.types import IdempotencyKey, JSONValue, RunId, ServiceName, ToolName
from learning_compiler.utils.hashing import stable_short_hash


class AttemptOutcome(StrEnum):
    SUCCESS = "success"
    ERROR = "error"


@dataclass(slots=True, frozen=True)
class Attempt:
    attempt_no: int
    outcome: AttemptOutcome
    error_type: str | None = None
    error_message: str | None = None

    def to_json(self) -> dict[str, JSONValue]:
        out: dict[str, JSONValue] = {"attempt_no": self.attempt_no, "outcome": self.outcome.value}
        if self.error_type is not None:
            out["error_type"] = self.error_type
        if self.error_message is not None:
            out["error_message"] = self.error_message
        return out


@dataclass(slots=True, frozen=True)
class SideEffectResult:
    receipt: ActionReceipt | None
    attempts: tuple[Attempt, ...]
    tool_calls: int
    final_error: str | None


def make_idempotency_key(*, run_id: RunId, step_id: int, tool: ToolName, service: ServiceName) -> IdempotencyKey:
    key = stable_short_hash(f"{run_id}:{step_id}:{tool.value}:{service}", length=20)
    return IdempotencyKey(key)


class ReliableTools:
    """Meeting 4: reliability wrapper for side effects.

    Adds:
    - retries for transient failures/timeouts
    - deterministic idempotency keys (so retries don't double-apply)
    """

    def __init__(self, *, raw: RawSimTools, max_attempts: int = 3) -> None:
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        self._raw = raw
        self._max_attempts = max_attempts

    # Read-only calls are passed through (no retries needed for the lab).
    def get_metrics(self, *, service: ServiceName, window_minutes: int) -> MetricsObservation:
        return self._raw.get_metrics(service=service, window_minutes=window_minutes)

    def tail_logs(self, *, service: ServiceName, n: int) -> LogsObservation:
        return self._raw.tail_logs(service=service, n=n)

    def health_check(self, *, service: ServiceName) -> HealthObservation:
        return self._raw.health_check(service=service)

    def runbook_search(self, *, query: str) -> RunbookObservation:
        return self._raw.runbook_search(query=query)

    # Side effects use retry.
    def restart(self, *, service: ServiceName, idempotency_key: IdempotencyKey) -> SideEffectResult:
        return self._retry(
            tool=ToolName.RESTART,
            attempt=lambda: self._raw.restart(service=service, idempotency_key=idempotency_key),
        )

    def rollback(
        self, *, service: ServiceName, version: str, idempotency_key: IdempotencyKey
    ) -> SideEffectResult:
        return self._retry(
            tool=ToolName.ROLLBACK,
            attempt=lambda: self._raw.rollback(
                service=service, version=version, idempotency_key=idempotency_key
            ),
        )

    def _retry(self, *, tool: ToolName, attempt: Callable[[], ActionReceipt]) -> SideEffectResult:
        attempts: list[Attempt] = []
        tool_calls = 0
        last_error: str | None = None
        for i in range(1, self._max_attempts + 1):
            tool_calls += 1
            try:
                receipt = attempt()
                attempts.append(Attempt(attempt_no=i, outcome=AttemptOutcome.SUCCESS))
                return SideEffectResult(
                    receipt=receipt,
                    attempts=tuple(attempts),
                    tool_calls=tool_calls,
                    final_error=None,
                )
            except (ToolTimeout, ToolTransientError) as e:
                attempts.append(
                    Attempt(
                        attempt_no=i,
                        outcome=AttemptOutcome.ERROR,
                        error_type=type(e).__name__,
                        error_message=str(e),
                    )
                )
                last_error = str(e)
                continue
            except ToolError as e:
                attempts.append(
                    Attempt(
                        attempt_no=i,
                        outcome=AttemptOutcome.ERROR,
                        error_type=type(e).__name__,
                        error_message=str(e),
                    )
                )
                last_error = str(e)
                break
        return SideEffectResult(
            receipt=None, attempts=tuple(attempts), tool_calls=tool_calls, final_error=last_error
        )
