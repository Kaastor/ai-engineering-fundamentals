from __future__ import annotations

from dataclasses import dataclass

from learning_compiler.agent.actions import Action, CallToolAction, MoveAction, StopAction
from learning_compiler.agent.interface import CourierAgent
from learning_compiler.core.hashing import stable_hash_hex
from learning_compiler.core.json import JsonValue
from learning_compiler.env.grid import GridMap, parse_ascii_map
from learning_compiler.env.types import Direction, manhattan
from learning_compiler.env.world import WorldObservation
from learning_compiler.tools.contracts import LookupMapRequest, LookupMapResponse
from learning_compiler.tools.wrappers import ToolCallResult


@dataclass(slots=True)
class Lab1HardcodedAgent(CourierAgent):
    """Meeting 1 agent: minimal loop + evidence.

    Behavior is intentionally simple: fetch the map once, then greedily step toward the goal.
    On the Meeting 1 toy map (no obstacles), this is enough to demonstrate the agent loop and journaling.
    """

    _grid_map: GridMap | None = None

    def decide(self, obs: WorldObservation) -> Action:
        if self._grid_map is None:
            return CallToolAction(request=LookupMapRequest())

        if obs.at_goal:
            return StopAction(reason="reached_goal")

        # Greedy: move along the axis with larger distance to goal.
        dx = obs.goal.x - obs.position.x
        dy = obs.goal.y - obs.position.y
        candidates: list[Direction] = []
        if abs(dx) >= abs(dy):
            candidates.append(Direction.EAST if dx > 0 else Direction.WEST)
            if dy != 0:
                candidates.append(Direction.SOUTH if dy > 0 else Direction.NORTH)
        else:
            candidates.append(Direction.SOUTH if dy > 0 else Direction.NORTH)
            if dx != 0:
                candidates.append(Direction.EAST if dx > 0 else Direction.WEST)

        # If preferred is blocked, try any unblocked direction that reduces Manhattan distance.
        for d in candidates:
            if not obs.blocked(d):
                return MoveAction(direction=d)

        cur_dist = manhattan(obs.position, obs.goal)
        for d in Direction.all():
            if obs.blocked(d):
                continue
            nxt = obs.position.moved(d)
            if manhattan(nxt, obs.goal) < cur_dist:
                return MoveAction(direction=d)

        return StopAction(reason="stuck")

    def observe_tool_result(self, result: ToolCallResult) -> None:
        if isinstance(result.parsed, LookupMapResponse):
            parsed = parse_ascii_map(result.parsed.map_text)
            self._grid_map = parsed.grid_map

    def observe_move_result(self, *, direction: Direction, succeeded: bool) -> None:
        # Meeting 1: no internal state to update besides what we learn from observations.
        _ = (direction, succeeded)

    def snapshot(self) -> JsonValue:
        if self._grid_map is None:
            return {"known_map": None}
        return {
            "known_map": {
                "sha": stable_hash_hex([str(self._grid_map.width), str(self._grid_map.height), str(len(self._grid_map.walls))]),
                "door": None if self._grid_map.door is None else {"x": self._grid_map.door.x, "y": self._grid_map.door.y},
            }
        }
