from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar


ResultT = TypeVar("ResultT")


class RetryError(Exception):
    """Base error type for retry utilities."""


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    max_attempts: int
    base_delay_s: float = 0.1
    max_delay_s: float = 2.0
    jitter_ratio: float = 0.1

    def __post_init__(self) -> None:
        if self.max_attempts <= 0:
            raise ValueError("max_attempts must be > 0")
        if self.base_delay_s < 0.0 or self.max_delay_s < 0.0:
            raise ValueError("delays must be non-negative")
        if self.base_delay_s > self.max_delay_s:
            raise ValueError("base_delay_s must be <= max_delay_s")
        if not (0.0 <= self.jitter_ratio <= 1.0):
            raise ValueError("jitter_ratio must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class RetryResult(Generic[ResultT]):
    ok: bool
    value: ResultT | None
    error: str | None
    attempts: int
    delays_scheduled_s: tuple[float, ...]


def run_with_retries(
    *,
    operation: Callable[[], ResultT],
    policy: RetryPolicy,
    rng: random.Random,
    is_retryable: Callable[[Exception], bool],
    sleep: Callable[[float], None] | None = None,
) -> RetryResult[ResultT]:
    """Run an operation with retries and deterministic backoff scheduling.

    We keep sleeping optional so this stays test-friendly and side-effect-free by default.
    """

    sleeper = sleep or (lambda _seconds: None)

    delays: list[float] = []
    last_err: Exception | None = None

    for attempt in range(1, policy.max_attempts + 1):
        try:
            value = operation()
            return RetryResult(
                ok=True,
                value=value,
                error=None,
                attempts=attempt,
                delays_scheduled_s=tuple(delays),
            )
        except Exception as exc:  # noqa: BLE001 - explicit contract: operation may fail
            last_err = exc
            if attempt >= policy.max_attempts or not is_retryable(exc):
                break

            delay = _compute_delay_s(attempt=attempt, policy=policy, rng=rng)
            delays.append(delay)
            sleeper(delay)

    assert last_err is not None  # for mypy
    return RetryResult(
        ok=False,
        value=None,
        error=f"{type(last_err).__name__}: {last_err}",
        attempts=policy.max_attempts,
        delays_scheduled_s=tuple(delays),
    )


def _compute_delay_s(*, attempt: int, policy: RetryPolicy, rng: random.Random) -> float:
    # Exponential backoff: base * 2^(attempt-1) capped at max_delay.
    raw = policy.base_delay_s * (2 ** (attempt - 1))
    capped = min(raw, policy.max_delay_s)

    # Jitter in [-ratio, +ratio] * capped, deterministic via rng.
    jitter_span = policy.jitter_ratio * capped
    jitter = (rng.random() * 2 - 1) * jitter_span
    return max(0.0, capped + jitter)
