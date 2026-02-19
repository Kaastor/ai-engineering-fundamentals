from __future__ import annotations

import argparse
from pathlib import Path

from learning_compiler.env.grid import parse_ascii_map, render_ascii_map
from learning_compiler.env.map_gen import MapGenConfig, generate_map
from learning_compiler.learning.knn import KnnModel
from learning_compiler.orchestration.runner import run_scenario
from learning_compiler.orchestration.stages import (
    CourseStage,
    default_budgets,
    default_fault_plan,
    default_tool_allowlist,
    tool_call_budget,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1, help="Seed for the run.")
    ap.add_argument("--model", type=Path, default=Path("data/knn_model.json"))
    ap.add_argument("--out", type=Path, default=Path("runs"))
    ap.add_argument("--map-seed", type=int, default=123, help="Seed for the generated test map.")
    args = ap.parse_args()

    model = KnnModel.load(args.model)

    stage = CourseStage.LAB4
    budgets = default_budgets(stage)

    grid_map = generate_map(args.map_seed, MapGenConfig(width=10, height=10, wall_density=0.18, place_door=False))
    map_text = render_ascii_map(grid_map, door_unlocked=False)
    parsed = parse_ascii_map(map_text)

    summary = run_scenario(
        stage=stage,
        seed=args.seed,
        scenario_name=f"lab4_generated_{args.map_seed}",
        parsed_map=parsed,
        budgets=budgets,
        allowlist=default_tool_allowlist(stage),
        fault_plan=default_fault_plan(stage, seed=args.seed),
        tool_budget=tool_call_budget(budgets),
        out_dir=args.out,
        knn_model=model,
    )
    print(summary)


if __name__ == "__main__":
    main()
