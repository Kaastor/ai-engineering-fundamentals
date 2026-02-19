Here’s a 6‑meeting (6×1h) “AI-from-zero” curriculum for 2nd‑year undergrads who can code but are math‑shy, with **Agentic Systems as the spine** and “timeless foundations” as the vibe.

The throughline is simple and ancient:

> **An AI system is an agent that repeatedly**
> **observes → decides → acts → verifies → stops**
> under uncertainty and resource limits. 

And the modern 2026 twist (still timeless) is also simple:

> **The model is a component, not the system.**
> A real agent is **Behavior + Reliability + Evaluation**. 

---

## The 6‑meeting curriculum

### Meeting 1 — The Big Map: What “AI” actually is (Agentic Systems anatomy)

**Goal:** Give students a mental model that survives hype cycles.

**Scope**

* **Russell/Norvig agent view:** agent = mapping from percept history to actions; rationality as “doing the right thing given what you know and what you want.”
* The **Agentic Systems anatomy**:
  **Behavior** (how it decides), **Reliability** (how it keeps working), **Evaluation** (how you know it’s good). 
* The **six canonical objects** that make agents debuggable and non-magical:
  **Intent, State, Plan, Action, Observation, Evidence**. 
* The “adult” invariants (non-negotiables) that separate demos from systems:
  budgets/stop rules, mediation of side effects, effect typing, reproducibility, trust discipline, measurability, operability. 
* Why the 2026 world cares: autonomy without these invariants becomes a haunted house with a credit card.

**Why here?**
Because it prevents the most common beginner error: treating AI as “a model that outputs answers” instead of “a decision-making loop embedded in software.” This one hour shapes how they interpret *everything* later.

---

### Meeting 2 — Behavior I: Search & Planning (how agents decide in clean worlds)

**Goal:** Teach “decision = structured computation,” not vibes.

**Scope**

* Problem formulation: state space, actions, transition model, goal test, path cost.
* Core algorithms (math-light, code-first intuition):
  BFS/DFS, Uniform Cost Search, **A***, heuristics as “useful lies with guarantees.”
* Plans vs policies: **a plan is a sequence; a policy is a rule for what to do next**.
* Task decomposition as a planning skill: turning vague goals into **checkable subgoals** (so verification becomes possible). 
* Stopping rules: “when are we done?” as an explicit design choice, not a feeling. 

**Why this is foundational (and timeless):**
Search is the “assembly language” of agency. Even when a neural model proposes steps, the *structure* of reasoning is still search/planning over a space of possibilities.

---

### Meeting 3 — Behavior II: Uncertainty, Beliefs, and Asking Questions (agents in messy worlds)

**Goal:** Make uncertainty a first-class citizen—because real agents live in fog.

**Scope**

* Probability as **bookkeeping for uncertainty** (no calculus; discrete examples).
* Bayes rule as an *update operator*: prior → evidence → posterior.
* Markov idea + belief state intuition: when you can’t see the full state, you maintain a belief about it (POMDP intuition, no heavy formalism).
* **Clarify vs act** as a decision problem:
  Ask a question when uncertainty is high *and* the cost of being wrong is high; otherwise take safe information‑gathering actions. 
* “Tools for facts, models for transformation” + **trust discipline**: treat tool outputs and retrieved text as **observations**, not truth-by-default. 
* A sneak preview of adversarial reality: indirect prompt injection is just “hostile observations pretending to be commands.” 

**Why here (before ML)?**
Because most ML courses accidentally teach students to be overconfident. Agency requires calibrated uncertainty handling: when to query, when to verify, when to abstain.

---

### Meeting 4 — Learning for Agents: How policies get acquired (without drowning in math)

**Goal:** Put ML/DL in the right mental box: **learning is one way to get behavior**, not the definition of AI.

**Scope**

* Three ways to get behavior:

  1. hand-designed rules/search,
  2. learned predictors (supervised learning),
  3. learned decision-making (reinforcement learning).
* Supervised learning in one sentence: learn a function that generalizes beyond the training set; failure modes: overfitting, dataset shift, spurious correlations.
* Reinforcement learning as “learning a policy from reward”:

  * MDP intuition: states, actions, rewards, transitions
  * Value functions (what’s good long-term), exploration vs exploitation
* The key conceptual bridge:
  **Planning = compute actions using a model of the world.**
  **RL = learn actions (or values) from experience.**
* Why deep learning matters but is not the foundation: neural nets are flexible function approximators; the agent loop and evaluation discipline still rule your life.

**Why this matters in 2026:**
Students will see endless “just fine-tune it / just add a bigger model” talk. This session inoculates them: learning is powerful, but agency is broader—and often fails for reasons *outside* the model.

---

### Meeting 5 — Reliability: Turning behavior into software that doesn’t betray you

**Goal:** Teach the engineering physics of agents: failures, side effects, and safety boundaries.

**Scope**

* **State machines/workflows**: make the loop explicit (states, transitions, guards, timeouts). 
* Tool boundaries and contracts: schemas, validation, normalized error taxonomy. 
* Reliability primitives that outlive frameworks:

  * timeouts, retries with backoff
  * **idempotency** (the “don’t double-charge the user” spell) 
  * circuit breakers and safe degradation
  * concurrency rules: parallelize reads, serialize writes 
* Security boundaries (timeless, not “LLM-specific”):

  * least privilege, allowlists, deterministic policy enforcement outside the model 
  * the mantra: **“the model proposes; the system disposes.”** 
* Observability and evidence:

  * run journal (black box recorder), stable IDs, replayability 
  * why “we can’t reproduce it” is not an acceptable ending

**Why it’s in an AI course at all:**
Because the AI boom is increasingly about **agents with tools**. If students only learn “models,” they’ll build impressive failures. Reliability is how agency touches reality without causing expensive folklore.

---

### Meeting 6 — Evaluation: The scientific method for AI systems (how you stay honest)

**Goal:** Make evaluation feel like *part of the system*, not an afterthought.

**Scope**

* Specs as the root of evaluation: define success criteria + constraints + budgets. 
* Three evaluation modes:

  * **in-run verification** (did the tool action actually happen?)
  * **offline eval** (fixed suites + regression gates)
  * **online monitoring** (SLIs/SLOs, drift, incident response) 
* Scoring methods: rule checks first; humans for subjective; model-judges only when calibrated. 
* Stochasticity hygiene: repeated trials, variance, tail risk; the “rule of three” intuition for rare bad events. 
* Adversarial evals: injection attempts, tool poisoning, permission probes as test cases, not “security later.” 
* Close with the “stay-sane map”:

  * fast-changing: prompts/framework APIs
  * slow-changing: state machines, idempotency, observability, evaluation discipline 

**Why this is the finale:**
Because evaluation is what turns AI into an engineering discipline instead of a performance art. It also gives students a compass for the next few years of hype: *“show me the spec and the eval.”*

---

## Why these six, in this order

1. **Agents first** so everything has a home.
   Search, probability, learning, and even deep nets become *tools for building policies* rather than disconnected topics.

2. **Behavior before Learning** because agency is about decision structure.
   Many students (and many companies) learn ML first and then try to duct-tape it into an agent. That’s backwards.

3. **Uncertainty early** because it trains intellectual honesty.
   The best agents aren’t the most confident—they’re the most evidence-driven and well-calibrated.

4. **Reliability + Evaluation are treated as core AI**, not “ops stuff.”
   In 2026, autonomy + tool use makes reliability and evaluation non-optional. The principles here outlive today’s models and libraries. 

5. **Math-light by design, but not concept-light.**
   Every session can be taught with discrete examples, simulation thinking, and pseudocode. Students who later want the math can “attach” it naturally:

   * Search → complexity/optimality proofs (optional depth)
   * Beliefs → formal probability/graphical models
   * RL → Bellman equations and function approximation theory

---

## What students should walk away believing (the “mind-shaping” part)

* AI is not synonymous with deep learning. AI is **goal-directed behavior under constraints**.
* A model can suggest; only a system can safely act. 
* If you can’t specify “good,” you can’t improve anything—only change it.
* The future belongs to builders who can connect **behavior + reliability + evaluation** into one coherent loop. 

That’s a six‑hour foundation that will still make sense to them in 2030, even if the 2026 toolchain fossils itself into museum exhibits.
