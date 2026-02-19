from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class IdGenerator:
    """Deterministic ID generator.

    Avoids module-level counters (hidden global state). Callers own the instance.
    """

    prefix: str
    _next: int = 1

    def new(self) -> str:
        value = f"{self.prefix}{self._next}"
        self._next += 1
        return value
