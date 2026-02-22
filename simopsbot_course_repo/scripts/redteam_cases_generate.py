from __future__ import annotations

import argparse
from pathlib import Path

from learning_compiler.sim.redteam import generate_redteam_cases


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic red-team cases (untrusted snippets).")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--out", type=Path, default=Path("outputs/redteam_cases.txt"))
    args = parser.parse_args()

    cases = generate_redteam_cases(seed=args.seed, n=args.n)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(cases) + "\n", encoding="utf-8")
    print(f"Wrote {len(cases)} cases to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
