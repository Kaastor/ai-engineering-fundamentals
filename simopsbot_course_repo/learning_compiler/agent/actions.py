from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal, TypeAlias

from learning_compiler.types import JSONValue, ServiceName

Version: TypeAlias = Literal["v1", "v2"]


class ActionType(StrEnum):
    OBSERVE_METRICS = "OBSERVE_METRICS"
    OBSERVE_LOGS = "OBSERVE_LOGS"
    OBSERVE_HEALTH = "OBSERVE_HEALTH"
    RUNBOOK_SEARCH = "RUNBOOK_SEARCH"
    ACT_RESTART = "ACT_RESTART"
    ACT_ROLLBACK = "ACT_ROLLBACK"
    ASK_USER = "ASK_USER"
    FINAL = "FINAL"


@dataclass(slots=True, frozen=True)
class ObserveMetrics:
    service: ServiceName
    window_minutes: int = 5

    @property
    def type(self) -> ActionType:
        return ActionType.OBSERVE_METRICS

    def to_json(self) -> dict[str, JSONValue]:
        return {"type": self.type.value, "service": self.service, "window_minutes": self.window_minutes}


@dataclass(slots=True, frozen=True)
class ObserveLogs:
    service: ServiceName
    n: int = 10

    @property
    def type(self) -> ActionType:
        return ActionType.OBSERVE_LOGS

    def to_json(self) -> dict[str, JSONValue]:
        return {"type": self.type.value, "service": self.service, "n": self.n}


@dataclass(slots=True, frozen=True)
class ObserveHealth:
    service: ServiceName

    @property
    def type(self) -> ActionType:
        return ActionType.OBSERVE_HEALTH

    def to_json(self) -> dict[str, JSONValue]:
        return {"type": self.type.value, "service": self.service}


@dataclass(slots=True, frozen=True)
class RunbookSearch:
    query: str

    @property
    def type(self) -> ActionType:
        return ActionType.RUNBOOK_SEARCH

    def to_json(self) -> dict[str, JSONValue]:
        return {"type": self.type.value, "query": self.query}


@dataclass(slots=True, frozen=True)
class ActRestart:
    service: ServiceName

    @property
    def type(self) -> ActionType:
        return ActionType.ACT_RESTART

    def to_json(self) -> dict[str, JSONValue]:
        return {"type": self.type.value, "service": self.service}


@dataclass(slots=True, frozen=True)
class ActRollback:
    service: ServiceName
    version: Version

    @property
    def type(self) -> ActionType:
        return ActionType.ACT_ROLLBACK

    def to_json(self) -> dict[str, JSONValue]:
        return {"type": self.type.value, "service": self.service, "version": self.version}


@dataclass(slots=True, frozen=True)
class AskUser:
    question: str

    @property
    def type(self) -> ActionType:
        return ActionType.ASK_USER

    def to_json(self) -> dict[str, JSONValue]:
        return {"type": self.type.value, "question": self.question}


@dataclass(slots=True, frozen=True)
class Final:
    summary: str
    evidence_refs: tuple[str, ...]

    @property
    def type(self) -> ActionType:
        return ActionType.FINAL

    def to_json(self) -> dict[str, JSONValue]:
        return {
            "type": self.type.value,
            "summary": self.summary,
            "evidence_refs": list(self.evidence_refs),
        }


Action: TypeAlias = (
    ObserveMetrics
    | ObserveLogs
    | ObserveHealth
    | RunbookSearch
    | ActRestart
    | ActRollback
    | AskUser
    | Final
)


def is_side_effect(action: Action) -> bool:
    return isinstance(action, (ActRestart, ActRollback))
