# Preface

## Purpose

This short “companion book” supports a six‑meeting laboratory course in foundational AI.
The intended audience is second‑year undergraduate students who can program confidently
but do not (yet) have strong mathematical preparation.

The course is designed for February 2026, during a period of intense public attention
to AI systems. The goal is to provide concepts that remain useful after the current
tooling ecosystem changes.

## A single organizing claim

The course uses **agentic systems** as its organizing principle:

> An AI system is an agent that repeatedly  
> **observes → decides → acts → verifies → stops**  
> under uncertainty and resource limits.

Two immediate implications follow:

1. **The model is a component, not the system.**  
   A modern system may include an ML model, an LLM, a search algorithm, or a mix. The system is the loop.

2. **Robust agents require three pillars:**
   - **Behavior**: how decisions are produced.
   - **Reliability**: how the loop keeps working under failures and constraints.
   - **Evaluation**: how you know the system is good, and stays good.

## What you should learn by the end

You should be able to:

- Describe the **agent perspective** (from classical AI) and apply it to modern systems.
- Build small agent loops with explicit:
  - budgets and stop rules,
  - typed actions and mediated side effects,
  - reproducible runs with stable traces,
  - verification and evaluation hooks.
- Recognize common failure modes (overconfidence, dataset shift, tool misuse, non‑reproducibility)
  and apply standard engineering countermeasures.

## How to read this book

Each meeting chapter contains:

- **Definitions** of technical terms in plain language.
- **A diagram** (Mermaid) to structure the mental model.
- **A worked example** (small enough to code).
- **A real‑world example** (to connect the concept to practice).
- **Common pitfalls** (what breaks when you build systems).

The recommended workflow is:

1. Read the chapter before the lab.
2. Run the corresponding `labN` script.
3. Use the run journal and evaluation suite as your primary debugging tools.

## Notation and conventions

- We use **discrete** examples whenever possible (no calculus required).
- Probability is treated as “**bookkeeping for uncertainty**”: a way to update beliefs when new evidence arrives.
- “Tool output” (including retrieved text) is treated as an **observation**, not as truth by default.

---

Next: **Meeting 1 — The Big Map: What “AI” actually is**.
