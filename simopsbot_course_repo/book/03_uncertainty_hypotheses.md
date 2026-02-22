# Chapter 3 — Operational Uncertainty: Hypotheses and Evidence Links

## 3.1 Uncertainty without heavy math

In production systems, data is:
- incomplete,
- delayed,
- noisy,
- sometimes adversarial.

Therefore, the agent should maintain **competing hypotheses** rather than pretending to be certain.

## 3.2 Hypotheses as disciplined honesty

A hypothesis record contains:
- a candidate cause (e.g., “bad deploy”),
- a confidence level (low/medium/high),
- evidence references (journal event IDs).

This is not probability theory. It is a pragmatic substitute:
- it makes uncertainty explicit,
- it ties claims to evidence,
- it triggers safe behavior when confidence is low.

## 3.3 Ask vs act

When confidence is low and actions are risky, a good agent should:
- gather more evidence (observe),
- ask a human,
- or abstain.

## 3.4 Worked example: ambiguity resolved by additional observation

Scenario: API latency is high. This could be:
- DB saturation (dependency slow), or
- network flakiness (timeouts).

A cautious agent first inspects:
- DB latency metrics,
- API logs for timeout signatures.

Only after evidence accumulates does it act.

## 3.5 Exercises

1. Inspect `learning_compiler/agent/hypotheses.py`. What evidence triggers each incident type?
2. Propose one additional heuristic (simple rule) and implement it.
