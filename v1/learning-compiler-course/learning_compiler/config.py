from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RunConfig:
    """Top-level configuration for a lab run.

    We keep this intentionally small and pass it explicitly to avoid hidden global state.
    """

    seed: int = 7
    max_steps: int = 50
