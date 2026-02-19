from __future__ import annotations

import random

from learning_compiler.learning.rl import GridWorldMDP, q_learning
from learning_compiler.planning.gridworld import GridPos, GridWorld, Move


def test_q_learning_is_deterministic_for_seed() -> None:
    world = GridWorld(
        width=5,
        height=4,
        walls=frozenset({GridPos(1, 1), GridPos(2, 1), GridPos(3, 1)}),
        start=GridPos(0, 0),
        goal=GridPos(4, 3),
    )
    mdp = GridWorldMDP(world=world)

    rl1 = q_learning(mdp=mdp, rng=random.Random(7), episodes=250, epsilon=0.25)
    rl2 = q_learning(mdp=mdp, rng=random.Random(7), episodes=250, epsilon=0.25)

    assert rl1.policy == rl2.policy
    assert rl1.policy[GridPos(0, 0)] == Move.DOWN
    assert rl1.policy[GridPos(0, 2)] == Move.RIGHT
