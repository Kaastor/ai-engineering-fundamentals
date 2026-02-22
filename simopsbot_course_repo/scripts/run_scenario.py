from __future__ import annotations

import argparse
from pathlib import Path

from learning_compiler.agent.loop import run_agent
from learning_compiler.agent.state import AgentProfile, AgentRunConfig
from learning_compiler.types import IncidentType


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one SimOpsBot scenario and write a JSONL journal.")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--profile", type=str, default="week5", choices=[p.value for p in AgentProfile])
    parser.add_argument("--out", type=Path, default=Path("outputs"))
    parser.add_argument(
        "--incident",
        type=str,
        default=None,
        choices=[i.value for i in IncidentType],
        help="Optional incident override (mostly for eval debugging).",
    )
    args = parser.parse_args()

    profile = AgentProfile(args.profile)
    cfg = AgentRunConfig(seed=args.seed, profile=profile)
    incident = IncidentType(args.incident) if args.incident is not None else None

    result = run_agent(config=cfg, out_dir=args.out, incident_override=incident)
    print(result.to_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
