from __future__ import annotations

import json
from typing import cast

from learning_compiler.agent.actions import (
    ActRestart,
    ActRollback,
    Action,
    ActionType,
    AskUser,
    Final,
    ObserveHealth,
    ObserveLogs,
    ObserveMetrics,
    RunbookSearch,
    Version,
)
from learning_compiler.types import ServiceName


class ActionValidationError(Exception):
    pass


def parse_action_proposal(raw: str) -> Action:
    """Parse and validate a model proposal into a typed Action.

    Invalid proposals are *errors*, not creativity.
    """

    try:
        obj: object = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ActionValidationError("proposal is not valid JSON") from e
    d = _expect_dict(obj)
    action_type = _expect_str(d.get("type"))
    try:
        at = ActionType(action_type)
    except ValueError as e:
        raise ActionValidationError(f"unknown action type: {action_type!r}") from e

    if at is ActionType.OBSERVE_METRICS:
        service = _parse_service(d.get("service"))
        window = _expect_int_default(d.get("window_minutes"), default=5)
        if window <= 0 or window > 60:
            raise ActionValidationError("window_minutes out of range")
        return ObserveMetrics(service=service, window_minutes=window)

    if at is ActionType.OBSERVE_LOGS:
        service = _parse_service(d.get("service"))
        n = _expect_int_default(d.get("n"), default=10)
        if n <= 0 or n > 200:
            raise ActionValidationError("n out of range")
        return ObserveLogs(service=service, n=n)

    if at is ActionType.OBSERVE_HEALTH:
        service = _parse_service(d.get("service"))
        return ObserveHealth(service=service)

    if at is ActionType.RUNBOOK_SEARCH:
        query = _expect_str(d.get("query"))
        if len(query) > 200:
            raise ActionValidationError("query too long")
        return RunbookSearch(query=query)

    if at is ActionType.ACT_RESTART:
        service = _parse_service(d.get("service"))
        return ActRestart(service=service)

    if at is ActionType.ACT_ROLLBACK:
        service = _parse_service(d.get("service"))
        version_s = _expect_str(d.get("version"))
        version = _parse_version(version_s)
        return ActRollback(service=service, version=version)

    if at is ActionType.ASK_USER:
        question = _expect_str(d.get("question"))
        if len(question) > 400:
            raise ActionValidationError("question too long")
        return AskUser(question=question)

    if at is ActionType.FINAL:
        summary = _expect_str(d.get("summary"))
        refs = d.get("evidence_refs")
        evidence_refs = _parse_evidence_refs(refs)
        return Final(summary=summary, evidence_refs=evidence_refs)

    raise ActionValidationError(f"unhandled action type: {action_type}")


def _expect_dict(obj: object) -> dict[str, object]:
    if not isinstance(obj, dict):
        raise ActionValidationError("proposal must be a JSON object")
    out: dict[str, object] = {}
    for k, v in obj.items():
        if not isinstance(k, str):
            raise ActionValidationError("proposal has non-string key")
        out[k] = v
    return out


def _expect_str(obj: object) -> str:
    if not isinstance(obj, str):
        raise ActionValidationError("expected string field")
    return obj


def _expect_int_default(obj: object, *, default: int) -> int:
    if obj is None:
        return default
    if not isinstance(obj, int):
        raise ActionValidationError("expected int field")
    return obj


def _parse_service(obj: object) -> ServiceName:
    s = _expect_str(obj)
    if s not in ("api", "db"):
        raise ActionValidationError(f"unknown service: {s!r}")
    return cast(ServiceName, s)


def _parse_version(value: str) -> Version:
    if value not in ("v1", "v2"):
        raise ActionValidationError(f"invalid version: {value!r}")
    return cast(Version, value)


def _parse_evidence_refs(obj: object) -> tuple[str, ...]:
    if not isinstance(obj, list):
        raise ActionValidationError("evidence_refs must be a list")
    out: list[str] = []
    for v in obj:
        if not isinstance(v, str):
            raise ActionValidationError("evidence_refs must be list[str]")
        out.append(v)
    return tuple(out)
