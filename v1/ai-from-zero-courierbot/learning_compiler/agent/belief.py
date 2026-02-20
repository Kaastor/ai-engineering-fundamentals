"""Simple belief tracking (Meeting 3).

We intentionally keep probability discrete and table-based: one binary variable.

Variable:
- `D` = door is locked (True/False)

We store `P(D=True)` and update using Bayes rule given noisy observations.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DoorBelief:
    p_locked: float

    def __post_init__(self) -> None:
        if not (0.0 <= self.p_locked <= 1.0):
            raise ValueError("p_locked must be in [0, 1]")

    def update_from_scan(
        self,
        *,
        reported_locked: bool,
        p_report_locked_given_locked: float,
        p_report_locked_given_unlocked: float,
    ) -> DoorBelief:
        posterior = bayes_update_binary(
            prior_true=self.p_locked,
            observed_true=reported_locked,
            p_obs_true_given_true=p_report_locked_given_locked,
            p_obs_true_given_false=p_report_locked_given_unlocked,
        )
        return DoorBelief(p_locked=posterior)


def bayes_update_binary(
    *,
    prior_true: float,
    observed_true: bool,
    p_obs_true_given_true: float,
    p_obs_true_given_false: float,
) -> float:
    """Bayes update for a binary hypothesis given a binary observation.

    - Hypothesis: H in {True, False}
    - Observation: O in {True, False}
    Inputs encode:
    - P(H=True) (prior_true)
    - P(O=True | H=True) (p_obs_true_given_true)
    - P(O=True | H=False) (p_obs_true_given_false)

    Returns:
    - P(H=True | O=observed_true)
    """

    if not (0.0 <= prior_true <= 1.0):
        raise ValueError("prior_true must be in [0, 1]")
    for p in (p_obs_true_given_true, p_obs_true_given_false):
        if not (0.0 <= p <= 1.0):
            raise ValueError("conditional probabilities must be in [0, 1]")

    if observed_true:
        p_o_given_h = p_obs_true_given_true
        p_o_given_not_h = p_obs_true_given_false
    else:
        p_o_given_h = 1.0 - p_obs_true_given_true
        p_o_given_not_h = 1.0 - p_obs_true_given_false

    numerator = p_o_given_h * prior_true
    denominator = numerator + p_o_given_not_h * (1.0 - prior_true)
    if denominator == 0.0:
        # This only happens with inconsistent probability inputs. We treat it as a caller error.
        raise ValueError("denominator is zero; check conditional probabilities")
    return numerator / denominator
