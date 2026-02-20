from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from learning_compiler.agent.actions import Action, CallToolAction, MoveAction, StopAction
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
    ReportDeliveryRequest,
    ReportDeliveryResponse,
)
from learning_compiler.tools.wrappers import ToolCallResult


class WorkflowPhase(str, Enum):
    INIT = "init"
    NAVIGATE = "navigate"
    UNLOCK = "unlock"
    VERIFY = "verify"
    REPORT = "report"
    DONE = "done"
    FAIL = "fail"


@dataclass(slots=True)
class CourierWorkflowAgent(CourierAgent):
    """Meeting 5+ agent: explicit workflow state machine.

    This agent is intentionally conservative:
- it always obtains a map,
- it navigates via A*,
- if it encounters a door, it unlocks it (idempotently) and verifies via confirm,
- once at goal, it reports delivery (idempotently) and stops.

    The interesting engineering work is in the *system* around it: budgets, retries, validation, and journals.
    """

    planner_budget: PlannerBudget
    phase: WorkflowPhase = WorkflowPhase.INIT

    _grid_map: GridMap | None = None
    _plan: list[Direction] = field(default_factory=list)
    _last_plan_stats: dict[str, JsonValue] | None = None

    def decide(self, obs: WorldObservation) -> Action:
        match self.phase:
            case WorkflowPhase.INIT:
                return CallToolAction(request=LookupMapRequest())

            case WorkflowPhase.NAVIGATE:
                if obs.at_goal:
                    self.phase = WorkflowPhase.REPORT
                    return CallToolAction(request=ReportDeliveryRequest())
                if self._grid_map is None:
                    self.phase = WorkflowPhase.INIT
                    return CallToolAction(request=LookupMapRequest())
                if not self._plan:
                    self._compute_plan(start=obs.position, goal=obs.goal)
                if not self._plan:
                    self.phase = WorkflowPhase.FAIL
                    return StopAction(reason="no_plan")
                next_dir = self._plan[0]
                if self._is_next_step_into_door(current=obs.position, direction=next_dir) and obs.blocked(next_dir):
                    # Door blocks movement: unlock it.
                    self.phase = WorkflowPhase.UNLOCK
                    return CallToolAction(request=DoorUnlockRequest())
                # Otherwise follow the plan.
                self._plan.pop(0)
                return MoveAction(direction=next_dir)

            case WorkflowPhase.UNLOCK:
                # After unlock tool, we verify.
                self.phase = WorkflowPhase.VERIFY
                return CallToolAction(request=ConfirmDoorRequest())

            case WorkflowPhase.VERIFY:
                # We wait for ConfirmDoorResponse; decide() should not be called in a tight loop without it.
                # If it is, we conservatively ask again.
                return CallToolAction(request=ConfirmDoorRequest())

            case WorkflowPhase.REPORT:
                # Wait for report response; if decide() is called again, request again (idempotent).
                return CallToolAction(request=ReportDeliveryRequest())

            case WorkflowPhase.DONE:
                return StopAction(reason="done")

            case WorkflowPhase.FAIL:
                return StopAction(reason="failed")

        return StopAction(reason="invalid_phase")

    def observe_tool_result(self, result: ToolCallResult) -> None:
        parsed = result.parsed

        if isinstance(parsed, LookupMapResponse):
            self._grid_map = parse_ascii_map(parsed.map_text).grid_map
            self._plan.clear()
            # Start navigating once we have the map.
            if self.phase == WorkflowPhase.INIT:
                self.phase = WorkflowPhase.NAVIGATE
            return

        if isinstance(parsed, DoorUnlockResponse):
            # Next decide() will issue a confirm.
            return

        if isinstance(parsed, ConfirmDoorResponse):
            if parsed.is_locked:
                self.phase = WorkflowPhase.FAIL
                return
            # Door is unlocked; resume navigation.
            self.phase = WorkflowPhase.NAVIGATE
            self._plan.clear()
            return

        if isinstance(parsed, ReportDeliveryResponse):
            if parsed.accepted:
                self.phase = WorkflowPhase.DONE
            else:
                self.phase = WorkflowPhase.FAIL
            return

    def observe_move_result(self, *, direction: Direction, succeeded: bool) -> None:
        _ = direction
        if not succeeded:
            # Any unexpected movement failure triggers replanning.
            self._plan.clear()

    def snapshot(self) -> JsonValue:
        return {
            "phase": self.phase.value,
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
            door_unlocked=True,
            budget=self.planner_budget,
        )
        self._plan = list(result.plan.moves)
        self._last_plan_stats = {
            "expansions": result.stats.expansions,
            "max_frontier": result.stats.max_frontier,
        }

    def _is_next_step_into_door(self, *, current: Position, direction: Direction) -> bool:
        if self._grid_map is None or self._grid_map.door is None:
            return False
        return current.moved(direction) == self._grid_map.door
