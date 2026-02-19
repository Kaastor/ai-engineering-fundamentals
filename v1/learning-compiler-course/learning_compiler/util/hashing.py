from __future__ import annotations

import dataclasses
import hashlib
import json
from collections.abc import Mapping, Sequence
from enum import Enum
from typing import Final


_JSON_SEPARATORS: Final[tuple[str, str]] = (",", ":")


def stable_json_dumps(value: object) -> str:
    """Serialize *deterministically* to JSON.

    - keys are sorted
    - whitespace is removed
    - non-ASCII is preserved (UTF-8)

    This function is intentionally strict: unknown types raise TypeError so callers
    are forced to model protocol fields explicitly.
    """

    jsonable = _to_jsonable(value)
    return json.dumps(
        jsonable,
        sort_keys=True,
        separators=_JSON_SEPARATORS,
        ensure_ascii=False,
    )


def stable_sha256_hex(value: object) -> str:
    """Compute a stable SHA-256 hash of the deterministic JSON serialization."""

    payload = stable_json_dumps(value).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _to_jsonable(value: object) -> object:
    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Enum):
        # Enums serialize to their values; prefer str/int values in Enum definitions.
        return _to_jsonable(value.value)

    if dataclasses.is_dataclass(value):
        fields = dataclasses.fields(value)
        return {f.name: _to_jsonable(getattr(value, f.name)) for f in fields}

    if isinstance(value, Mapping):
        # JSON keys must be strings.
        return {str(k): _to_jsonable(v) for k, v in value.items()}

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_to_jsonable(v) for v in value]

    raise TypeError(f"Value of type {type(value).__name__} is not JSON-serializable here")
