# Meeting 4 — Learning Upgrade (Behavior Cloning)

## Central question

How can behavior be acquired from data—and why does it still fail?

This meeting adds supervised learning as a component:
we learn a mapping from state features to actions using examples.

---

## Glossary (minimal)

- **Supervised learning:** learn a function from input-output examples.
- **Policy:** a mapping from observed state to action.
- **Generalization:** performing well on new examples, not just memorizing training data.
- **Dataset shift:** deployment conditions differ from training conditions.

---

## Behavior cloning in one sentence

Use an “expert” (the planner) to generate training examples, then learn to imitate it.

In code:

- `scripts/run_lab4_train.py` generates data with A\* and trains a tiny kNN model.
- `scripts/run_lab4_run.py` runs CourierBot using the learned policy.

Learning modules:

- `learning_compiler/learning/dataset.py`
- `learning_compiler/learning/knn.py`

---

## Features (intentionally simple)

We use discrete features:

- `dx_to_goal`, `dy_to_goal`
- blocked flags for N/S/E/W

This keeps the representation inspectable and the math minimal.

---

## Failure modes to expect

- **Overfitting**: a model performs very well on training data but worse on new maps.
- **Shift**: a model trained on sparse obstacles performs poorly when obstacle density increases.

These are not moral failures; they are predictable consequences of data and assumptions.

---

## Analogy

A learned policy is like a student who studied only last year’s exam:
they can do great if the exam is similar, and crash spectacularly if the instructor changes the questions.

---

## Exercise

1. Train: `python scripts/run_lab4_train.py --seed 1 --k 7`
2. Run: `python scripts/run_lab4_run.py --seed 1 --map-seed 123`
3. Then change `--map-seed` to something larger (new map).
4. Compare run journals:
   - steps,
   - “stuck” stops,
   - differences in chosen moves.
