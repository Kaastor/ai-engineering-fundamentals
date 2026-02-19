"""Stable hashing utilities.

Python's built-in `hash()` is intentionally randomized across processes. For replayability and stable IDs,
we instead use SHA-256 and explicit encoding.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256


def stable_hash_hex(parts: Iterable[str]) -> str:
    h = sha256()
    for part in parts:
        h.update(part.encode("utf-8"))
        h.update(b"\x1f")  # unit separator
    return h.hexdigest()


def stable_hash_int(parts: Iterable[str], *, bits: int = 32) -> int:
    """Returns a non-negative int derived from SHA-256, truncated to `bits`.

    This is useful for seeding `random.Random` deterministically.
    """

    if bits <= 0 or bits > 256:
        raise ValueError("bits must be in (0, 256]")
    hex_digest = stable_hash_hex(parts)
    value = int(hex_digest, 16)
    mask = (1 << bits) - 1
    return value & mask


@dataclass(frozen=True, slots=True)
class StableIdFactory:
    """Creates stable event IDs within a run."""

    run_id: str

    def event_id(self, *, seq: int) -> str:
        return stable_hash_hex([self.run_id, str(seq)])
