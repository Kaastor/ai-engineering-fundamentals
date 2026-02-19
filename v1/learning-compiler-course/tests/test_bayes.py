from __future__ import annotations

from learning_compiler.uncertainty.belief import Box, SensorReading, initial_belief, update_belief


def test_bayes_update_uniform_prior() -> None:
    prior = initial_belief()
    posterior = update_belief(prior=prior, reading=SensorReading.SAYS_A, accuracy=0.75)

    assert abs(posterior.prob(Box.A) - 0.75) < 1e-9
    assert abs(posterior.prob(Box.B) - 0.25) < 1e-9
