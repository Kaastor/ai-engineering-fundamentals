from __future__ import annotations

from learning_compiler.labs.lab1_big_map import run


def test_journal_hash_is_deterministic_for_seed() -> None:
    out1, r1 = run(seed=7)
    out2, r2 = run(seed=7)
    assert out1 == out2
    assert r1.journal.trace_hash() == r2.journal.trace_hash()


def test_journal_hash_changes_with_run_id_seed() -> None:
    _out1, r1 = run(seed=1)
    _out2, r2 = run(seed=2)
    assert r1.journal.trace_hash() != r2.journal.trace_hash()
