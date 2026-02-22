# Meeting 1 — The Agent Loop + Evidence (no GenAI yet)

## Goal

Build a deterministic agent skeleton that produces a replayable JSONL trace.

## What to modify

- `learning_compiler/journal/*`
- `learning_compiler/agent/loop.py` (week1 path)
- `learning_compiler/agent/deciders/rule_based.py`

## Checklist

- [ ] Journal has stable event IDs.
- [ ] Each step logs `step_start`.
- [ ] Observations are logged with tool outputs.
- [ ] Budgets stop the run safely.
- [ ] Final entry references evidence event IDs.

## Run

```bash
python -m scripts.run_scenario --seed 0 --profile week1 --out outputs
python -m scripts.print_journal outputs/run_seed000000_week1.jsonl
```
