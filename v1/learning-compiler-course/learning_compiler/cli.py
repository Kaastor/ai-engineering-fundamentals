from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Callable

from learning_compiler import __version__
from learning_compiler.labs import (
    lab1_big_map,
    lab2_search,
    lab3_uncertainty,
    lab4_learning,
    lab5_reliability,
    lab6_evaluation,
)


@dataclass(frozen=True, slots=True)
class Command:
    name: str
    run: Callable[[int], str]


_COMMANDS: tuple[Command, ...] = (
    Command(name="lab1", run=lambda seed: lab1_big_map.run(seed=seed)[0]),
    Command(name="lab2", run=lambda seed: lab2_search.run(seed=seed)[0]),
    Command(name="lab3", run=lambda seed: lab3_uncertainty.run(seed=seed)),
    Command(name="lab4", run=lambda seed: lab4_learning.run(seed=seed)[0]),
    Command(name="lab5", run=lambda seed: lab5_reliability.run(seed=seed)),
    Command(name="lab6", run=lambda seed: lab6_evaluation.run(seed=seed)),
)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="lc", description="Learning Compiler course CLI")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)
    for cmd in _COMMANDS:
        p = sub.add_parser(cmd.name, help=f"Run {cmd.name}")
        p.add_argument("--seed", type=int, default=7, help="Deterministic seed (default: 7)")

    args = parser.parse_args(argv)

    cmd = next((c for c in _COMMANDS if c.name == args.command), None)
    if cmd is None:
        raise RuntimeError(f"Unknown command: {args.command}")

    output = cmd.run(args.seed)
    print(output)  # noqa: T201 - CLI is an I/O edge
    return 0
