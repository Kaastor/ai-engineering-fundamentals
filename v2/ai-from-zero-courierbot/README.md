# AI From Zero — CourierBot (Agentic Systems Spine)

This repository is a **staff-quality, package-first** implementation of the course project described in the
6×1h syllabus:

> **An AI system is an agent loop:** observe → decide → act → verify → stop  
> under uncertainty and resource limits.  
> **The model is a component, not the system.**

The running project is **CourierBot**: a small Python agent that navigates a campus grid and interacts with
**simulated tools** that can fail, time out, or return malformed outputs.

## What you get

- `learning_compiler/`: the importable library (reusable logic lives here)
- `scripts/`: thin, executable wrappers (CLI entry points)
- `book/`: companion chapters in **formal academic tone** (Markdown + Mermaid)
- `spec.md`: a minimal system spec for evaluation (Meeting 6)
- `tests/`: lightweight regression tests (mypy/ruff-friendly)

## Quickstart

> Python **3.11** only.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run the labs (each produces a deterministic `runs/<run_id>/journal.jsonl`):

```bash
python scripts/run_lab1.py --seed 1
python scripts/run_lab2.py --seed 1
python scripts/run_lab3.py --seed 1
python scripts/run_lab4_train.py --seed 1
python scripts/run_lab4_run.py --seed 1
python scripts/run_lab5.py --seed 1
python scripts/run_lab6_eval.py --seed 1
```

Typecheck + lint:

```bash
mypy .
ruff check .
pytest
```

## Course invariants (repeated every week)

1. **Budgets / stop rules** (steps, tool calls, expansions)
2. **Evidence / run journal** (JSONL with stable IDs; replayable)
3. **Tool boundaries** (“policy proposes; system disposes”)

## Repository philosophy

- **Determinism is a feature:** seeded RNGs only; stable hashing for IDs.
- **I/O at the edges:** core logic is testable and pure-ish; scripts are thin wrappers.
- **Explicit contracts:** custom exceptions; no silent failures; no bare `except`.

---

## Directory map

- `learning_compiler/agent/`: agent loop, policies, workflow state machine
- `learning_compiler/planning/`: BFS + A* on grid graphs
- `learning_compiler/env/`: grid world, parsing, seeded map generation
- `learning_compiler/tools/`: tool simulator + reliability wrappers (validate/retry/idempotency)
- `learning_compiler/journal/`: JSONL event models + writer + replay reader
- `learning_compiler/learning/`: behavior cloning (dataset generation + kNN policy)
- `learning_compiler/evaluation/`: offline eval harness + adversarial cases

---

## Notes for instructors

The code intentionally supports **course stages** (Lab 1 → Lab 6) without forking the whole codebase.
Each script selects a stage and config, while reusing shared domain modules.

You can teach the progression by:
- running the earlier labs with fewer capabilities enabled
- then re-running the exact same scenarios after upgrades
- comparing journals as "black box flight recorders"
