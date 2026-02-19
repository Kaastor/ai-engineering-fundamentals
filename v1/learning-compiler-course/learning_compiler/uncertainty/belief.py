from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from learning_compiler.uncertainty.bayes import DiscreteDistribution, bayes_update, normalize


class Box(str, Enum):
    A = "A"
    B = "B"


class SensorReading(str, Enum):
    SAYS_A = "says_A"
    SAYS_B = "says_B"


@dataclass(frozen=True, slots=True)
class ClarifyVsAct:
    """A small decision record used in Meeting 3."""

    posterior: DiscreteDistribution[Box]
    chosen_box: Box
    expected_cost_act: float
    expected_cost_ask: float
    should_ask: bool


def initial_belief() -> DiscreteDistribution[Box]:
    return normalize({Box.A: 1.0, Box.B: 1.0})


def sensor_model(*, accuracy: float) -> Mapping[tuple[SensorReading, Box], float]:
    """P(reading | true_box)."""

    if not (0.0 < accuracy < 1.0):
        raise ValueError("accuracy must be in (0, 1)")

    return {
        (SensorReading.SAYS_A, Box.A): accuracy,
        (SensorReading.SAYS_A, Box.B): 1.0 - accuracy,
        (SensorReading.SAYS_B, Box.A): 1.0 - accuracy,
        (SensorReading.SAYS_B, Box.B): accuracy,
    }


def observe_sensor(*, true_box: Box, accuracy: float, rng: random.Random) -> SensorReading:
    model = sensor_model(accuracy=accuracy)
    p_says_a = model[(SensorReading.SAYS_A, true_box)]
    return SensorReading.SAYS_A if rng.random() < p_says_a else SensorReading.SAYS_B


def update_belief(
    *, prior: DiscreteDistribution[Box], reading: SensorReading, accuracy: float
) -> DiscreteDistribution[Box]:
    model = sensor_model(accuracy=accuracy)
    likelihood = {h: model[(reading, h)] for h in prior.support()}
    return bayes_update(prior=prior, likelihood=likelihood)


def decide_clarify_vs_act(
    *,
    posterior: DiscreteDistribution[Box],
    wrong_cost: float,
    ask_cost: float,
) -> ClarifyVsAct:
    """Choose between asking (information gathering) and acting immediately.

    - If you *act* by choosing a box, expected cost is P(wrong) * wrong_cost.
    - If you *ask*, you pay ask_cost but then choose correctly (assume perfect info).

    This is intentionally simplistic; the point is to make the trade-off explicit.
    """

    if wrong_cost < 0.0 or ask_cost < 0.0:
        raise ValueError("Costs must be non-negative")

    p_a = posterior.prob(Box.A)
    p_b = posterior.prob(Box.B)

    chosen = Box.A if p_a >= p_b else Box.B
    p_wrong = 1.0 - max(p_a, p_b)
    expected_act = p_wrong * wrong_cost
    expected_ask = ask_cost

    return ClarifyVsAct(
        posterior=posterior,
        chosen_box=chosen,
        expected_cost_act=expected_act,
        expected_cost_ask=expected_ask,
        should_ask=expected_ask < expected_act,
    )
