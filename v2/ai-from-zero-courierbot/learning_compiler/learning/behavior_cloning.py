"""Behavior cloning utilities (Meeting 4)."""
from __future__ import annotations

from dataclasses import dataclass

from learning_compiler.env.map_gen import MapGenConfig
from learning_compiler.learning.dataset import Dataset, generate_expert_dataset
from learning_compiler.learning.knn import KnnConfig, KnnModel, train_knn
from learning_compiler.planning.search import PlannerBudget


@dataclass(frozen=True, slots=True)
class TrainReport:
    train_size: int
    test_size: int
    train_accuracy: float
    test_accuracy: float


def train_behavior_cloning_model(
    *,
    seed: int,
    train_maps: int,
    test_maps: int,
    map_cfg: MapGenConfig,
    planner_budget: PlannerBudget,
    knn_config: KnnConfig,
) -> tuple[KnnModel, TrainReport]:
    # Deterministic split: contiguous ranges of seeds.
    train_ds = generate_expert_dataset(
        seeds=range(seed, seed + train_maps),
        map_cfg=map_cfg,
        planner_budget=planner_budget,
    )
    test_ds = generate_expert_dataset(
        seeds=range(seed + train_maps, seed + train_maps + test_maps),
        map_cfg=map_cfg,
        planner_budget=planner_budget,
    )

    model = train_knn(
        vectors=(ex.features for ex in train_ds.examples),
        labels=(ex.label for ex in train_ds.examples),
        config=knn_config,
    )

    train_acc = accuracy(model, train_ds)
    test_acc = accuracy(model, test_ds)
    report = TrainReport(
        train_size=len(train_ds),
        test_size=len(test_ds),
        train_accuracy=train_acc,
        test_accuracy=test_acc,
    )
    return model, report


def accuracy(model: KnnModel, ds: Dataset) -> float:
    correct = 0
    for ex in ds.examples:
        if model.predict(ex.features) == ex.label:
            correct += 1
    return correct / max(1, len(ds))
