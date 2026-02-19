"""Tool request/response contracts.

Tools are **simulated** in this repository. The important part is the boundary:
the agent can *request* a tool call, but the system decides whether to execute it,
and validates the output before it affects state.

We keep the contracts explicit and typed (no stringly-typed dict soup).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ToolName(str, Enum):
    LOOKUP_MAP = "lookup_map"
    SCAN_DOOR = "scan_door"
    CONFIRM_DOOR = "confirm_door"
    DOOR_UNLOCK = "door_unlock"
    REPORT_DELIVERY = "report_delivery"


# -------------------------
# Requests
# -------------------------


@dataclass(frozen=True, slots=True)
class LookupMapRequest:
    tool: ToolName = ToolName.LOOKUP_MAP


@dataclass(frozen=True, slots=True)
class ScanDoorRequest:
    tool: ToolName = ToolName.SCAN_DOOR


@dataclass(frozen=True, slots=True)
class ConfirmDoorRequest:
    tool: ToolName = ToolName.CONFIRM_DOOR


@dataclass(frozen=True, slots=True)
class DoorUnlockRequest:
    """Unlocks the door (side-effectful).

    The **system** should populate `idempotency_key`.
    """

    idempotency_key: str | None = None
    tool: ToolName = ToolName.DOOR_UNLOCK


@dataclass(frozen=True, slots=True)
class ReportDeliveryRequest:
    """Reports delivery at the destination (side-effectful).

    The **system** should populate `idempotency_key`.
    """

    idempotency_key: str | None = None
    tool: ToolName = ToolName.REPORT_DELIVERY


ToolRequest = (
    LookupMapRequest
    | ScanDoorRequest
    | ConfirmDoorRequest
    | DoorUnlockRequest
    | ReportDeliveryRequest
)


# -------------------------
# Validated responses
# -------------------------


@dataclass(frozen=True, slots=True)
class LookupMapResponse:
    map_text: str


@dataclass(frozen=True, slots=True)
class ScanDoorResponse:
    reported_locked: bool


@dataclass(frozen=True, slots=True)
class ConfirmDoorResponse:
    is_locked: bool


@dataclass(frozen=True, slots=True)
class DoorUnlockResponse:
    unlocked: bool


@dataclass(frozen=True, slots=True)
class ReportDeliveryResponse:
    accepted: bool


ToolResponse = (
    LookupMapResponse
    | ScanDoorResponse
    | ConfirmDoorResponse
    | DoorUnlockResponse
    | ReportDeliveryResponse
)
