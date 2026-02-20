from __future__ import annotations

import argparse
from pathlib import Path

from learning_compiler.env.map_gen import MapGenConfig
from learning_compiler.learning.behavior_cloning import train_behavior_cloning_model
from learning_compiler.learning.knn import KnnConfig
from learning_compiler.planning.search import PlannerBudget


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1, help="Base seed for dataset generation.")
    ap.add_argument("--out", type=Path, default=Path("data/knn_model.json"))
    ap.add_argument("--train-maps", type=int, default=80)
    ap.add_argument("--test-maps", type=int, default=20)
    ap.add_argument("--k", type=int, default=7)
    args = ap.parse_args()

    model, report = train_behavior_cloning_model(
        seed=args.seed,
        train_maps=args.train_maps,
        test_maps=args.test_maps,
        map_cfg=MapGenConfig(width=10, height=10, wall_density=0.18, place_door=False),
        planner_budget=PlannerBudget(max_expansions=10_000),
        knn_config=KnnConfig(k=args.k),
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    model.save(args.out)

    print("Saved:", args.out)
    print("TrainReport:", report)


if __name__ == "__main__":
    main()
