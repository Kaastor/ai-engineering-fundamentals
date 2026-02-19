from __future__ import annotations

from learning_compiler.core.hashing import stable_hash_hex, stable_hash_int


def test_stable_hash_is_deterministic() -> None:
    a = stable_hash_hex(["hello", "world"])
    b = stable_hash_hex(["hello", "world"])
    assert a == b
    assert len(a) == 64


def test_stable_hash_int_bounds() -> None:
    v = stable_hash_int(["x"], bits=16)
    assert 0 <= v < (1 << 16)
