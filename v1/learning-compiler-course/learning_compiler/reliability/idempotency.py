from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Generic, TypeVar


ResultT = TypeVar("ResultT")


class IdempotencyError(Exception):
    """Errors related to idempotency handling."""


@dataclass(frozen=True, slots=True)
class IdempotencyRecord(Generic[ResultT]):
    ok: bool
    value: ResultT | None
    error: str | None


@dataclass(slots=True)
class IdempotencyStore(Generic[ResultT]):
    """In-memory idempotency store.

    In production you would back this with a DB, and carefully define retention,
    deduplication windows, etc. Here we focus on the core invariant:

    > same key => same outcome, without repeating side effects
    """

    _records: dict[str, IdempotencyRecord[ResultT]] = field(default_factory=dict)

    def run(self, *, key: str, operation: Callable[[], ResultT]) -> IdempotencyRecord[ResultT]:
        if not key:
            raise IdempotencyError("Idempotency key must be non-empty")

        existing = self._records.get(key)
        if existing is not None:
            return existing

        try:
            value = operation()
            record = IdempotencyRecord(ok=True, value=value, error=None)
        except Exception as exc:  # noqa: BLE001 - boundary where side effect may fail
            record = IdempotencyRecord(ok=False, value=None, error=f"{type(exc).__name__}: {exc}")

        self._records[key] = record
        return record
