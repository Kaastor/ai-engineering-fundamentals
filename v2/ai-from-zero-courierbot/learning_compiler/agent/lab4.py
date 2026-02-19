from __future__ import annotations

from dataclasses import dataclass

from learning_compiler.agent.actions import Action, CallToolAction, MoveAction, StopAction
from learning_compiler.agent.interface import CourierAgent
from learning_compiler.core.json import JsonValue
from learning_compiler.env.grid import GridMap, parse_ascii_map
from learning_compiler.env.types import Direction
from learning_compiler.env.world import WorldObservation
from learning_compiler.learning.knn import KnnModel
from learning_compiler.tools.contracts import LookupMapRequest, LookupMapResponse
from learning_compiler.tools.wrappers import ToolCallResult


@dataclass(slots=True)
class Lab4LearnedAgent(CourierAgent):
    """Meeting 4 agent: learned policy as a component (behavior cloning)."""

    model: KnnModel
    _grid_map: GridMap | None = None

    def decide(self, obs: WorldObservation) -> Action:
        if self._grid_map is None:
            return CallToolAction(request=LookupMapRequest())

        if obs.at_goal:
            return StopAction(reason="reached_goal")

        vector = (
            obs.goal.x - obs.position.x,
            obs.goal.y - obs.position.y,
            int(obs.blocked_north),
            int(obs.blocked_south),
            int(obs.blocked_east),
            int(obs.blocked_west),
        )
        predicted = self.model.predict(vector)

        if not obs.blocked(predicted):
            return MoveAction(direction=predicted)

        # Fallback: pick the first unblocked direction in a fixed order.
        for d in Direction.all():
            if not obs.blocked(d):
                return MoveAction(direction=d)

        return StopAction(reason="stuck")

    def observe_tool_result(self, result: ToolCallResult) -> None:
        if isinstance(result.parsed, LookupMapResponse):
            self._grid_map = parse_ascii_map(result.parsed.map_text).grid_map

    def observe_move_result(self, *, direction: Direction, succeeded: bool) -> None:
        _ = (direction, succeeded)

    def snapshot(self) -> JsonValue:
        return {
            "known_map": self._grid_map is not None,
            "policy": "knn",
            "k": self.model.config.k,
            "train_points": len(self.model.vectors),
        }
