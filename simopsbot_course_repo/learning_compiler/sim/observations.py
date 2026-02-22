from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from learning_compiler.types import JSONValue, ServiceName, ToolName


class HealthStatus(StrEnum):
    OK = "ok"
    DEGRADED = "degraded"
    DOWN = "down"


@dataclass(slots=True, frozen=True)
class MetricsObservation:
    tool: ToolName
    service: ServiceName
    window_minutes: int
    error_rate: float
    latency_ms: float

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "tool": self.tool.value,
            "service": self.service,
            "window_minutes": self.window_minutes,
            "error_rate": round(self.error_rate, 6),
            "latency_ms": round(self.latency_ms, 3),
        }


@dataclass(slots=True, frozen=True)
class LogsObservation:
    tool: ToolName
    service: ServiceName
    lines: tuple[str, ...]

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "tool": self.tool.value,
            "service": self.service,
            "lines": list(self.lines),
        }


@dataclass(slots=True, frozen=True)
class HealthObservation:
    tool: ToolName
    service: ServiceName
    status: HealthStatus
    details: dict[str, str]

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "tool": self.tool.value,
            "service": self.service,
            "status": self.status.value,
            "details": dict(self.details),
        }


@dataclass(slots=True, frozen=True)
class RunbookObservation:
    tool: ToolName
    query: str
    snippets: tuple[str, ...]

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "tool": self.tool.value,
            "query": self.query,
            "snippets": list(self.snippets),
        }


@dataclass(slots=True, frozen=True)
class ActionReceipt:
    tool: ToolName
    service: ServiceName
    idempotency_key: str
    applied: bool
    message: str

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "tool": self.tool.value,
            "service": self.service,
            "idempotency_key": self.idempotency_key,
            "applied": self.applied,
            "message": self.message,
        }
