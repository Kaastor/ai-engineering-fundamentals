from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from statistics import mean

from learning_compiler.orchestration.runner import RunSummary


@dataclass(frozen=True, slots=True)
class EvalMetrics:
    runs: int
    success_rate: float
    mean_steps_success: float | None
    p95_steps_success: int | None
    mean_tool_attempts: float
    failures: int

    def regression_gate(self, *, min_success_rate: float) -> bool:
        return self.success_rate >= min_success_rate


def compute_metrics(summaries: Iterable[RunSummary]) -> EvalMetrics:
    runs = list(summaries)
    if not runs:
        raise ValueError("no runs")

    successes = [r for r in runs if r.success]
    success_rate = len(successes) / len(runs)

    steps_success = sorted(r.steps for r in successes)
    mean_steps_success = mean(steps_success) if steps_success else None
    p95_steps_success = _percentile_int(steps_success, 0.95) if steps_success else None

    mean_tool_attempts = mean(r.tool_attempts for r in runs)

    return EvalMetrics(
        runs=len(runs),
        success_rate=success_rate,
        mean_steps_success=mean_steps_success,
        p95_steps_success=p95_steps_success,
        mean_tool_attempts=mean_tool_attempts,
        failures=len(runs) - len(successes),
    )


def _percentile_int(sorted_values: list[int], p: float) -> int:
    if not sorted_values:
        raise ValueError("empty list")
    if not (0.0 <= p <= 1.0):
        raise ValueError("p must be in [0, 1]")
    idx = int(round((len(sorted_values) - 1) * p))
    return sorted_values[idx]
