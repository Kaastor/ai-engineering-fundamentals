"""Tool response validation.

A core invariant of reliable agentic systems is:

> tool outputs are **observations**, not truth-by-default.

That means:
- parse strictly,
- reject malformed data,
- ignore trailing injection-like text,
- record warnings in the journal.

We validate *raw strings* into typed `ToolResponse` objects.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from learning_compiler.core.errors import ToolValidationError
from learning_compiler.tools.contracts import (
    ConfirmDoorResponse,
    DoorUnlockResponse,
    LookupMapResponse,
    ReportDeliveryResponse,
    ScanDoorResponse,
    ToolName,
    ToolResponse,
)


@dataclass(frozen=True, slots=True)
class ToolParseInfo:
    trailing_text: str | None

    @property
    def had_trailing_text(self) -> bool:
        return self.trailing_text is not None and self.trailing_text.strip() != ""


def validate_tool_response(tool: ToolName, raw: str) -> tuple[ToolResponse, ToolParseInfo]:
    """Parse a raw tool response string into a typed response.

    We accept a leading JSON object and ignore trailing text, but we *report* it via ToolParseInfo.
    """

    decoder = json.JSONDecoder()
    try:
        obj, idx = decoder.raw_decode(raw)
    except json.JSONDecodeError as e:
        raise ToolValidationError(f"invalid JSON from tool {tool.value}: {e.msg}") from e

    trailing = raw[idx:]
    if not isinstance(obj, dict):
        raise ToolValidationError(f"tool {tool.value} must return a JSON object")

    info = ToolParseInfo(trailing_text=trailing if trailing.strip() else None)
    return (_parse_object(tool, obj), info)


def _parse_object(tool: ToolName, obj: Mapping[str, Any]) -> ToolResponse:
    match tool:
        case ToolName.LOOKUP_MAP:
            map_text = _require_str(obj, "map_text", tool)
            return LookupMapResponse(map_text=map_text)
        case ToolName.SCAN_DOOR:
            reported = _require_bool(obj, "reported_locked", tool)
            return ScanDoorResponse(reported_locked=reported)
        case ToolName.CONFIRM_DOOR:
            locked = _require_bool(obj, "is_locked", tool)
            return ConfirmDoorResponse(is_locked=locked)
        case ToolName.DOOR_UNLOCK:
            unlocked = _require_bool(obj, "unlocked", tool)
            return DoorUnlockResponse(unlocked=unlocked)
        case ToolName.REPORT_DELIVERY:
            accepted = _require_bool(obj, "accepted", tool)
            return ReportDeliveryResponse(accepted=accepted)

    # Exhaustiveness guard.
    raise ToolValidationError(f"unknown tool: {tool.value}")


def _require_str(obj: Mapping[str, Any], key: str, tool: ToolName) -> str:
    v = obj.get(key)
    if not isinstance(v, str):
        raise ToolValidationError(f"tool {tool.value} missing/invalid '{key}' (expected str)")
    return v


def _require_bool(obj: Mapping[str, Any], key: str, tool: ToolName) -> bool:
    v = obj.get(key)
    if not isinstance(v, bool):
        raise ToolValidationError(f"tool {tool.value} missing/invalid '{key}' (expected bool)")
    return v
