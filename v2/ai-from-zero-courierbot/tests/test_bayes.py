from __future__ import annotations

from learning_compiler.agent.belief import bayes_update_binary


def test_bayes_update_moves_probability_in_right_direction() -> None:
    # Prior: 50% locked.
    # Observation: scan says locked.
    # Sensor: 80% correct.
    posterior = bayes_update_binary(
        prior_true=0.5,
        observed_true=True,
        p_obs_true_given_true=0.8,
        p_obs_true_given_false=0.2,
    )
    assert posterior > 0.5

    posterior2 = bayes_update_binary(
        prior_true=0.5,
        observed_true=False,
        p_obs_true_given_true=0.8,
        p_obs_true_given_false=0.2,
    )
    assert posterior2 < 0.5
