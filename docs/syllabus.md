# Introduction to AI Systems (GenAI Agents)

**Theme:** *Agency under uncertainty, with Reliability + Evaluation as first-class.*
**Format:** 6 laboratory meetings × 60 minutes (explain + build + run + inspect evidence)
**Audience:** 2nd‑year undergrads, strong coders, math‑shy, **AI from zero**
**Time context:** February 2026
**Principle:** **A model is a component, not the system.** A real agent is **Behavior + Reliability + Evaluation** inside an explicit loop.

---

## Why this is still “Intro to AI” (under your spec)

This course is not a survey of all AI techniques. It’s a **worldview-shaping introduction** to what “AI” means in practice in 2026:

* **AI = agentic behavior under constraints** (not “a chatbot”).
* **Uncertainty is normal**; good agents manage it.
* **Reliability and evaluation are not optional** once a system can act.
* GenAI is the modern surface area, but we teach **timeless system patterns** (budgets, evidence, contracts, verification, regression tests) that outlast toolchains.

This keeps the scope feasible in 6 hours while still being foundational.

---

## Hard constraint: no dataset collection/labeling

To avoid the dataset problem entirely:

* **No external datasets** (no scraping, no real incident logs, no real runbooks, no “collect example tickets”).
* All “data” used is either:

  * **synthetic and course-provided**, or
  * **programmatically generated** from templates with a seed,
  * with **ground truth in code** for evaluation (no manual labeling).

This is enforced by the project choice and the grading artifacts.

---

# Running artifact: one agent, six upgrades

## Project: **SimOpsBot** — a GenAI incident-response agent in a toy production system

Students build one agent and upgrade it each week.

### The simulated world (small on purpose)

Keep it to **2 services** to reduce cognitive load:

* `api` depends on `db`
  Common incidents (scenario generator picks one):

1. bad deploy in `api` (error spikes)
2. `db` saturation (latency spikes)
3. flaky network between `api` and `db` (timeouts)

### Tools (all simulated, failure-injected)

Read-only observations:

* `get_metrics(service, window)` → error rate, latency (noisy/delayed)
* `tail_logs(service, n)` → log lines (some irrelevant; some adversarial strings)
* `health_check(service)` → status + a few fields

Actions with side effects:

* `restart(service, idempotency_key)`
* `rollback(service, version, idempotency_key)`

Knowledge (synthetic):

* `runbook_search(query)` → template-generated runbook snippets (some outdated/conflicting on purpose)

Everything is deterministic under a seed, so evaluation is automatable.

---

## The agent spine (repeated every meeting)

> **Observe → Decide → Act → Verify → Stop**
> under uncertainty and resource limits.

Three invariants become habits (used every week):

1. **Budgets / stop rules** (time, steps, tool calls; explicit “abstain” conditions)
2. **Evidence / run journal** (replayable JSONL trace)
3. **Tool boundaries** (*“model proposes; system disposes”*) enforced outside the model

---

# Outcomes (T‑shaped)

## Depth: core competence (agentic systems)

Students can:

* Implement an **agent loop** with explicit state, budgets, and journaling
* Use a GenAI model to propose **structured actions** and validate them
* Treat tool outputs as **observations** and require **evidence**
* Implement **verification** for side effects + **idempotency** for safe retries
* Handle untrusted input (logs/runbooks) safely via **policy guardrails**
* Build an **offline evaluation harness** + **regression gate**

## Breadth: durable AI worldview

Students can explain:

* Where GenAI fits in AI (not the whole field)
* Why uncertainty, reliability, and evaluation define “real” AI systems in 2026
* What changes fast (prompts/APIs) vs slow (contracts, state machines, evidence, eval discipline)

---

# Scope-control rules (to prevent overload)

These are baked into the syllabus structure:

* **One capability upgrade per meeting.**
* **Each meeting introduces ≤ 6 new technical terms.**
* **Every concept must appear in code and in a run journal.**
* Anything deeper becomes companion reading (the “book”), not in-class content.

---

# Assessment (lightweight, evidence-first)

Weekly (Meetings 1–5):

* code for the upgrade
* **1–2 run journals** (`.jsonl`)
* a short note: *one failure → what changed → what evidence improved*

Final (Meeting 6):

* `spec.md` (success criteria, constraints, budgets, unacceptable failures)
* `eval_runner.py` + scenario generator (seeded)
* `report.md` with metrics + two failure analyses using journal evidence

Grading emphasizes: **evidence discipline, safety boundaries, and evaluation**, not prompt cleverness.

---

# Companion “book” requirement (Markdown, formal tone)

Each chapter includes:

* clear definitions of terms
* Mermaid diagrams
* analogies
* worked examples with run traces + journal excerpts
* exercises

(Students can read before/after; the course works even if only some read, but reading reduces overload.)

---

# The 6 meetings (updated, reduced scope, beginner-safe)

## Meeting 1 — The Agent Loop + Evidence (no GenAI yet)

**Upgrade:** a working agent skeleton that produces a replayable trace.

**In-class concepts (keep tight)**

* Agent loop: observe → decide → act → verify → stop
* State vs observation
* Budget/stop rule
* Evidence and run journal (why “it seemed to work” is not evidence)

**New terms (limit):** agent loop, state, observation, action, evidence, budget.

**60-minute flow**

* 0–5: what the course builds (SimOpsBot) + the loop diagram
* 5–20: implement `RunJournal` (JSONL), stable `run_id`, step IDs
* 20–40: implement loop with a simple rule-based decider (no model)
* 40–55: add budgets (max steps, max tool calls) + verify placeholder
* 55–60: read a journal together: what counts as evidence?

**Deliverable**

* `agent_loop.py` + `journal.jsonl` from a deterministic scenario seed

**Book Chapter 1**

* “Agents, Evidence, and Budgets”
* Worked trace: 6-step run with annotated journal entries

---

## Meeting 2 — GenAI as a Component: Structured Actions + Validation

**Upgrade:** GenAI proposes the next step, but the system validates and controls execution.

**In-class concepts**

* “Model proposes; system disposes” (enforced by code)
* Structured output schema (JSON action objects)
* Validation + fallback behavior (invalid output is an error, not creativity)
* Reproducibility knob: deterministic settings for debugging

**New terms:** schema, validation, fallback, deterministic, proposal, executor.

**60-minute flow**

* 0–8: architecture sketch (model is not in control)
* 8–25: define `ActionSchema`:

  * `OBSERVE_METRICS(service)`
  * `OBSERVE_LOGS(service)`
  * `ACT_RESTART(service)`
  * `ACT_ROLLBACK(service, version)`
  * `ASK_USER(question)`
  * `FINAL(summary, evidence_refs)`
* 25–45: parse + validate + reject invalid proposals
* 45–55: add a safe fallback policy (ask user / observe more / stop)
* 55–60: compare two runs: one valid, one invalid proposal (journal shows handling)

**Deliverable**

* `llm_adapter.py` + `action_schema.py` + validator
* Journal now logs: model proposal → validation outcome → executed action

**Book Chapter 2**

* “GenAI-in-the-Loop Systems: Contracts Over Vibes”
* Mermaid: proposal → validation → executor pipeline

---

## Meeting 3 — Uncertainty Without Math Trauma: Hypotheses + Ask vs Act

**Upgrade:** the agent manages uncertainty explicitly using hypotheses + evidence links.

**In-class concepts**

* Observations are incomplete/noisy → uncertainty is normal
* Maintain a small **hypothesis list** (2–3 competing causes)
* Evidence discipline: each hypothesis has supporting evidence references
* Ask vs act: observe more (or ask) when confidence is low or stakes are high

**New terms:** hypothesis, evidence link, ambiguity, abstain, stake, observation noise.

**60-minute flow**

* 0–8: what uncertainty looks like in metrics/logs
* 8–25: implement `Hypotheses` structure:

  * `cause`, `confidence_level` (low/med/high), `evidence_ids`
* 25–45: implement update rules from observations (simple, rule-based)
* 45–55: implement “ask/observe-more” trigger (low confidence ⇒ gather evidence)
* 55–60: run an ambiguous scenario; show how the agent avoids premature action

**Deliverable**

* `hypotheses.py`
* Journals must show: competing hypotheses + evidence IDs + why the chosen next step was chosen

**Book Chapter 3**

* “Operational Uncertainty: Staying Honest in Fog”
* Worked example: ambiguous incident resolved by additional observation

---

## Meeting 4 — Acting Safely: Verification + Idempotency (reliability core)

**Upgrade:** side effects become safe: verify outcomes and prevent duplicate actions.

**In-class concepts**

* Tool contracts (inputs/outputs) and normalized errors
* Verification: after restart/rollback, check recovery evidence (metrics/health)
* Idempotency: retries must not double-apply side effects
* Minimal workflow states to keep debugging sane

**New terms:** contract, verification, idempotency, retry, side effect, workflow.

**60-minute flow**

* 0–10: why actions are dangerous without verification
* 10–30: wrap `restart/rollback` with:

  * timeouts + retry (simple)
  * idempotency keys
  * structured receipts recorded in journal
* 30–45: implement `verify_recovery()` rule (health OK + metrics improved)
* 45–55: introduce a tiny workflow (Observe → Diagnose → Act → Verify)
* 55–60: failure injection: timeout then retry; prove “no double action” via journal

**Deliverable**

* `tools_wrapped.py` (contracts + idempotency + retry)
* Verification evidence stored in journal

**Book Chapter 4**

* “Reliability Primitives for Agentic Systems”
* Mermaid workflow + worked incident trace

---

## Meeting 5 — Safety Boundaries: Untrusted Inputs + Policy Guardrails

**Upgrade:** the system resists hostile observations (logs/runbooks) and prevents forbidden actions.

**In-class concepts**

* Injection reframed timelessly: **untrusted input masquerading as instruction**
* Allowlists and argument constraints (policy enforced outside model)
* Safe degradation: when uncertain or under attack → observe/ask/stop, not act

**New terms:** untrusted input, policy, allowlist, constraint, adversarial, safe degradation.

**60-minute flow**

* 0–10: threat model: what could go wrong in this toy world?
* 10–25: inject adversarial log lines / runbook snippets (synthetic, templated)
* 25–45: implement `policy.py`:

  * allowed tools
  * allowed services
  * rate limits / budgets
  * forbidden tool sequences (optional, simple)
* 45–55: run red-team cases; confirm blocked attempts in journal
* 55–60: discuss: why this generalizes beyond LLMs (classic security principle)

**Deliverable**

* `policy.py` + `redteam_cases_generate.py` (template-based)
* A journal showing at least one blocked injection attempt + safe fallback behavior

**Book Chapter 5**

* “Security as Input Discipline: Data Is Not Commands”
* Worked example: poisoned runbook handled safely

---

## Meeting 6 — Evaluation as Engineering: Specs + Offline Suite + Regression Gate

**Upgrade:** you turn a demo into an engineering artifact: spec, tests, metrics, gate.

**In-class concepts**

* Spec: success criteria + constraints + budgets + unacceptable failures
* Offline eval suite: seeded scenario generator + automated runs
* Regression gate: thresholds that prevent backsliding
* Minimal metrics for agents (objective, automatable)

**New terms:** spec, metric, offline eval, regression gate, threshold, reproducibility.

**60-minute flow**

* 0–10: write `spec.md` together (one page, concrete)
* 10–30: implement `scenario_generator(seed)` (programmatic incidents + noise + tool failures)
* 30–45: implement `eval_runner.py` to run N seeds and compute metrics:

  * recovery success rate
  * mean steps/time
  * verification success rate
  * evidence compliance rate
  * unsafe action attempt rate (must be 0)
* 45–55: set regression thresholds; compare “Week 2 agent” vs “Week 5 agent”
* 55–60: interpret one failure using journal evidence (scientific method vibe)

**Deliverable**

* `spec.md`, `scenario_generator.py`, `eval_runner.py`, `report.md`

**Book Chapter 6**

* “Evaluation: The Scientific Method for AI Systems”
* Mermaid: spec → suite → gate → ship loop

---

# Companion book outline (formal, Markdown)

1. Agents, evidence, budgets
2. GenAI-in-the-loop: structured outputs and validation
3. Operational uncertainty: hypotheses, evidence links, ask vs act
4. Safe action: verification and idempotency
5. Safety boundaries: untrusted inputs and policy enforcement
6. Evaluation: specs, offline suites, regression gates

**Appendices (optional depth, not class time)**

* AI landscape map (classical AI, probability, learning, RL—where they fit)
* Minimal probability primer (discrete tables; intuition)
* Decoding details (for the curious)
* Monitoring mindset (SLIs/SLOs, drift) as “where this goes next”

---

# What this updated version changes to reduce overload (without losing value)

* The simulator is intentionally **small (2 services)** to keep cognitive load low.
* Probability and decoding theory are **not taught in-class**; uncertainty is taught operationally via hypotheses + evidence.
* Reliability is narrowed to the two most universally reusable primitives: **verification** and **idempotency**, plus simple retries/timeouts.
* Security is kept to **one timeless principle** and implemented concretely with policy guardrails.
* Every meeting produces a visible artifact: **run journals** that make learning tangible.

This is about as “high signal per hour” as you can get while respecting that students are total beginners and you only have six hours. The course becomes a compass: students won’t “know all AI,” but they’ll stop building haunted-house demos and start building **bounded, evidence-driven, evaluable agentic systems**—which is exactly the kind of foundation that still makes sense in 2030.
