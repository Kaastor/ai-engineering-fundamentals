from __future__ import annotations

from learning_compiler.reliability.idempotency import IdempotencyStore


def test_idempotency_runs_operation_once() -> None:
    store: IdempotencyStore[int] = IdempotencyStore()
    counter = {"calls": 0}

    def op() -> int:
        counter["calls"] += 1
        return 42

    r1 = store.run(key="k", operation=op)
    r2 = store.run(key="k", operation=op)

    assert r1.ok and r2.ok
    assert r1.value == 42 and r2.value == 42
    assert counter["calls"] == 1
