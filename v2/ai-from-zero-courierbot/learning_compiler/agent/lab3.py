from __future__ import annotations

from dataclasses import dataclass, field

from learning_compiler.agent.actions import Action, CallToolAction, MoveAction, StopAction
from learning_compiler.agent.belief import DoorBelief
from learning_compiler.agent.interface import CourierAgent
from learning_compiler.core.json import JsonValue
from learning_compiler.env.grid import GridMap, parse_ascii_map
from learning_compiler.env.types import Direction, Position
from learning_compiler.env.world import WorldObservation
from learning_compiler.planning.search import PlannerBudget, PlannerResult, astar_plan
from learning_compiler.tools.contracts import (
    ConfirmDoorRequest,
    ConfirmDoorResponse,
    DoorUnlockRequest,
    DoorUnlockResponse,
    LookupMapRequest,
    LookupMapResponse,
    ScanDoorRequest,
    ScanDoorResponse,
)
from learning_compiler.tools.wrappers import ToolCallResult


@dataclass(slots=True)
class Lab3UncertaintyAgent(CourierAgent):
    """Meeting 3 agent: uncertainty upgrade (belief + ask vs act)."""

    planner_budget: PlannerBudget
    p_scan_correct: float = 0.8
    unlock_threshold: float = 0.85
    proceed_threshold: float = 0.15

    _grid_map: GridMap | None = None
    _plan: list[Direction] = field(default_factory=list)

    _door_belief: DoorBelief = field(default_factory=lambda: DoorBelief(p_locked=0.5))
    _door_unlocked_known: bool = False
    _has_recent_scan: bool = False
    _last_move_target_is_door: bool = False

    def decide(self, obs: WorldObservation) -> Action:
        if self._grid_map is None:
            return CallToolAction(request=LookupMapRequest())

        if obs.at_goal:
            return StopAction(reason="reached_goal")

        if not self._plan:
            self._compute_plan(start=obs.position, goal=obs.goal)

        if not self._plan:
            return StopAction(reason="no_plan")

        next_dir = self._plan[0]
        if self._is_next_step_into_door(current=obs.position, direction=next_dir) and not self._door_unlocked_known:
            return self._handle_door_before_move()

        # Default: execute next move in the plan.
        self._last_move_target_is_door = self._is_next_step_into_door(current=obs.position, direction=next_dir)
        self._plan.pop(0)
        self._has_recent_scan = False  # movement changes context; don't treat old scans as fresh
        return MoveAction(direction=next_dir)

    def observe_tool_result(self, result: ToolCallResult) -> None:
        parsed = result.parsed
        if isinstance(parsed, LookupMapResponse):
            self._grid_map = parse_ascii_map(parsed.map_text).grid_map
            self._plan.clear()
            return

        if isinstance(parsed, ScanDoorResponse):
            self._door_belief = self._door_belief.update_from_scan(
                reported_locked=parsed.reported_locked,
                p_report_locked_given_locked=self.p_scan_correct,
                p_report_locked_given_unlocked=1.0 - self.p_scan_correct,
            )
            self._has_recent_scan = True
            return

        if isinstance(parsed, ConfirmDoorResponse):
            self._door_belief = DoorBelief(p_locked=1.0 if parsed.is_locked else 0.0)
            self._has_recent_scan = True
            return

        if isinstance(parsed, DoorUnlockResponse):
            if parsed.unlocked:
                self._door_unlocked_known = True
                self._door_belief = DoorBelief(p_locked=0.0)
            return

    def observe_move_result(self, *, direction: Direction, succeeded: bool) -> None:
        _ = direction
        if succeeded:
            return
        # If movement failed and we were trying to enter the door tile, treat it as strong evidence
        # that the door is locked.
        if self._last_move_target_is_door:
            self._door_belief = DoorBelief(p_locked=1.0)
            self._door_unlocked_known = False
        # Replan from the new reality.
        self._plan.clear()

    def snapshot(self) -> JsonValue:
        return {
            "known_map": self._grid_map is not None,
            "remaining_plan_len": len(self._plan),
            "door": {
                "belief_p_locked": round(self._door_belief.p_locked, 4),
                "unlocked_known": self._door_unlocked_known,
                "has_recent_scan": self._has_recent_scan,
            },
        }

    def _handle_door_before_move(self) -> Action:
        if not self._has_recent_scan:
            return CallToolAction(request=ScanDoorRequest())

        p_locked = self._door_belief.p_locked
        if p_locked >= self.unlock_threshold:
            return CallToolAction(request=DoorUnlockRequest())
        if p_locked <= self.proceed_threshold:
            # Likely unlocked; proceed without spending a confirm tool call.
            return self._pop_next_move()
        # Uncertain: ask for clarification (perfect but costs a tool call).
        return CallToolAction(request=ConfirmDoorRequest())

    def _pop_next_move(self) -> Action:
        if not self._plan:
            return StopAction(reason="no_plan")
        d = self._plan.pop(0)
        self._last_move_target_is_door = False
        return MoveAction(direction=d)

    def _compute_plan(self, *, start: Position, goal: Position) -> None:
        if self._grid_map is None:
            self._plan.clear()
            return
        result: PlannerResult = astar_plan(
            self._grid_map,
            start=start,
            goal=goal,
            door_unlocked=True,
            budget=self.planner_budget,
        )
        self._plan = list(result.plan.moves)

    def _is_next_step_into_door(self, *, current: Position, direction: Direction) -> bool:
        if self._grid_map is None or self._grid_map.door is None:
            return False
        return current.moved(direction) == self._grid_map.door
