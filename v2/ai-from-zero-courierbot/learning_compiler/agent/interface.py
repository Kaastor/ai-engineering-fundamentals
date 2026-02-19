"""Agent interface.

The system runs an agent by:
1) giving it a world observation,
2) receiving an action proposal,
3) executing that action (subject to budgets and tool permissions),
4) returning structured results (including validated tool responses).

This is the central course worldview:
- the **agent** is a component,
- the **system** owns budgets, verification, and tool boundaries.
"""
from __future__ import annotations

from typing import Protocol

from learning_compiler.agent.actions import Action
from learning_compiler.core.json import JsonValue
from learning_compiler.env.types import Direction
from learning_compiler.env.world import WorldObservation
from learning_compiler.tools.wrappers import ToolCallResult


class CourierAgent(Protocol):
    def decide(self, obs: WorldObservation) -> Action:
        ...

    def observe_tool_result(self, result: ToolCallResult) -> None:
        ...

    def observe_move_result(self, *, direction: Direction, succeeded: bool) -> None:
        ...

    def snapshot(self) -> JsonValue:
        ...
