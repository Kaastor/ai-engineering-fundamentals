"""Serialization helpers for journaling.

We keep serialization in one place so the journal schema stays stable and explicit.
"""

from __future__ import annotations

from learning_compiler.agent.actions import Action, CallToolAction, MoveAction, StopAction
from learning_compiler.core.hashing import stable_hash_hex
from learning_compiler.core.json import JsonValue
from learning_compiler.env.types import Position
from learning_compiler.env.world import WorldObservation
from learning_compiler.tools.contracts import (
    ConfirmDoorRequest,
    ConfirmDoorResponse,
    DoorUnlockRequest,
    DoorUnlockResponse,
    LookupMapRequest,
    LookupMapResponse,
    ReportDeliveryRequest,
    ReportDeliveryResponse,
    ScanDoorRequest,
    ScanDoorResponse,
    ToolName,
    ToolRequest,
    ToolResponse,
)
from learning_compiler.tools.wrappers import ToolCallResult


def position_to_json(pos: Position) -> dict[str, JsonValue]:
    return {"x": pos.x, "y": pos.y}


def world_observation_to_json(obs: WorldObservation) -> dict[str, JsonValue]:
    return {
        "position": position_to_json(obs.position),
        "goal": position_to_json(obs.goal),
        "at_goal": obs.at_goal,
        "blocked": {
            "N": obs.blocked_north,
            "S": obs.blocked_south,
            "E": obs.blocked_east,
            "W": obs.blocked_west,
        },
    }


def action_to_json(action: Action) -> dict[str, JsonValue]:
    if isinstance(action, MoveAction):
        return {"kind": action.kind, "data": {"direction": action.direction.value}}
    if isinstance(action, CallToolAction):
        return {"kind": action.kind, "data": tool_request_to_json(action.request)}
    if isinstance(action, StopAction):
        return {"kind": action.kind, "data": {"reason": action.reason}}
    raise AssertionError(f"unknown action: {action}")


def tool_request_to_json(req: ToolRequest) -> dict[str, JsonValue]:
    if isinstance(req, LookupMapRequest):
        return {"tool": req.tool.value}
    if isinstance(req, ScanDoorRequest):
        return {"tool": req.tool.value}
    if isinstance(req, ConfirmDoorRequest):
        return {"tool": req.tool.value}
    if isinstance(req, DoorUnlockRequest):
        return {"tool": req.tool.value, "idempotency_key": req.idempotency_key}
    if isinstance(req, ReportDeliveryRequest):
        return {"tool": req.tool.value, "idempotency_key": req.idempotency_key}
    raise AssertionError(f"unknown tool request: {req}")


def tool_response_to_json(tool: ToolName, resp: ToolResponse) -> dict[str, JsonValue]:
    match tool:
        case ToolName.LOOKUP_MAP:
            assert isinstance(resp, LookupMapResponse)
            preview: list[JsonValue] = [line for line in resp.map_text.splitlines()[0:3]]
            return {
                "tool": tool.value,
                "data": {
                    "map_sha": stable_hash_hex([resp.map_text]),
                    "map_preview": preview,
                },
            }
        case ToolName.SCAN_DOOR:
            assert isinstance(resp, ScanDoorResponse)
            return {"tool": tool.value, "data": {"reported_locked": resp.reported_locked}}
        case ToolName.CONFIRM_DOOR:
            assert isinstance(resp, ConfirmDoorResponse)
            return {"tool": tool.value, "data": {"is_locked": resp.is_locked}}
        case ToolName.DOOR_UNLOCK:
            assert isinstance(resp, DoorUnlockResponse)
            return {"tool": tool.value, "data": {"unlocked": resp.unlocked}}
        case ToolName.REPORT_DELIVERY:
            assert isinstance(resp, ReportDeliveryResponse)
            return {"tool": tool.value, "data": {"accepted": resp.accepted}}

    raise AssertionError(f"unknown tool: {tool}")


def tool_call_result_to_json(result: ToolCallResult) -> dict[str, JsonValue]:
    return {
        "tool": result.raw.tool.value,
        "attempts": result.attempts,
        "had_timeout": result.had_timeout,
        "had_validation_error": result.had_validation_error,
        "warnings": {"trailing_text": result.parse_info.trailing_text},
        "parsed": tool_response_to_json(result.raw.tool, result.parsed),
    }
