"""Agent action types.

Actions are proposals from the agent. The *system* executes them subject to budgets and tool allowlists.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from learning_compiler.env.types import Direction
from learning_compiler.tools.contracts import ToolRequest


@dataclass(frozen=True, slots=True)
class MoveAction:
    direction: Direction
    kind: Literal["move"] = "move"


@dataclass(frozen=True, slots=True)
class CallToolAction:
    request: ToolRequest
    kind: Literal["call_tool"] = "call_tool"


@dataclass(frozen=True, slots=True)
class StopAction:
    reason: str
    kind: Literal["stop"] = "stop"


Action = MoveAction | CallToolAction | StopAction
