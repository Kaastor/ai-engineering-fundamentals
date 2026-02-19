from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass(slots=True)
class CircuitBreaker:
    """A tiny deterministic circuit breaker (step-based, not time-based).

    This is a teaching-friendly approximation of the classic pattern:
    - CLOSED: allow calls; count failures
    - OPEN: block calls
    - HALF_OPEN: allow a trial call; if success -> CLOSED, else -> OPEN
    """

    failure_threshold: int
    reset_after_steps: int

    _state: BreakerState = BreakerState.CLOSED
    _consecutive_failures: int = 0
    _opened_at_step: int | None = None
    _half_open_trial_used: bool = False

    def __post_init__(self) -> None:
        if self.failure_threshold <= 0:
            raise ValueError("failure_threshold must be > 0")
        if self.reset_after_steps <= 0:
            raise ValueError("reset_after_steps must be > 0")

    @property
    def state(self) -> BreakerState:
        return self._state

    def allow_request(self, *, step_index: int) -> bool:
        match self._state:
            case BreakerState.CLOSED:
                return True
            case BreakerState.OPEN:
                assert self._opened_at_step is not None
                if step_index - self._opened_at_step >= self.reset_after_steps:
                    self._state = BreakerState.HALF_OPEN
                    self._half_open_trial_used = False
                    return True
                return False
            case BreakerState.HALF_OPEN:
                if self._half_open_trial_used:
                    return False
                self._half_open_trial_used = True
                return True

    def on_success(self) -> None:
        self._consecutive_failures = 0
        self._opened_at_step = None
        self._half_open_trial_used = False
        self._state = BreakerState.CLOSED

    def on_failure(self, *, step_index: int) -> None:
        if self._state == BreakerState.HALF_OPEN:
            self._trip(step_index=step_index)
            return

        self._consecutive_failures += 1
        if self._consecutive_failures >= self.failure_threshold:
            self._trip(step_index=step_index)

    def _trip(self, *, step_index: int) -> None:
        self._state = BreakerState.OPEN
        self._opened_at_step = step_index
        self._half_open_trial_used = False
