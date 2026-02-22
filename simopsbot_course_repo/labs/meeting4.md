# Meeting 4 — Acting Safely: Verification + Idempotency

## Goal

Make side effects safe:
- deterministic idempotency keys
- retries for transient failures
- verification evidence after side effects

## What to modify

- `learning_compiler/agent/tools_wrapped.py`
- `learning_compiler/agent/verifier.py`
- `learning_compiler/agent/loop.py`
