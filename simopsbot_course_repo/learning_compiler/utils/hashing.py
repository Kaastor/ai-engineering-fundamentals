from __future__ import annotations

import hashlib

from learning_compiler.types import RunId


def stable_short_hash(text: str, *, length: int = 12) -> str:
    """Stable hash for IDs and trace fingerprints.

    - Deterministic across runs
    - Short (default 12 hex chars) to keep journals readable
    """

    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return digest[:length]


def make_run_id(*, seed: int, profile: str) -> RunId:
    return RunId(stable_short_hash(f"seed={seed}|profile={profile}", length=16))
