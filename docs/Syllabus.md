# AI 101: Reliable GenAI Systems with Kernel Lite
## 7×1h course plan (methodology-first)

### Course spine
A minimal **Kernel Lite** runtime that preserves production invariants:

- strategies propose actions (typed),
- kernel enforces budgets/policies,
- tools execute via contracts,
- side effects are gated,
- runs are logged/audited,
- systems are evaluated with regression + adversarial suites.

### What this course is (and isn’t)
**This course is:**
- an introduction to AI as *measurement-driven engineering*,
- an introduction to GenAI as a *probabilistic component that must be constrained*.

**This course is not:**
- a deep learning architecture tour,
- a full RAG stack course,
- a collection of prompt tricks.

### Scientific loop used every week
Every homework follows the same loop:

1. **Hypothesis** (what you expect will improve and why)
2. **Controlled change** (one variable at a time)
3. **Measure** (run the evaluation suite; record metrics)
4. **Error analysis** (inspect failures; categorize them)
5. **Conclusion** (what you learned; what you would try next)

---

## Course schedule (7 classes)

### Class 1 — What is “learning”?
**Core mental model:** A model is a function fit by optimizing a loss on data, and generalization is never guaranteed.

- Why train/test exists, and why “it works on my data” means nothing.
- Loss as an objective; optimization as improvement; overfitting as default.
- Connection to LLMs: next-token prediction, why hallucinations are structurally expected.
- Students leave with the course’s scientific loop and a baseline evaluation mindset.

**Homework 1:** Run a tiny supervised baseline; perform 1 controlled change; report metrics + 5 failure examples.

---

### Class 2 — Kernel mindset: trust boundaries, TCB, and “untrusted inputs”
**Core mental model:** Treat model output as untrusted input. Safety is a design property.

- Trust boundaries; Trusted Computing Base (TCB).
- Prompt injection as “adversarial input,” not a magical hack.
- Reference monitor idea: everything sensitive goes through a gate.
- Introduce Kernel Lite architecture: strategies propose, kernel enforces.

**In-class lab:** Break a naive “agent” with injection; write a simple threat model.

**Homework 2:** Add an “untrusted content envelope” to all model outputs/observations + write 10 adversarial prompts and expected safe behavior.

---

### Class 3 — ABI + deterministic orchestration (K1 + K2)
**Core mental model:** Reliability requires explicit state machines and typed interfaces.

- Typed state (JSON schema / Pydantic models).
- Explicit finite-state machine orchestration: stop conditions, retries, timeouts.
- Budget caps as hard constraints (time, tokens, tool calls).

**In-class lab:** Implement a minimal orchestrator with typed state transitions + transition tests.

**Homework 3:** Add stop conditions + budget pressure behavior; write tests that prove the kernel halts safely.

---

### Class 4 — Tools as contracts (tool executor)
**Core mental model:** Tools are APIs with schemas, typed errors, and deterministic behavior.

- Tool schemas: args, outputs, error types.
- Canonicalization and input validation.
- Bounded retries and timeouts (policy, not vibes).
- Logging: make runs inspectable.

**In-class lab:** Build a tool executor for read-only tools (e.g., “read file”, “list items”) with typed errors.

**Homework 4:** Add one new tool + add a tool error taxonomy; measure and report failure categories.

---

### Class 5 — Policy + reference monitor + gated side effects (K5-lite)
**Core mental model:** If it can cause side effects, it must be mediated.

- Allowlists, risk tiers, least privilege.
- Propose/preview/commit pattern for write tools.
- Approvals: binding to what exactly will happen (avoid TOCTOU).
- Fail closed: refusal is a feature.

**In-class lab:** Add one “write” tool (e.g., modify a TODO list file) and enforce propose → preview → commit with approval.

**Homework 5:** Add an approval policy + “no write without approval” tests; add adversarial attempts to bypass approval.

---

### Class 6 — Idempotency + outbox + replay safety
**Core mental model:** Production failures are crashes and retries; correctness requires dedupe and durable intent.

- Idempotency keys and deduplication.
- Outbox pattern: separate “decide” from “commit effects.”
- Crash recovery; exactly-once illusions vs at-least-once reality.

**In-class lab:** Simulate a crash mid-tool-call; demonstrate safe resume without duplicate side effects.

**Homework 6:** Add a crash simulation test; prove “no duplicate write” across restarts; add an audit record for each effect.

---

### Class 7 — Evaluation harness + adversarial suites (release discipline)
**Core mental model:** If you can’t test it, you can’t ship it.

- Regression tests for structured output, policy, and tool safety.
- Adversarial suite (prompt injection, malformed outputs, constraint violations).
- Release gating: “CI must pass” mindset.
- Final report structure: metrics, ablations, failure taxonomy.

**In-class lab:** Build the class evaluation pack and run it against multiple versions.

**Final deliverable:** A short engineering report:
- baseline metrics,
- 2 ablations and their measured impact,
- top failure modes and mitigations,
- “what I learned” (methodology reflection).

---

## Grading (process-first, honest)
Suggested rubric (can be adapted):

- **Reproducibility & tests (25%)**: deterministic runs, clear tests, stable outputs
- **Measurement quality (20%)**: correct metrics, logged results, controlled comparisons
- **Reliability & safety (25%)**: bounded retries, policy enforcement, safe failure behavior
- **Error analysis (20%)**: concrete failure examples + categories + mitigation reasoning
- **Clarity (10%)**: readable code + short written conclusions

---

## Allowed tooling policy (AI coding assistants)
AI coding assistants are allowed for boilerplate and syntax help.

But students must submit:
- a short “what changed and why” explanation,
- passing tests and reproducible metrics,
- a brief error analysis with examples.

We grade understanding and methodology, not copy-paste velocity.
