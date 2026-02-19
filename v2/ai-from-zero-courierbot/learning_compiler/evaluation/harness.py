"""Offline evaluation harness (Meeting 6).

This harness runs CourierBot on many seeded scenarios and reports metrics + a regression gate.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from learning_compiler.env.grid import parse_ascii_map, render_ascii_map
from learning_compiler.env.map_gen import MapGenConfig, generate_map
from learning_compiler.evaluation.metrics import EvalMetrics, compute_metrics
from learning_compiler.orchestration.runner import RunSummary, run_scenario
from learning_compiler.orchestration.stages import (
    CourseStage,
    RunBudgets,
    default_budgets,
    default_fault_plan,
    default_tool_allowlist,
    tool_call_budget,
)


@dataclass(frozen=True, slots=True)
class EvalConfig:
    runs: int = 25
    seed_start: int = 1
    map_cfg: MapGenConfig = field(
        default_factory=lambda: MapGenConfig(width=10, height=10, wall_density=0.18, place_door=True)
    )
    min_success_rate: float = 0.8


def run_offline_eval(*, seed: int, out_dir: Path, cfg: EvalConfig) -> tuple[list[RunSummary], EvalMetrics]:
    stage = CourseStage.LAB6
    budgets: RunBudgets = default_budgets(stage)
    allowlist = default_tool_allowlist(stage)

    summaries: list[RunSummary] = []
    for i in range(cfg.runs):
        map_seed = cfg.seed_start + i
        grid_map = generate_map(map_seed, cfg.map_cfg)
        map_text = render_ascii_map(grid_map, door_unlocked=False)
        parsed = parse_ascii_map(map_text)

        summary = run_scenario(
            stage=stage,
            seed=seed,
            scenario_name=f"eval_seed_{map_seed}",
            parsed_map=parsed,
            budgets=budgets,
            allowlist=allowlist,
            fault_plan=default_fault_plan(stage, seed=seed),
            tool_budget=tool_call_budget(budgets),
            out_dir=out_dir,
        )
        summaries.append(summary)

    # Add one explicit adversarial case: lookup_map returns valid JSON + trailing injection text.
    # (Seed 4 is chosen because it deterministically triggers MALFORMED for lookup_map on step 0 for this scenario.)
    adversarial_seed = 4
    adv_map = generate_map(999, cfg.map_cfg)
    adv_text = render_ascii_map(adv_map, door_unlocked=False)
    adv_parsed = parse_ascii_map(adv_text)
    summaries.append(
        run_scenario(
            stage=stage,
            seed=adversarial_seed,
            scenario_name="eval_adversarial",
            parsed_map=adv_parsed,
            budgets=budgets,
            allowlist=allowlist,
            fault_plan=default_fault_plan(stage, seed=adversarial_seed),
            tool_budget=tool_call_budget(budgets),
            out_dir=out_dir,
        )
    )

    metrics = compute_metrics(summaries)
    return summaries, metrics
