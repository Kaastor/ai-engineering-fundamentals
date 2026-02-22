from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from learning_compiler.agent.loop import run_agent
from learning_compiler.agent.state import AgentProfile, AgentResult, AgentRunConfig
from learning_compiler.eval.gate import DEFAULT_THRESHOLDS, GateResult, GateThresholds, check_gate
from learning_compiler.eval.metrics import EvalMetrics, compute_metrics
from learning_compiler.eval.scenario_generator import incident_for_seed
from learning_compiler.types import JSONValue
from learning_compiler.utils.json import canonical_dumps


@dataclass(slots=True, frozen=True)
class EvalReport:
    profile: AgentProfile
    seeds: tuple[int, ...]
    metrics: EvalMetrics
    gate: GateResult
    results: tuple[AgentResult, ...]

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "profile": self.profile.value,
            "seeds": list(self.seeds),
            "metrics": {
                "total_runs": self.metrics.total_runs,
                "recovery_success_rate": self.metrics.recovery_success_rate,
                "mean_steps": self.metrics.mean_steps,
                "verification_success_rate": self.metrics.verification_success_rate,
                "evidence_compliance_rate": self.metrics.evidence_compliance_rate,
                "unsafe_action_attempt_rate": self.metrics.unsafe_action_attempt_rate,
            },
            "gate": {"passed": self.gate.passed, "reasons": list(self.gate.reasons)},
            "results": [r.to_json() for r in self.results],
        }


def run_eval(
    *,
    profile: AgentProfile,
    seeds: list[int],
    out_dir: Path,
    thresholds: GateThresholds | None = None,
) -> EvalReport:
    """Run an offline evaluation suite across seeds."""

    out_dir.mkdir(parents=True, exist_ok=True)
    runs_dir = out_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    results: list[AgentResult] = []
    for seed in seeds:
        cfg = AgentRunConfig(seed=seed, profile=profile)
        incident = incident_for_seed(seed)
        result = run_agent(config=cfg, out_dir=runs_dir, incident_override=incident)
        results.append(result)

    metrics = compute_metrics(results=results)
    gate = check_gate(metrics=metrics, thresholds=thresholds or DEFAULT_THRESHOLDS)

    report = EvalReport(profile=profile, seeds=tuple(seeds), metrics=metrics, gate=gate, results=tuple(results))

    _write_outputs(out_dir=out_dir, report=report)
    return report


def _write_outputs(*, out_dir: Path, report: EvalReport) -> None:
    (out_dir / "eval_summary.json").write_text(canonical_dumps(report.to_json()), encoding="utf-8")

    md_lines: list[str] = []
    md_lines.append(f"# Eval Summary ({report.profile.value})")
    md_lines.append("")
    md_lines.append("## Metrics")
    md_lines.append("")
    md_lines.append(report.metrics.to_markdown())
    md_lines.append("")
    md_lines.append("## Regression gate")
    md_lines.append("")
    md_lines.append(f"- Passed: **{report.gate.passed}**")
    if report.gate.reasons:
        md_lines.append("- Reasons:")
        for r in report.gate.reasons:
            md_lines.append(f"  - {r}")
    else:
        md_lines.append("- Reasons: none")

    (out_dir / "eval_summary.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    # One JSON per line for simple grepping.
    with (out_dir / "results.jsonl").open("w", encoding="utf-8") as fp:
        for r in report.results:
            fp.write(canonical_dumps(r.to_json()))
            fp.write("\n")
