from __future__ import annotations

from dataclasses import dataclass
import random
from collections.abc import Callable

from learning_compiler.sim.faults import FaultPlan, ToolError, ToolTimeout
from learning_compiler.sim.observations import (
    ActionReceipt,
    HealthObservation,
    LogsObservation,
    MetricsObservation,
    RunbookObservation,
)
from learning_compiler.sim.redteam import maybe_inject_untrusted_snippet
from learning_compiler.sim.runbooks import runbook_search
from learning_compiler.sim.world import SimWorld
from learning_compiler.types import IdempotencyKey, ServiceName, ToolName


@dataclass(slots=True, frozen=True)
class ToolCallBudget:
    max_calls: int

    def validate(self) -> None:
        if self.max_calls <= 0:
            raise ValueError("max_calls must be positive")


class RawSimTools:
    """Simulated tools, with deterministic noise + deterministic faults.

    This is the *untrusted* interface the agent uses:
    - observations can be noisy / delayed / adversarial
    - actions can fail (timeout / transient error)
    """

    def __init__(self, *, world: SimWorld, fault_plan: FaultPlan, seed: int) -> None:
        self._world = world
        self._faults = fault_plan
        self._rng = random.Random(seed ^ 0x7001_7001)
        self._idempotency: set[str] = set()

    # ---- Read-only tools ----

    def get_metrics(self, *, service: ServiceName, window_minutes: int) -> MetricsObservation:
        self._faults.maybe_raise(tool=ToolName.GET_METRICS)
        delay_steps = 1 if self._rng.random() < 0.30 else 0
        err, lat = self._world.true_metrics(service=service, delay_steps=delay_steps)
        noisy_err = _clip01(err + self._rng.gauss(0.0, 0.01))
        noisy_lat = max(0.0, lat + self._rng.gauss(0.0, 12.0))
        return MetricsObservation(
            tool=ToolName.GET_METRICS,
            service=service,
            window_minutes=window_minutes,
            error_rate=noisy_err,
            latency_ms=noisy_lat,
        )

    def tail_logs(self, *, service: ServiceName, n: int) -> LogsObservation:
        self._faults.maybe_raise(tool=ToolName.TAIL_LOGS)
        lines = list(self._world.tail_logs(service=service, n=n))
        injected = maybe_inject_untrusted_snippet(rng=self._rng)
        if injected is not None:
            lines.insert(0, injected)
        return LogsObservation(tool=ToolName.TAIL_LOGS, service=service, lines=tuple(lines))

    def health_check(self, *, service: ServiceName) -> HealthObservation:
        self._faults.maybe_raise(tool=ToolName.HEALTH_CHECK)
        status, details = self._world.health(service=service)
        return HealthObservation(tool=ToolName.HEALTH_CHECK, service=service, status=status, details=details)

    def runbook_search(self, *, query: str) -> RunbookObservation:
        self._faults.maybe_raise(tool=ToolName.RUNBOOK_SEARCH)
        snippets = runbook_search(incident=self._world.incident, query=query, rng=self._rng)
        return RunbookObservation(tool=ToolName.RUNBOOK_SEARCH, query=query, snippets=snippets)

    # ---- Side-effect tools (idempotent on key) ----

    def restart(self, *, service: ServiceName, idempotency_key: IdempotencyKey) -> ActionReceipt:
        return self._apply_action(
            tool=ToolName.RESTART,
            service=service,
            idempotency_key=idempotency_key,
            apply=lambda: self._world.restart(service=service),
        )

    def rollback(self, *, service: ServiceName, version: str, idempotency_key: IdempotencyKey) -> ActionReceipt:
        return self._apply_action(
            tool=ToolName.ROLLBACK,
            service=service,
            idempotency_key=idempotency_key,
            apply=lambda: self._world.rollback(service=service, version=version),
        )

    def _apply_action(
        self,
        *,
        tool: ToolName,
        service: ServiceName,
        idempotency_key: IdempotencyKey,
        apply: Callable[[], str],
    ) -> ActionReceipt:
        key = str(idempotency_key)
        if key in self._idempotency:
            # Idempotent replay: do not apply side effects twice.
            return ActionReceipt(
                tool=tool,
                service=service,
                idempotency_key=key,
                applied=False,
                message="idempotent replay: action already applied",
            )

        try:
            self._faults.maybe_raise(tool=tool)
        except ToolTimeout:
            # Timeout is ambiguous: maybe applied, maybe not.
            applied = self._rng.random() < 0.50
            if applied:
                _ = apply()
                self._idempotency.add(key)
            raise
        except ToolError:
            raise

        msg = apply()
        self._idempotency.add(key)
        return ActionReceipt(
            tool=tool,
            service=service,
            idempotency_key=key,
            applied=True,
            message=msg,
        )


def _clip01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x
