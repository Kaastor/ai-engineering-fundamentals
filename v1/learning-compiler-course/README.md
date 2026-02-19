# Learning Compiler Course Repo (Agentic Systems–first AI, Feb 2026)

This repository is a **6×1h lab companion** for an “AI-from-zero” course aimed at
**2nd-year undergrads** who can code but are math-shy.

The organizing principle is intentionally boring (the best kind of boring):

> An AI system is an agent that repeatedly **observes → decides → acts → verifies → stops**
> under uncertainty and resource limits.

Modern twist, still timeless:

> The model is a component, not the system. A real agent is **Behavior + Reliability + Evaluation**.

This codebase avoids framework churn and instead teaches “engineering physics” that
will still be true when today’s libraries are fossils.

---

## What’s in the repo

### Code (importable, testable)
- `learning_compiler/agent/` — agent loop primitives: typed actions, journal, stop rules.
- `learning_compiler/planning/` — BFS/DFS/UCS/A* with a small GridWorld problem.
- `learning_compiler/uncertainty/` — discrete Bayes updates + belief-state decision examples.
- `learning_compiler/learning/` — tiny supervised learning + tabular Q-learning.
- `learning_compiler/reliability/` — retries, idempotency, circuit breaker primitives.
- `learning_compiler/evaluation/` — offline eval suite runner + adversarial cases.
- `learning_compiler/labs/` — per-meeting lab runners that glue the pieces together.

### Scripts (thin wrappers)
- `scripts/lc.py` — a small CLI that runs each lab.

### Reading material (“companion book”)
- `docs/book/` — six chapters (Markdown), formal tone, Mermaid diagrams, analogies, worked examples.

---

## Quickstart

### 1) Create an environment (Python 3.11)
```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

### 2) Run a lab
```bash
python scripts/lc.py lab1 --seed 7
python scripts/lc.py lab2 --seed 7
python scripts/lc.py lab6 --seed 7
```

### 3) Run checks
```bash
ruff check .
ruff format .
mypy .
pytest
```

---

## Pedagogical design notes

This repo is designed to make “agent invariants” explicit and inspectable:

- **Budgets & stop rules** are first-class and deterministic.
- **Side effects are typed** (read vs write) and mediated by the system.
- **Observations are treated as data** (including tool output), not truth-by-default.
- **Runs are journaled** with stable, replay-friendly hashes.
- **Evaluation is code**: offline suites, adversarial probes, regression gates.

---

## License

MIT, see `LICENSE`.
