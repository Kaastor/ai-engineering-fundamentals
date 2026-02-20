# AI From Zero (Agentic Systems Spine) — Companion Notes

## Course worldview

This course treats **AI systems** as **agentic systems**:

> An AI system is an **agent loop**: **observe → decide → act → verify → stop**  
> under uncertainty and resource limits.

A **model** (including an LLM) can be a powerful component inside this loop, but it is not the system.

### Three invariants (used every week)

1. **Budgets / stop rules**  
   Every run must have explicit limits (steps, tool calls, planner expansions). “Runs forever” is a bug.

2. **Evidence / run journal (replayability)**  
   Every run produces a structured journal (JSONL) with stable IDs. You should be able to answer:
   - what the agent saw,
   - what it did,
   - why it stopped,
   - what evidence supports success.

3. **Tool boundaries (“policy proposes; system disposes”)**  
   The agent proposes actions and tool calls; the **system** enforces:
   - allowlists and contracts,
   - validation,
   - idempotency for side effects,
   - retries and timeouts.

---

## Repository map (for students)

- `learning_compiler/`: the library you import in labs.
- `scripts/`: thin wrappers used to run each lab.
- `book/`: these notes (Markdown).
- `runs/`: created when you run the scripts (journals live here).

---

## How to read a journal

A journal is **JSON Lines**: one JSON object per line.

Typical event types:

- `run_start`: configuration, budgets, map
- `step`: observation, action, outcomes, verification, agent snapshot
- `violation`: invariant/budget violations
- `run_end`: final result

You can treat a journal as a **flight recorder**: it tells you what happened even when the agent fails.

---

## About the name `learning_compiler`

The library name is intentionally nerdy: the course emphasizes that learning and models are *compiled into*
a system that also needs **contracts, evidence, budgets, and evaluation**.
