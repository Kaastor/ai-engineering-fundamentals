"""Deterministic RNG helpers."""
from __future__ import annotations

import random
from dataclasses import dataclass

from learning_compiler.core.hashing import stable_hash_int


@dataclass(frozen=True, slots=True)
class SeededRng:
    """A deterministic RNG derived from a base seed and a purpose string."""

    base_seed: int

    def for_purpose(self, purpose: str) -> random.Random:
        seed = stable_hash_int([str(self.base_seed), purpose], bits=32)
        return random.Random(seed)
