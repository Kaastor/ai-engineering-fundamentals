from __future__ import annotations

import argparse
from pathlib import Path

from learning_compiler.evaluation.harness import EvalConfig, run_offline_eval


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1, help="Seed for faults/retries (system-level randomness).")
    ap.add_argument("--out", type=Path, default=Path("runs"))
    ap.add_argument("--runs", type=int, default=25)
    args = ap.parse_args()

    summaries, metrics = run_offline_eval(
        seed=args.seed,
        out_dir=args.out,
        cfg=EvalConfig(runs=args.runs),
    )

    print("\\n=== Offline eval metrics ===")
    print(metrics)

    passed = metrics.regression_gate(min_success_rate=0.8)
    print("Regression gate:", "PASS" if passed else "FAIL")

    # Also print a small failure table for debugging.
    failures = [s for s in summaries if not s.success]
    if failures:
        print("\\nFailures:")
        for f in failures[:10]:
            print("-", f.run_id, f.scenario, f.reason)


if __name__ == "__main__":
    main()
