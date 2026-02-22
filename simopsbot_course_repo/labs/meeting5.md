# Meeting 5 — Safety Boundaries: Untrusted Inputs + Policy Guardrails

## Goal

Resist hostile observations (logs/runbooks) and prevent forbidden actions.

## What to modify

- `learning_compiler/agent/policy.py`
- `learning_compiler/agent/deciders/llm_based.py` (scrubbing)
- `learning_compiler/sim/redteam.py` (case generator)

## Evidence requirement

Produce a journal showing:
- an adversarial snippet in logs/runbooks
- a blocked unsafe proposal
- safe fallback behavior
