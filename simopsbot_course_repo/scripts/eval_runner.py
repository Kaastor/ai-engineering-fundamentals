from __future__ import annotations

import argparse
from pathlib import Path

from learning_compiler.agent.state import AgentProfile
from learning_compiler.eval.runner import run_eval


def main() -> int:
    parser = argparse.ArgumentParser(description="Run offline evaluation suite for SimOpsBot.")
    parser.add_argument("--profile", type=str, default="week5", choices=[p.value for p in AgentProfile])
    parser.add_argument(
        "--seeds",
        type=str,
        default="0:50",
        help="Seed list. Examples: '0:50' (range), '1,2,3'. End is exclusive for ranges.",
    )
    parser.add_argument("--out", type=Path, default=Path("outputs/eval"))
    args = parser.parse_args()

    profile = AgentProfile(args.profile)
    seeds = _parse_seeds(args.seeds)

    report = run_eval(profile=profile, seeds=seeds, out_dir=args.out)
    print((args.out / "eval_summary.md").read_text(encoding="utf-8"))
    print(f"Gate passed: {report.gate.passed}")
    return 0


def _parse_seeds(spec: str) -> list[int]:
    s = spec.strip()
    if ":" in s:
        left, right = s.split(":", maxsplit=1)
        start = int(left) if left else 0
        end = int(right)
        if end < start:
            raise ValueError("range end must be >= start")
        return list(range(start, end))
    if "," in s:
        return [int(x.strip()) for x in s.split(",") if x.strip()]
    return [int(s)]


if __name__ == "__main__":
    raise SystemExit(main())
