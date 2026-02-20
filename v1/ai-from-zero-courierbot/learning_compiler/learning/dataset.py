"""Dataset generation for behavior cloning (Meeting 4).

We generate training data by using the planner (A*) as an "expert" and recording:
    features(state) -> expert_action

This is deliberately not "AI magic": it is supervised learning as a systems choice.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from learning_compiler.env.features import extract_local_features
from learning_compiler.env.map_gen import MapGenConfig, generate_map
from learning_compiler.env.types import Direction
from learning_compiler.planning.search import PlannerBudget, astar_plan


@dataclass(frozen=True, slots=True)
class Example:
    features: tuple[int, int, int, int, int, int]
    label: Direction


@dataclass(frozen=True, slots=True)
class Dataset:
    examples: tuple[Example, ...]

    def __len__(self) -> int:
        return len(self.examples)

    def labels(self) -> tuple[Direction, ...]:
        return tuple(ex.label for ex in self.examples)


def generate_expert_dataset(
    *,
    seeds: Iterable[int],
    map_cfg: MapGenConfig,
    planner_budget: PlannerBudget,
) -> Dataset:
    examples: list[Example] = []
    for seed in seeds:
        grid_map = generate_map(seed, map_cfg)
        plan = astar_plan(
            grid_map,
            start=grid_map.start,
            goal=grid_map.goal,
            door_unlocked=True,
            budget=planner_budget,
        ).plan.moves

        pos = grid_map.start
        for step_dir in plan:
            feats = extract_local_features(
                grid_map,
                position=pos,
                goal=grid_map.goal,
                door_unlocked=True,
            ).as_vector()
            examples.append(Example(features=feats, label=step_dir))
            pos = pos.moved(step_dir)

    return Dataset(examples=tuple(examples))
