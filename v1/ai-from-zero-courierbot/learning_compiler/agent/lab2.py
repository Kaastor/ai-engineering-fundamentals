from __future__ import annotations

from dataclasses import dataclass, field

from learning_compiler.agent.actions import Action, CallToolAction, MoveAction, StopAction
from learning_compiler.agent.interface import CourierAgent
from learning_compiler.core.json import JsonValue
from learning_compiler.env.grid import GridMap, parse_ascii_map
from learning_compiler.env.types import Direction, Position
from learning_compiler.env.world import WorldObservation
from learning_compiler.planning.search import PlannerBudget, PlannerResult, astar_plan
from learning_compiler.tools.contracts import LookupMapRequest, LookupMapResponse
from learning_compiler.tools.wrappers import ToolCallResult


@dataclass(slots=True)
class Lab2PlanningAgent(CourierAgent):
    """Meeting 2 agent: planning upgrade (A* in a clean world)."""

    planner_budget: PlannerBudget
    _grid_map: GridMap | None = None
    _plan: list[Direction] = field(default_factory=list)
    _last_plan_stats: dict[str, JsonValue] | None = None

    def decide(self, obs: WorldObservation) -> Action:
        if self._grid_map is None:
            return CallToolAction(request=LookupMapRequest())

        if obs.at_goal:
            return StopAction(reason="reached_goal")

        if not self._plan:
            self._compute_plan(start=obs.position, goal=obs.goal)

        if not self._plan:
            return StopAction(reason="no_plan")

        direction = self._plan.pop(0)
        return MoveAction(direction=direction)

    def observe_tool_result(self, result: ToolCallResult) -> None:
        if isinstance(result.parsed, LookupMapResponse):
            parsed = parse_ascii_map(result.parsed.map_text)
            self._grid_map = parsed.grid_map
            self._plan.clear()  # recompute on next decide()

    def observe_move_result(self, *, direction: Direction, succeeded: bool) -> None:
        _ = direction
        if not succeeded:
            # Replan if the world doesn't behave as expected.
            self._plan.clear()

    def snapshot(self) -> JsonValue:
        return {
            "known_map": self._grid_map is not None,
            "remaining_plan_len": len(self._plan),
            "last_plan": self._last_plan_stats,
        }

    def _compute_plan(self, *, start: Position, goal: Position) -> None:
        if self._grid_map is None:
            self._plan.clear()
            return
        result: PlannerResult = astar_plan(
            self._grid_map,
            start=start,
            goal=goal,
            door_unlocked=True,  # planning in a clean world (ignore door locks)
            budget=self.planner_budget,
        )
        self._plan = list(result.plan.moves)
        self._last_plan_stats = {
            "expansions": result.stats.expansions,
            "max_frontier": result.stats.max_frontier,
        }
