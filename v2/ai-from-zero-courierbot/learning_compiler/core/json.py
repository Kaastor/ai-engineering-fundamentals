"""Small JSON helpers with precise types."""
from __future__ import annotations

import json
from typing import TypeAlias

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


def dumps_compact(value: JsonValue) -> str:
    """Deterministic JSON encoding (stable key ordering, no whitespace)."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
