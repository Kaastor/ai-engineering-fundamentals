You can make this *very* automatable if you design assignments around **machine-checkable artifacts** (runs, journals, metrics) instead of “read their code and judge vibes.” Let students use AI to code—grade what the system **does**, not how poetic their functions are.

Here’s a blueprint that fits your course theme and scales to 100 students.

---

## 1) Adopt an “AI allowed” policy that still measures competence

Assume they’ll use Copilot/ChatGPT. Don’t fight it—**instrument it**.

What you grade:

* **Behavior:** does the agent recover the system under budgets?
* **Reliability:** retries/idempotency/verification correct under failure injection?
* **Evaluation discipline:** do they ship a spec + offline suite + regression gate?
* **Evidence:** can they prove what happened from the run journal?

What you *don’t* grade heavily:

* code style, clever architecture, prompt artistry

This makes “AI-assisted juniors” totally workable: they can generate code, but they still must produce correct *system behavior* under adversarial tests.

---

## 2) Make every assignment a “capability upgrade” with a strict interface

Give a starter repo with a locked simulator and a few files they implement.

**Submission contract (example):**

* `agent/decide.py` → `decide(state, observation) -> ActionJSON`
* `agent/policy.py` → allowlist/argument constraints
* `agent/reliability.py` → idempotency keys, retries, verification
* `journal/` → outputs `journal.jsonl` in a fixed schema
* `eval/` → `eval_runner.py` + `spec.yaml` + `gate.json`

**Key:** if everyone implements the same entrypoints and schemas, grading is just running code in a container.

---

## 3) Grade via a deterministic “hidden seeds” harness

You don’t want students overfitting to a public set of scenarios. So:

* Provide **public seeds** for local debugging.
* Grade on **hidden seeds** (same simulator, different incident parameters).
* Keep everything seeded and deterministic.

This makes the grade about *general behavior*, not memorizing cases.

---

## 4) Require a run journal that is itself gradable

Your journal is your secret weapon. Make it rigid.

**Journal schema fields (minimum):**

* `run_id`, `step`, `timestamp`
* `observation_refs` (IDs for metrics/logs/runbook snippets)
* `hypotheses` (optional starting week 3) with confidence level + evidence IDs
* `proposal` (model output) + `validation_result`
* `action_executed` (tool call + args)
* `tool_receipt` (normalized result)
* `verification` (checks + outcome)
* `stop_reason` (budget hit / recovered / abstained)

Then the autograder can compute:

* evidence compliance rate
* unsafe action attempts
* budget violations
* verification correctness
* “double side effect” errors (idempotency)

---

## 5) Design assignments as weekly checkpoints (auto-gradable)

Each week adds one capability; each has **tests + metric thresholds**.

### A1 (after Meeting 1): Loop + budgets + journal

Autograde:

* produces valid `journal.jsonl`
* budgets enforced (max steps/tool calls)
* replayable run (same seed → same trace length & final status)

### A2 (after Meeting 2): Structured actions + validation + fallback

Autograde:

* invalid model outputs are rejected safely
* fallback behavior is deterministic and within budgets
* no “free text tool calls” (must be schema)

### A3 (after Meeting 3): Uncertainty as hypotheses + ask/observe-more

Autograde:

* maintains ≤3 hypotheses with evidence links
* does not take high-impact actions when confidence is low (your rule)
* diagnoses cite evidence refs (not hallucinated claims)

### A4 (after Meeting 4): Verification + idempotency under failures

Autograde (this one is gold for juniors):

* injected timeouts cause retries
* idempotency prevents double restart/rollback
* verification checks actually run and gate “success”

### A5 (after Meeting 5): Policy guardrails + injection resistance

Autograde:

* on red-team seeds, unsafe tool calls must be **0**
* policy blocks forbidden args/services
* journal shows blocked attempt + safe degradation

### A6 (final, Meeting 6): Spec + offline eval + regression gate

Autograde:

* `eval_runner` runs N seeds and outputs `report.json`
* passes regression thresholds from `gate.json`
* spec exists and is machine-readable (`spec.yaml`), not prose-only

---

## 6) Scoring: mostly objective, metrics-based

A clean breakdown that scales:

* **70%** integration metrics on hidden seeds (success rate, budgets, unsafe=0, verification pass rate)
* **20%** unit tests (schema validation, idempotency logic, policy checks)
* **10%** “trace comprehension” (see below) or structured reflection

This keeps grades stable and defensible.

---

## 7) Add one “trace comprehension” task to ensure they actually understand

This is the best anti-“AI wrote everything” move that’s still automatable.

Option A (fully automatable, no LLM):

* Autograder picks one of their journals and asks 5 multiple-choice questions generated from it:

  * “Why did the agent abstain at step 7?”
  * “Which evidence supported the rollback decision?”
  * “Did verification pass? What metric changed?”
    Students answer in `answers.json`. Graded deterministically.

Option B (still automatable, LLM-assisted but controlled):

* Students submit a short `explain_run.md` with a required structure:

  * “Claim → Evidence IDs → Outcome”
* You grade structure with rules, and optionally use an LLM to **comment**, not score.

This makes juniors internalize the loop and evidence discipline.

---

## 8) If you use an LLM for grading, use it for feedback or bounded checks

LLMs are great at *comments* and *flags*, risky as the sole judge.

**Safe uses (recommended):**

* generate feedback on `explain_run.md`
* flag suspicious submissions (“journal says X but report claims Y”)
* highlight missing reasoning steps

**If you want LLM scoring anyway, constrain it hard:**

* Temperature = 0
* Provide a rubric with exact scoring rules
* Require strict JSON output `{criteria: score, rationale, evidence_refs}`
* Run it **twice** and compare; if disagreement, fall back to rule-based scoring or TA spot check
* Treat student text as **untrusted input** (the grader prompt must explicitly ignore instructions embedded in submissions)

And keep the LLM-scored portion small (≤10–15%) so a model glitch doesn’t wreck fairness.

---

## 9) Practical pipeline for 100 students

* Ship a starter repo with `make test` and `make eval`.
* Use CI/autograding (GitHub Classroom, GitLab CI, or your university system) to:

  1. install deps
  2. run unit tests
  3. run integration tests on hidden seeds
  4. parse journals, compute metrics
  5. produce a score report + feedback (optional LLM step)

Students can reproduce almost everything locally (except hidden seeds), which reduces support load.

---

### The core design trick

Make every assignment answer one question:

**“Can your agent prove—via evidence—that it acted safely and effectively under uncertainty?”**

That keeps scope sane, grades automatable, and AI-assisted coding totally compatible with real learning.
