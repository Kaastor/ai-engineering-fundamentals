from __future__ import annotations

import random

from learning_compiler.uncertainty.belief import (
    Box,
    ClarifyVsAct,
    decide_clarify_vs_act,
    initial_belief,
    observe_sensor,
    update_belief,
)


def run(*, seed: int) -> str:
    rng = random.Random(seed)

    prior = initial_belief()
    true_box = Box.A if rng.random() < 0.5 else Box.B
    accuracy = 0.75
    reading = observe_sensor(true_box=true_box, accuracy=accuracy, rng=rng)
    posterior = update_belief(prior=prior, reading=reading, accuracy=accuracy)

    high_stakes = decide_clarify_vs_act(posterior=posterior, wrong_cost=10.0, ask_cost=1.0)
    low_stakes = decide_clarify_vs_act(posterior=posterior, wrong_cost=1.0, ask_cost=1.0)

    lines: list[str] = []
    lines.append("# Lab 3 — Uncertainty, Beliefs, Asking Questions")
    lines.append("")
    lines.append(f"True hidden state (for simulation): prize_in={true_box.value}")
    lines.append(f"Sensor reading: {reading.value} (accuracy={accuracy:.2f})")
    lines.append("")
    lines.append("Prior:")
    lines.append(f"- P(A)={prior.prob(Box.A):.3f}, P(B)={prior.prob(Box.B):.3f}")
    lines.append("Posterior after Bayes update:")
    lines.append(f"- P(A)={posterior.prob(Box.A):.3f}, P(B)={posterior.prob(Box.B):.3f}")
    lines.append(f"- entropy={posterior.entropy_bits():.3f} bits")
    lines.append("")
    lines.append("## Clarify vs act as a decision problem")
    lines.append(_format("High stakes", high_stakes))
    lines.append(_format("Low stakes", low_stakes))

    lines.append("")
    lines.append("Key idea: asking a question is an *action* with a cost. You ask when the")
    lines.append("expected cost of being wrong is larger than the cost of asking.")

    return "\n".join(lines)


def _format(title: str, d: ClarifyVsAct) -> str:
    decision = "ASK" if d.should_ask else f"ACT (choose {d.chosen_box.value})"
    return (
        f"### {title}\n"
        f"- chosen_box_if_act: {d.chosen_box.value}\n"
        f"- expected_cost_act: {d.expected_cost_act:.3f}\n"
        f"- expected_cost_ask: {d.expected_cost_ask:.3f}\n"
        f"- decision: **{decision}**\n"
    )
