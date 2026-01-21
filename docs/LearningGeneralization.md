# Class 1 (60 minutes): What is “learning”?
## A model is a function fit by optimizing a loss on data, and generalization is never guaranteed

### Why this class exists
This course will be “kernel-first” and reliability-first. That only makes sense if students first understand:

- what “a model” is,
- what it means to “learn,”
- why evaluation is non-negotiable,
- why LLM failures (hallucinations) are not surprising.

This class sets the mindset for everything that follows.

---

## Learning objectives (students should be able to…)
By the end of this class, a student should be able to:

1. Define a model as **a function with parameters**.
2. Explain learning as **choosing parameters to minimize a loss on data**.
3. Explain why **generalization** is the goal and why it is uncertain.
4. Run a simple train/validation/test experiment and interpret results.
5. Do basic error analysis: inspect failures, categorize them, propose a fix.
6. Connect this to LLMs: next-token prediction loss, stochastic outputs, hallucination as a failure mode of generalization + missing grounding.

---

## Minimal math (kept honest, not heavy)
Only these concepts are used:

- **Function:** input → output (e.g., text → label)
- **Parameters:** knobs inside the function
- **Loss:** a number that measures error (lower is better)
- **Optimization:** a procedure that reduces loss (conceptually hill-climbing)
- **Generalization:** performance on unseen data

No calculus is required, but the concepts must be correct.

---

## In-class plan (60 minutes)

### 0–5 min — Course framing: AI as measurement-driven work
- “AI is experimentation with measurement.”
- The course loop: hypothesis → change → measure → error analysis.
- What we will not do: prompt tricks without evaluation.

**Instructor note:** Keep it crisp. This is the course “constitution.”

---

### 5–15 min — The ontology: model, parameters, loss
Whiteboard / slides with one simple example:

- Model: \( f_\theta(x) \)  
  - \(x\) = input  
  - \(\theta\) = parameters  
  - \(f\) = prediction function

- Loss: \( L(\theta) \) measures how wrong predictions are on data.

Key statement:
> Learning = choosing \(\theta\) to make the loss smaller on training examples.

Then immediately add the warning:
> Minimizing training loss does **not** guarantee generalization.

---

### 15–30 min — Tiny supervised baseline (NLP-flavored)
Goal: show a complete experiment quickly.

Use a small text classification dataset (can be toy-sized):
- Example tasks: spam vs not spam, sentiment, topic label.

Pipeline:
1. Split data into train/test (and optionally validation).
2. Vectorize text (TF-IDF).
3. Train logistic regression (or similar simple classifier).
4. Evaluate: accuracy + confusion matrix (or precision/recall/F1).

Show:
- training score
- test score
- one or two misclassified examples

**Instructor note:** Students must see that “the numbers can be computed” and are not magical.

---

### 30–40 min — Overfitting demonstration (the “generalization is not guaranteed” punch)
Pick one controlled “bad idea” that makes training performance look better without improving test performance.

Examples:
- add overly specific n-grams
- crank model complexity
- intentionally introduce leakage (only as a cautionary demo)

Then compare:
- train metric goes up,
- test metric stays the same or goes down.

Name it:
- **overfitting** = memorizing patterns that don’t transfer.

---

### 40–50 min — Error analysis as a first-class skill
Give students 5–10 misclassified examples and ask:

- What pattern do you see?
- Is the label wrong?
- Is the input ambiguous?
- Is the model missing a feature?

Introduce the idea of a **failure taxonomy**, even if simple:
- ambiguity
- missing context
- rare phrasing
- negation
- out-of-domain

This previews later kernel work: systems fail in categories, not randomly.

---

### 50–60 min — Bridge to LLMs (GenAI connection without mysticism)
Explain LLM training as the same ontology:

- The model is a function \( f_\theta(\text{context}) \to \text{next token distribution} \).
- The loss is usually next-token prediction loss (cross-entropy).
- Optimization minimizes that loss on massive text data.
- At inference, the model samples tokens → outputs vary.
- Hallucination is expected when:
  - the context is insufficient,
  - the model is pressured to answer anyway,
  - there is no grounding/verification.

Key takeaway:
> LLMs are not databases. They are probability engines trained to predict plausible continuations.

This motivates why the rest of the course focuses on:
- typed outputs,
- validation,
- refusal/clarification,
- policies and gates,
- evaluation suites.

---

## Homework 1 (starter-code friendly)
### Goal
Practice the scientific loop on a simple model.

### Required deliverables
1. **Baseline run** with metrics (train + test).
2. **One controlled change** (exactly one major change), and re-run metrics.
3. **Short error analysis**:
   - show 5 failure examples,
   - categorize them (at least 2 categories),
   - propose a next experiment.

### Allowed controlled changes (choose one)
- preprocessing improvement (lowercasing, punctuation handling, stopwords)
- feature change (char n-grams vs word n-grams)
- regularization strength change
- class weighting for imbalance
- threshold tuning (if using probabilities)

### Rules (enforces learning, even with AI coding tools)
- You may use AI coding assistants.
- You must include a short note: “what changed and why I expected it to help.”
- Your submission must be reproducible (one command or one notebook run cell).

---

## Optional extension (for fast students)
- Create a “leakage trap” example: show an easy way to accidentally cheat evaluation.
- Explain why it’s invalid and how to fix the split.

This extension sets up Class 2’s security mindset.
