from __future__ import annotations

import json
import random
from typing import Final

from learning_compiler.llm.adapter import LLMAdapter, LLMContext

_INVALID_OUTPUT_RATE: Final[float] = 0.15
_FORBIDDEN_SUGGESTION_RATE: Final[float] = 0.10


class FakeLLM(LLMAdapter):
    """Deterministic 'LLM' for offline labs.

    It behaves like a chat model in the only way we actually need for the course:
    - it proposes structured actions
    - it sometimes produces invalid outputs (to exercise validation + fallback)
    - it sometimes suggests unsafe actions (to exercise policy guardrails)

    No API keys, no network calls, no nondeterminism.
    """

    def __init__(self, *, seed: int) -> None:
        self._rng = random.Random(seed ^ 0xF4CE_11A0)  # deterministic

    def propose_next_action(self, *, context: LLMContext) -> str:
        if self._rng.random() < _INVALID_OUTPUT_RATE:
            # Occasionally break the contract (like real life).
            return "I think you should restart everything. Trust me."

        # Extract quick signals from observations.
        api_err = _last_metric(context=context, service="api", field="error_rate")
        db_lat = _last_metric(context=context, service="db", field="latency_ms")
        api_timeouts = _has_timeout_logs(context=context, service="api")

        if api_err is None and db_lat is None:
            return json.dumps({"type": "OBSERVE_METRICS", "service": "api", "window_minutes": 5})

        if api_err is not None and api_err > 0.25:
            return json.dumps({"type": "ACT_ROLLBACK", "service": "api", "version": "v1"})

        if db_lat is not None and db_lat > 300.0:
            if self._rng.random() < _FORBIDDEN_SUGGESTION_RATE:
                # Suggest something spicy and forbidden: rollback db (policy should block).
                return json.dumps({"type": "ACT_ROLLBACK", "service": "db", "version": "v2"})
            return json.dumps({"type": "ACT_RESTART", "service": "db"})

        if api_timeouts:
            return json.dumps({"type": "ACT_RESTART", "service": "api"})

        # Default: gather more evidence.
        return json.dumps({"type": "OBSERVE_LOGS", "service": "api", "n": 8})


def _last_metric(*, context: LLMContext, service: str, field: str) -> float | None:
    for obs in reversed(context.observations):
        if obs.get("tool") != "get_metrics":
            continue
        if obs.get("service") != service:
            continue
        v = obs.get(field)
        if isinstance(v, (int, float)):
            return float(v)
    return None


def _has_timeout_logs(*, context: LLMContext, service: str) -> bool:
    for obs in reversed(context.observations):
        if obs.get("tool") != "tail_logs":
            continue
        if obs.get("service") != service:
            continue
        lines = obs.get("lines")
        if isinstance(lines, list):
            for line in lines:
                if isinstance(line, str) and "timeout" in line.lower():
                    return True
    return False
