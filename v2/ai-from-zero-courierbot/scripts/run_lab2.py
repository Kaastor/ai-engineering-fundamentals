from __future__ import annotations

import argparse
from pathlib import Path

from learning_compiler.orchestration.runner import run_scenario
from learning_compiler.orchestration.scenarios import LAB2_OBSTACLES
from learning_compiler.orchestration.stages import (
    CourseStage,
    default_budgets,
    default_fault_plan,
    default_tool_allowlist,
    tool_call_budget,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", type=Path, default=Path("runs"))
    args = ap.parse_args()

    stage = CourseStage.LAB2
    budgets = default_budgets(stage)
    scenario = LAB2_OBSTACLES

    summary = run_scenario(
        stage=stage,
        seed=args.seed,
        scenario_name=scenario.name,
        parsed_map=scenario.parse(),
        budgets=budgets,
        allowlist=default_tool_allowlist(stage),
        fault_plan=default_fault_plan(stage, seed=args.seed),
        tool_budget=tool_call_budget(budgets),
        out_dir=args.out,
    )
    print(summary)


if __name__ == "__main__":
    main()
