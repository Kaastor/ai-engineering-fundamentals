from __future__ import annotations

import random
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum

from learning_compiler.learning.rl import GridWorldMDP, q_learning
from learning_compiler.learning.supervised import KnnClassifier, accuracy, make_blob_dataset
from learning_compiler.planning.gridworld import GridPos, GridWorld, Move, render_ascii


class Label(str, Enum):
    RED = "red"
    BLUE = "blue"


@dataclass(frozen=True, slots=True)
class LearningDemoResult:
    train_acc: float
    test_acc: float
    shifted_acc: float
    rl_episodes: int


def run(*, seed: int) -> tuple[str, LearningDemoResult]:
    rng = random.Random(seed)

    # --- Supervised learning demo (kNN) ---
    train = make_blob_dataset(
        rng=rng,
        n_per_class=40,
        centers={Label.RED: (-2.0, -2.0), Label.BLUE: (2.0, 2.0)},
        std=1.0,
    )
    test = make_blob_dataset(
        rng=rng,
        n_per_class=40,
        centers={Label.RED: (-2.0, -2.0), Label.BLUE: (2.0, 2.0)},
        std=1.0,
    )
    shifted = make_blob_dataset(
        rng=rng,
        n_per_class=40,
        centers={Label.RED: (-1.0, 2.5), Label.BLUE: (1.0, -2.5)},
        std=1.0,
    )

    model: KnnClassifier[Label] = KnnClassifier.fit(k=3, examples=train)
    train_acc = accuracy(model=model, data=train)
    test_acc = accuracy(model=model, data=test)
    shifted_acc = accuracy(model=model, data=shifted)

    # --- Reinforcement learning demo (tabular Q-learning) ---
    world = GridWorld(
        width=5,
        height=4,
        walls=frozenset({GridPos(1, 1), GridPos(2, 1), GridPos(3, 1)}),
        start=GridPos(0, 0),
        goal=GridPos(4, 3),
    )
    mdp = GridWorldMDP(world=world)
    rl = q_learning(mdp=mdp, rng=rng, episodes=250, epsilon=0.25)

    lines: list[str] = []
    lines.append("# Lab 4 — Learning for Agents")
    lines.append("")
    lines.append("## Supervised learning: k-NN as a function approximator")
    lines.append(f"- train accuracy: {train_acc:.3f}")
    lines.append(f"- test accuracy (same distribution): {test_acc:.3f}")
    lines.append(f"- test accuracy (dataset shift): {shifted_acc:.3f}")
    lines.append("")
    lines.append("Interpretation:")
    lines.append("- High train accuracy is not enough.")
    lines.append("- Distribution shift is a systems problem, not a math problem.")
    lines.append("")
    lines.append("## Reinforcement learning: tabular Q-learning on a GridWorld MDP")
    lines.append("World:")
    lines.append("```")
    lines.append(render_ascii(world))
    lines.append("```")
    lines.append("")
    lines.append("Greedy policy arrows (learned):")
    lines.append("```")
    lines.append(render_policy(world=world, policy=rl.policy))
    lines.append("```")

    return (
        "\n".join(lines),
        LearningDemoResult(
            train_acc=train_acc,
            test_acc=test_acc,
            shifted_acc=shifted_acc,
            rl_episodes=rl.episodes,
        ),
    )


def render_policy(*, world: GridWorld, policy: Mapping[GridPos, Move]) -> str:
    arrows = {Move.UP: "^", Move.DOWN: "v", Move.LEFT: "<", Move.RIGHT: ">"}

    lines: list[str] = []
    for y in range(world.height):
        row: list[str] = []
        for x in range(world.width):
            p = GridPos(x, y)
            if p == world.start:
                row.append("S")
            elif p == world.goal:
                row.append("G")
            elif p in world.walls:
                row.append("#")
            elif p in policy:
                row.append(arrows[policy[p]])
            else:
                row.append(".")
        lines.append("".join(row))
    return "\n".join(lines)
