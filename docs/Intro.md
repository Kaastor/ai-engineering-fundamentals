# AI 101: Reliable GenAI Systems with Kernel Lite
## Course design rationale (for instructors and students)

### Audience and constraints (why this course looks the way it does)
This course is designed for **2nd/3rd year undergraduate students** at a **public Polish university** who:

- are seeing AI for the **first time** in a formal class,
- often have **gaps in math** (especially probability/linear algebra intuition),
- often have **gaps in programming** (Python comfort varies),
- still deserve a course that teaches **real AI methodology** rather than “buzzword tourism.”

The course format is constrained:
- **7 classes × 1 hour** in-class time.
- Homework is allowed (and expected), and starter code can be provided so students do not start from scratch.

The design goal is not “cover everything,” but to build **strong mental models** and a **repeatable scientific workflow** that students can reuse in future ML/DL/GenAI courses.

---

## The mindset this course aims to set
This is intentionally a “first AI class that sets your default worldview.”

By the end, students should instinctively think:

1. **A model is a function fit by optimizing a loss on data.**
2. **Generalization is never guaranteed.** Train accuracy is not the goal.
3. **If you can’t measure it, you can’t improve it.**
4. **AI work is experimentation:** hypothesis → controlled change → measure → error analysis.
5. **LLMs are unreliable components by default.** Reliability is not “prompt vibes”; it is engineered.

This mindset is compatible with every subfield:
- classic ML,
- deep learning,
- generative AI,
- “agentic” systems.

---

## Depth vs breadth (the “T-shaped” choice)
With only 7 hours in class, a broad tour of AI (“vision, RL, LLMs, diffusion, etc.”) tends to produce:
- vocabulary without competence,
- demos without measurement,
- confidence without falsifiability.

Instead, we use a **depth-first spine**:
- one coherent system slice,
- repeated evaluation cycles,
- a growing test suite,
- and visible failure modes that students learn to diagnose.

We still include a thin ribbon of breadth:
- short “where this generalizes” notes (e.g., how the same ideas apply to RAG, DL training, or agents),
- but **breadth never replaces measurement**.

---

## Why not a full RAG course (and why this isn’t “anti-RAG”)
Retrieval-Augmented Generation (RAG) can be valuable in production, but teaching a full end-to-end RAG stack early has costs:

- Many moving parts (ingestion, chunking, indexing, retrieval, reranking, prompting, grounding, evaluation).
- Interactions between knobs create “tuning superstition” if students lack strong evaluation habits.
- Cognitive load is high: architecture details can crowd out methodology.

So the course does **not** center on “full RAG architecture.”

Instead, RAG is treated as:
- **one possible strategy later**, built on top of stable reliability foundations,
- not the first thing students must understand.

---

## Why “Kernel Lite” is the base (kernel-first, strategy-second)
The course is built around **Kernel Lite**, a minimal agent runtime that preserves the **production-relevant invariants** while removing enterprise overhead.

### Kernel-first principle
- **Strategies propose.**
- **Kernel enforces.**
- **All effects go through a gate.**

This separation is the mental model that scales:
- today’s LLM prompts,
- tomorrow’s agent planners,
- any future model family.

### Why it reduces cognitive load
Kernel Lite is a “real system slice” with fewer moving parts than full RAG:
- typed interfaces,
- tool contracts,
- explicit state machine orchestration,
- policy gating and approvals,
- idempotency/replay safety,
- audit logs,
- evaluation harness + adversarial tests.

These are stable ideas that remain true when frameworks change.

---

## Why this is still an AI course (not “just software engineering”)
A common confusion: “If we aren’t training deep nets, is this still AI?”

Yes—because modern AI work is **systems + evaluation**:
- Models are probabilistic components.
- The core difficulty is **reliability under uncertainty**.
- Scientific method + measurement is what separates engineering from demos.

We still include a first class that teaches the fundamental ML ontology:
- model → loss → optimization → generalization,
and connects that directly to why LLMs hallucinate and why reliability mechanisms exist.

---

## How we handle math and coding gaps
### Math
We teach only “math that pays rent,” just-in-time:
- what a function/model is,
- what a loss is,
- what optimization means conceptually,
- why train/test splits exist,
- why uncertainty and generalization matter.

We do **not** require calculus fluency.

### Programming
We assume students are learning Python as they go.
To keep progress real:
- starter code is provided,
- homework focuses on **small changes** and **measured improvements**,
- code review focuses on clarity and tests.

### Use of AI coding assistants (allowed, but accountable)
Students may use AI coding tools to speed up syntax and boilerplate.

However, learning is enforced by requiring:
- a short “what changed and why” note,
- passing tests and reproducible runs,
- a brief error analysis (examples, not vibes).

The goal is: **AI tools amplify learning**, they don’t replace it.

---

## What students will be able to do after the course
Students will be able to:

- Explain (correctly) what “learning” is: **loss minimization + generalization uncertainty**.
- Build a minimal reliable system around an LLM-like component using:
  - typed JSON outputs,
  - schema validation and bounded repair,
  - tool contracts and typed errors,
  - policy gating for side effects,
  - auditing and reproducibility,
  - evaluation packs (including adversarial cases).
- Run the scientific loop on AI systems:
  - propose a hypothesis,
  - change one thing,
  - measure impact,
  - categorize failures,
  - iterate.

That’s the foundation for future deep learning, RAG, and full agent systems.

---

## Spine project (intentionally “application-light”)
The spine is not a flashy app. The spine is a **minimal production-like runtime**:

> A local Kernel Lite agent runtime where strategies propose actions in strict typed form, the kernel enforces safety and budgets, tools run through a contract boundary, and every change is evaluated against a test suite.

This is deliberately chosen because:
- applications are disposable,
- methodology is transferable.

---

## Assessment philosophy (what you are graded on)
We do not grade “how impressive the demo sounds.”

We grade:
- correctness and reproducibility,
- measurement quality,
- controlled experimentation,
- error analysis,
- reliability and safe failure behavior.

