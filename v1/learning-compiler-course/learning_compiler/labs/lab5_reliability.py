from __future__ import annotations

import random
from dataclasses import dataclass

from learning_compiler.reliability.circuit_breaker import CircuitBreaker
from learning_compiler.reliability.idempotency import IdempotencyStore
from learning_compiler.reliability.retry import RetryPolicy, run_with_retries


class RetryableChargeError(Exception):
    """A simulated transient error (e.g., network timeout)."""


@dataclass(slots=True)
class FakePaymentProcessor:
    """A tiny side-effecting 'tool' for reliability demos."""

    fail_first_n: int
    charges_executed: int = 0
    _attempts: int = 0

    def charge(self, *, amount_cents: int) -> str:
        self._attempts += 1
        if self._attempts <= self.fail_first_n:
            raise RetryableChargeError("transient processor error")

        self.charges_executed += 1
        return f"receipt_{self.charges_executed:03d}"


def run(*, seed: int) -> str:
    rng = random.Random(seed)

    lines: list[str] = []
    lines.append("# Lab 5 — Reliability: software that doesn't betray you")
    lines.append("")
    lines.append("## Retries with exponential backoff (deterministic jitter)")
    processor = FakePaymentProcessor(fail_first_n=2)

    policy = RetryPolicy(max_attempts=5, base_delay_s=0.2, max_delay_s=2.0, jitter_ratio=0.25)

    retry_result = run_with_retries(
        operation=lambda: processor.charge(amount_cents=500),
        policy=policy,
        rng=rng,
        is_retryable=lambda e: isinstance(e, RetryableChargeError),
    )

    lines.append(f"- ok: {retry_result.ok}")
    lines.append(f"- attempts: {retry_result.attempts}")
    lines.append(f"- scheduled delays (s): {list(retry_result.delays_scheduled_s)}")
    lines.append(f"- receipt: {retry_result.value}")
    lines.append(f"- charges executed (side effects): {processor.charges_executed}")
    lines.append("")

    lines.append("## Idempotency: don't double-charge the user")
    store: IdempotencyStore[str] = IdempotencyStore()

    def charge_once() -> str:
        return processor.charge(amount_cents=500)

    first = store.run(key="payment_abc123", operation=charge_once)
    second = store.run(key="payment_abc123", operation=charge_once)

    lines.append(f"- first call ok={first.ok}, value={first.value}")
    lines.append(f"- second call ok={second.ok}, value={second.value} (should be identical)")
    lines.append(f"- charges executed (side effects): {processor.charges_executed}")
    lines.append("")

    lines.append("## Circuit breaker: fail fast instead of melting down")
    breaker = CircuitBreaker(failure_threshold=2, reset_after_steps=3)

    def flaky_call() -> str:
        raise RetryableChargeError("still down")

    for step in range(8):
        allowed = breaker.allow_request(step_index=step)
        if not allowed:
            lines.append(f"- step {step}: breaker={breaker.state.value}, request=BLOCKED")
            continue

        try:
            _ = flaky_call()
            breaker.on_success()
            lines.append(f"- step {step}: breaker={breaker.state.value}, request=OK")
        except RetryableChargeError:
            breaker.on_failure(step_index=step)
            lines.append(f"- step {step}: breaker={breaker.state.value}, request=FAILED")

    lines.append("")
    lines.append("Takeaway: reliability is a set of small, boring spells that prevent expensive folklore.")

    return "\n".join(lines)
