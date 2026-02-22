from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from learning_compiler.journal.models import JournalEvent, JournalKind
from learning_compiler.types import JSONValue, RunId


class JournalParseError(Exception):
    pass


def read_journal(path: Path) -> list[JournalEvent]:
    events: list[JournalEvent] = []
    for line_no, line in enumerate(_read_lines(path), start=1):
        try:
            obj: object = json.loads(line)
        except json.JSONDecodeError as e:
            raise JournalParseError(f"{path}:{line_no}: invalid JSON") from e
        events.append(_parse_event(obj, path=path, line_no=line_no))
    return events


def _read_lines(path: Path) -> Iterable[str]:
    with path.open("r", encoding="utf-8") as fp:
        for raw in fp:
            line = raw.strip()
            if line:
                yield line


def _parse_event(obj: object, *, path: Path, line_no: int) -> JournalEvent:
    d = _expect_dict(obj, where=f"{path}:{line_no}")
    event_id = _expect_str(d.get("event_id"), where=f"{path}:{line_no}:event_id")
    run_id_s = _expect_str(d.get("run_id"), where=f"{path}:{line_no}:run_id")
    step_id = _expect_int(d.get("step_id"), where=f"{path}:{line_no}:step_id")
    kind_s = _expect_str(d.get("kind"), where=f"{path}:{line_no}:kind")
    payload_obj = d.get("payload")
    payload = _coerce_json_value(payload_obj, where=f"{path}:{line_no}:payload")
    if not isinstance(payload, dict):
        raise JournalParseError(f"{path}:{line_no}: payload must be a JSON object")
    kind = _parse_kind(kind_s, where=f"{path}:{line_no}:kind")
    return JournalEvent(
        event_id=event_id,
        run_id=RunId(run_id_s),
        step_id=step_id,
        kind=kind,
        payload=payload,
    )


def _parse_kind(value: str, *, where: str) -> JournalKind:
    try:
        return JournalKind(value)
    except ValueError as e:
        raise JournalParseError(f"{where}: unknown kind {value!r}") from e


def _expect_dict(obj: object, *, where: str) -> dict[str, object]:
    if not isinstance(obj, dict):
        raise JournalParseError(f"{where}: expected JSON object")
    # json.loads gives dict[str, Any]; re-type to dict[str, object] at the boundary.
    out: dict[str, object] = {}
    for k, v in obj.items():
        if not isinstance(k, str):
            raise JournalParseError(f"{where}: non-string key in object")
        out[k] = v
    return out


def _expect_str(obj: object, *, where: str) -> str:
    if not isinstance(obj, str):
        raise JournalParseError(f"{where}: expected string")
    return obj


def _expect_int(obj: object, *, where: str) -> int:
    if not isinstance(obj, int):
        raise JournalParseError(f"{where}: expected int")
    return obj


def _coerce_json_value(obj: object, *, where: str) -> JSONValue:
    # Recursively validate that obj is JSON-serializable in our type system.
    if obj is None:
        return None
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, int):
        return obj
    if isinstance(obj, float):
        return obj
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return [_coerce_json_value(v, where=where) for v in obj]
    if isinstance(obj, dict):
        out: dict[str, JSONValue] = {}
        for k, v in obj.items():
            if not isinstance(k, str):
                raise JournalParseError(f"{where}: non-string key in object")
            out[k] = _coerce_json_value(v, where=where)
        return out
    raise JournalParseError(f"{where}: value is not valid JSON")
