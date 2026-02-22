# SimOpsBot Course Repository (Intro to AI Systems — GenAI Agents)

This repository is the **running artifact** for a 6×60-minute laboratory course:

> **A model is a component, not the system.**  
> A real agent is **Behavior + Reliability + Evaluation** inside an explicit loop.

Students build one agent (**SimOpsBot**) and upgrade it each week:

1. **Agent loop + evidence** (journaling, budgets)
2. **GenAI as a component** (structured actions + validation)
3. **Uncertainty management** (hypotheses + ask-vs-act)
4. **Reliability primitives** (verification + idempotency + retry)
5. **Safety boundaries** (untrusted inputs + policy guardrails)
6. **Evaluation engineering** (offline suite + regression gate)

Everything is **deterministic under a seed** so you can evaluate agents offline without datasets.

---

## Quickstart

### Requirements

- Python **3.11**

### Install (editable) + dev tooling

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Run one scenario (writes a JSONL run journal)

```bash
python -m scripts.run_scenario --seed 7 --profile week5 --out outputs/
```

### Print a journal (human-friendly)

```bash
python -m scripts.print_journal outputs/run_seed000007_week5.jsonl
```

### Run the offline evaluation suite

```bash
python -m scripts.eval_runner --profile week5 --seeds 0:50 --out outputs/eval_week5/
```

### Compare Week 2 vs Week 5 agents (regression gate demo)

```bash
python -m scripts.eval_runner --profile week2 --seeds 0:50 --out outputs/eval_week2/
python -m scripts.eval_runner --profile week5 --seeds 0:50 --out outputs/eval_week5/
```

---

## Repository layout

- `scripts/` — thin CLI wrappers (no business logic)
- `learning_compiler/` — importable package, organized by domain
  - `sim/` — deterministic incident simulator + tools + failure injection
  - `agent/` — agent loop, actions, policy, verifier, hypotheses
  - `journal/` — replayable JSONL run journal (evidence)
  - `llm/` — *fake* LLM adapter (deterministic) + interface for real models
  - `eval/` — scenario runner, metrics, regression gate
- `book/` — companion reading (formal tone, Mermaid diagrams, worked traces)
- `tests/` — unit tests + determinism checks

---

## Profiles (what “week” means in code)

You can run the agent in different capability profiles:

- `week1`: rule-based loop + evidence + budgets
- `week2`: model proposes structured actions; system validates + falls back
- `week3`: explicit hypotheses + evidence links; ask/observe-more when uncertain
- `week4`: safe side effects via verification + idempotency + retry
- `week5`: policy guardrails + untrusted-input discipline

The default `LLMAdapter` is a **deterministic fake model** so evaluation is stable
without API keys.

---

## Design principles baked in

- **Determinism**: seeded RNG, stable run IDs, stable journal event IDs
- **No import-time side effects**: safe imports, explicit entrypoints
- **Tool boundaries**: validator + policy live outside the “model”
- **Evidence-first**: journals are the primary debugging interface

---

## Course artifacts

- `spec.md` — one-page success criteria + constraints + unacceptable failures
- `report.md` — template for the final report (metrics + failure analyses)

---

## License

MIT (see `LICENSE`).
