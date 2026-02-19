# Meeting 3 — Behavior II: Uncertainty, Beliefs, and Asking Questions (agents in messy worlds)

## Learning objectives

By the end of this meeting you should be able to:

- Explain probability as **bookkeeping for uncertainty** (discrete, no calculus required).
- Use Bayes’ rule as an **update operator**: prior → evidence → posterior.
- Explain what a **belief state** is and why it matters when the world is partially observed.
- Treat “clarify vs act” as a **decision problem** with explicit costs.
- Apply trust discipline: treat retrieved text and tool output as **observations**, not commands.

## Probability as bookkeeping

Probability in agentic systems is not about mystical randomness.
It is a pragmatic language for representing uncertainty.

**Definition (Belief).**  
A belief is a probability distribution over hypotheses: “how plausible each possibility is.”

If you are unsure whether a sensor is correct, you represent that uncertainty explicitly.
That is intellectual honesty, in math form.

## Bayes’ rule as an update operator

Bayes’ rule in discrete form:

\[
P(H \mid E) = \frac{P(E \mid H) P(H)}{P(E)}
\]

Interpretation:

- \(P(H)\) is the **prior**: what you believed before seeing evidence.
- \(P(E \mid H)\) is the **likelihood**: how compatible the evidence is with each hypothesis.
- \(P(H \mid E)\) is the **posterior**: what you believe after seeing evidence.

### A belief update diagram

```mermaid
flowchart LR
    Prior[Prior belief P(H)] --> Update[Bayes update]
    Evidence[Evidence E] --> Update
    Model[Likelihood model P(E|H)] --> Update
    Update --> Posterior[Posterior belief P(H|E)]
```

## Belief states (POMDP intuition without heavy math)

In many real systems you cannot observe the full state of the world.
You observe a noisy projection of it.

**Definition (Belief state).**  
A belief state is a probability distribution over hidden world states.

This is a core idea behind Partially Observable Markov Decision Processes (POMDPs),
but you do not need the full formalism to benefit from the intuition:

> When you can’t see the whole world, you carry a probability distribution over what might be true.

## Clarify vs act: asking questions as actions

A common beginner mistake is to treat asking questions as “extra” or “optional.”
For agents, **asking is an action** with:

- a cost (time, user annoyance, money),
- a benefit (reduced uncertainty).

### Worked example (two boxes + noisy sensor)

Hidden state: which box contains the prize (A or B).  
Prior: uniform (50/50).  
Sensor accuracy: 75%.

If the sensor says “A”, then:

\[
P(A \mid \text{sensor says A}) =
\frac{0.5 \cdot 0.75}{0.5 \cdot 0.75 + 0.5 \cdot 0.25} = 0.75
\]

Now you choose between:

- **Act**: pick the most likely box (expected cost = probability of being wrong × cost of being wrong).
- **Clarify**: ask a question / gather information (expected cost = cost of asking).

**Decision rule (informal):**
> Ask when the cost of being wrong is high *and* your uncertainty is high.

This is the agent version of “measure twice, cut once.”

### Analogy: shipping a package
If you are shipping a cheap sticker, you might not pay for tracking.
If you are shipping a passport, you probably do.
The action (buy tracking) is justified by the expected cost of failure.

## Trust discipline: tools for facts, models for transformation

Modern agents often combine:
- **tools** (databases, search, APIs) for factual queries,
- **models** for summarization, translation, planning, and transformation.

But the critical rule is:

> Tool output is an observation, not truth by default.

Why?
Because tools can fail, tools can be stale, tools can be poisoned, and the internet is adversarial.

### Prompt injection as “hostile observations”
Indirect prompt injection is a modern example of an old idea:

> Some observations are adversarial and attempt to control you.

A malicious web page might contain text that looks like instructions.
A robust system treats it as input data and enforces policies outside the model.

---

Next: **Meeting 4 — Learning: supervised learning and reinforcement learning as ways to obtain behavior**.
