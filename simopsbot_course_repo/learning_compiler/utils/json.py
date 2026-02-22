from __future__ import annotations

import json
from typing import IO

from learning_compiler.types import JSONValue


def canonical_dumps(value: JSONValue) -> str:
    """Serialize JSON in a stable way (for determinism + diffability)."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def write_jsonl_line(fp: IO[str], value: JSONValue) -> None:
    fp.write(canonical_dumps(value))
    fp.write("\n")
