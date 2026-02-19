# Meeting 3 — Uncertainty Upgrade (Beliefs + Ask vs Act)

## Central question

What should an agent do when it can’t trust what it sees?

This meeting adds a noisy sensor: a door scan that is wrong 20% of the time.
The agent maintains a **belief** about whether the door is locked.

---

## Glossary (minimal)

- **Prior:** belief before seeing new evidence.
- **Posterior:** belief after incorporating evidence.
- **Bayes update:** a rule for updating beliefs using conditional probabilities.
- **Belief state:** a representation of uncertainty over hidden variables.
- **Ask vs act:** a decision strategy: ask when uncertainty is high and error cost is high.

---

## Bayes update (binary form)

Hypothesis: `D` = “door is locked”.

Observation: `O` = “scan reports locked”.

We store `P(D=True)`.

If the scan is 80% correct:

- `P(O=True | D=True) = 0.8`
- `P(O=True | D=False) = 0.2`

Bayes rule gives:

```
P(D=True | O) = P(O | D=True) P(D=True) / P(O)
```

In code, see `learning_compiler/agent/belief.py`.

---

## Where the decision happens

When the plan wants to move through the door:

1. If we have no recent scan, call `scan_door`.
2. Update belief using Bayes.
3. Decide:
   - **unlock** if `P(locked)` is high,
   - **proceed** if `P(locked)` is low,
   - **ask for confirmation** if in the uncertain middle.

This is implemented in `learning_compiler/agent/lab3.py`.

---

## Analogy

Think of the scan like a flaky friend who’s right 80% of the time:
you don’t ignore them, but you also don’t bet your life savings on a single text message.

---

## Exercise

1. Run `python scripts/run_lab3.py --seed 1`.
2. Find the step where a `scan_door` happens.
3. Track `belief_p_locked` across the next few steps.
4. Explain why the agent chose “confirm” or “unlock.”
