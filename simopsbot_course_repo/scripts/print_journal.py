from __future__ import annotations

import argparse
from pathlib import Path

from learning_compiler.journal.reader import read_journal
from learning_compiler.types import JSONValue


def main() -> int:
    parser = argparse.ArgumentParser(description="Pretty-print a SimOpsBot JSONL run journal.")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    events = read_journal(args.path)
    for e in events:
        header = f"[step {e.step_id:02d}] {e.kind.value}  id={e.event_id}"
        print(header)
        print(_indent(_pretty_payload(e.payload), prefix="  "))
        print()
    return 0


def _pretty_payload(payload: dict[str, JSONValue]) -> str:
    # Keep it simple: deterministic-ish repr.
    lines: list[str] = []
    for k in sorted(payload.keys()):
        v = payload[k]
        lines.append(f"{k}: {v!r}")
    return "\n".join(lines)


def _indent(text: str, *, prefix: str) -> str:
    return "\n".join(prefix + line for line in text.splitlines())


if __name__ == "__main__":
    raise SystemExit(main())
