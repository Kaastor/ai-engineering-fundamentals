from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from learning_compiler.agent.actions import CallToolAction, MoveAction, StopAction
from learning_compiler.agent.interface import CourierAgent
from learning_compiler.agent.lab1 import Lab1HardcodedAgent
from learning_compiler.agent.lab2 import Lab2PlanningAgent
from learning_compiler.agent.lab3 import Lab3UncertaintyAgent
from learning_compiler.agent.lab4 import Lab4LearnedAgent
from learning_compiler.agent.serialization import (
    action_to_json,
    tool_call_result_to_json,
    world_observation_to_json,
)
from learning_compiler.agent.workflow import CourierWorkflowAgent
from learning_compiler.core.errors import ToolError
from learning_compiler.core.hashing import StableIdFactory, stable_hash_hex
from learning_compiler.core.json import JsonValue
from learning_compiler.env.grid import ParsedMap, map_to_dict
from learning_compiler.env.world import WorldState
from learning_compiler.journal.models import EventType
from learning_compiler.journal.writer import JsonlJournalWriter
from learning_compiler.learning.knn import KnnModel
from learning_compiler.orchestration.stages import CourseStage, RunBudgets
from learning_compiler.planning.search import PlannerBudget
from learning_compiler.tools.contracts import (
    ConfirmDoorResponse,
    DoorUnlockResponse,
    ReportDeliveryResponse,
    ToolName,
)
from learning_compiler.tools.faults import FaultPlan
from learning_compiler.tools.simulator import ToolExecutionContext, ToolSimulator
from learning_compiler.tools.wrappers import (
    ReliableToolCaller,
    ToolAllowlist,
    ToolCallBudget,
    ToolCallResult,
)


@dataclass(frozen=True, slots=True)
class RunSummary:
    run_id: str
    stage: str
    scenario: str
    seed: int
    success: bool
    steps: int
    tool_attempts: int
    delivered: bool
    reason: str


def run_scenario(
    *,
    stage: CourseStage,
    seed: int,
    scenario_name: str,
    parsed_map: ParsedMap,
    budgets: RunBudgets,
    allowlist: ToolAllowlist,
    fault_plan: FaultPlan,
    tool_budget: ToolCallBudget,
    out_dir: Path,
    knn_model: KnnModel | None = None,
) -> RunSummary:
    run_id = _make_run_id(stage=stage, seed=seed, scenario=scenario_name)
    run_dir = out_dir / run_id
    journal_path = run_dir / "journal.jsonl"

    world = WorldState.initial(parsed_map.grid_map, door_locked=True)
    tool_ctx = ToolExecutionContext(run_id=run_id)
    tool_sim = ToolSimulator(fault_plan=fault_plan)
    tool_caller = ReliableToolCaller(simulator=tool_sim, allowlist=allowlist, budget=tool_budget)

    agent = _build_agent(stage=stage, budgets=budgets, knn_model=knn_model)

    id_factory = StableIdFactory(run_id=run_id)
    steps = 0
    reason = ""
    success = False

    with JsonlJournalWriter(journal_path, id_factory=id_factory) as jw:
        jw.write(
            EventType.RUN_START,
            {
                "run_id": run_id,
                "stage": stage.value,
                "seed": seed,
                "scenario": scenario_name,
                "budgets": {
                    "max_steps": budgets.max_steps,
                    "max_tool_attempts": budgets.max_tool_attempts,
                    "planner_max_expansions": budgets.planner_max_expansions,
                    "max_retries_per_tool_call": budgets.max_retries_per_tool_call,
                },
                "tools_allowed": [t.value for t in sorted(allowlist.allowed, key=lambda x: x.value)],
                "map": map_to_dict(parsed_map),
            },
        )

        while True:
            if steps >= budgets.max_steps:
                reason = "budget:max_steps"
                jw.write(EventType.VIOLATION, {"code": reason, "message": "step budget exceeded"})
                break
            if tool_ctx.tool_calls > budgets.max_tool_attempts:
                reason = "budget:max_tool_attempts"
                jw.write(EventType.VIOLATION, {"code": reason, "message": "tool attempt budget exceeded"})
                break

            obs = world.observe()
            action = agent.decide(obs)

            step_payload: dict[str, JsonValue] = {
                "step": steps,
                "world": world_observation_to_json(obs),
                "agent": agent.snapshot(),
                "action": action_to_json(action),
                "tool_attempts_total": tool_ctx.tool_calls,
            }

            try:
                if isinstance(action, MoveAction):
                    succeeded = world.apply_move(action.direction)
                    agent.observe_move_result(direction=action.direction, succeeded=succeeded)
                    step_payload["outcome"] = {"move_succeeded": succeeded}
                    step_payload["verify"] = {"ok": succeeded, "kind": "move"}

                elif isinstance(action, CallToolAction):
                    call_id = stable_hash_hex([run_id, "tool", str(steps), action.request.tool.value])
                    result = tool_caller.call(
                        action.request,
                        call_id=call_id,
                        grid_map=world.grid_map,
                        door_locked=world.door_locked,
                        delivered=world.delivered,
                        ctx=tool_ctx,
                    )
                    _apply_tool_effects(world, result)
                    agent.observe_tool_result(result)
                    step_payload["outcome"] = {"tool": tool_call_result_to_json(result)}
                    step_payload["verify"] = _verify_tool_effect(world, result)

                elif isinstance(action, StopAction):
                    reason = action.reason
                    step_payload["outcome"] = {"stopped": True, "reason": reason}
                    step_payload["verify"] = {"ok": True, "kind": "stop"}
                    jw.write(EventType.STEP, step_payload)
                    break
                else:
                    raise AssertionError(f"unknown action: {action}")

            except ToolError as e:
                reason = f"tool_error:{type(e).__name__}"
                jw.write(EventType.VIOLATION, {"code": reason, "message": str(e)})
                step_payload["outcome"] = {"error": str(e)}
                step_payload["verify"] = {"ok": False, "kind": "tool"}
                jw.write(EventType.STEP, step_payload)
                break

            jw.write(EventType.STEP, step_payload)
            steps += 1

            # Success conditions.
            if world.delivered:
                success = True
                reason = "delivered"
                break
            if stage in (CourseStage.LAB1, CourseStage.LAB2, CourseStage.LAB3, CourseStage.LAB4) and world.agent_pos == world.grid_map.goal:
                success = True
                reason = "reached_goal"
                break

        jw.write(
            EventType.RUN_END,
            {
                "success": success,
                "reason": reason,
                "steps": steps,
                "tool_attempts": tool_ctx.tool_calls,
                "delivered": world.delivered,
            },
        )

    return RunSummary(
        run_id=run_id,
        stage=stage.value,
        scenario=scenario_name,
        seed=seed,
        success=success,
        steps=steps,
        tool_attempts=tool_ctx.tool_calls,
        delivered=world.delivered,
        reason=reason,
    )


def _make_run_id(*, stage: CourseStage, seed: int, scenario: str) -> str:
    return stable_hash_hex([stage.value, str(seed), scenario])[:16]


def _build_agent(stage: CourseStage, *, budgets: RunBudgets, knn_model: KnnModel | None) -> CourierAgent:
    if stage == CourseStage.LAB1:
        return Lab1HardcodedAgent()
    if stage == CourseStage.LAB2:
        return Lab2PlanningAgent(planner_budget=PlannerBudget(max_expansions=budgets.planner_max_expansions))
    if stage == CourseStage.LAB3:
        return Lab3UncertaintyAgent(planner_budget=PlannerBudget(max_expansions=budgets.planner_max_expansions))
    if stage == CourseStage.LAB4:
        if knn_model is None:
            raise ValueError("LAB4 requires knn_model")
        return Lab4LearnedAgent(model=knn_model)
    if stage in (CourseStage.LAB5, CourseStage.LAB6):
        return CourierWorkflowAgent(planner_budget=PlannerBudget(max_expansions=budgets.planner_max_expansions))
    raise ValueError(f"unknown stage: {stage}")


def _apply_tool_effects(world: WorldState, result: ToolCallResult) -> None:
    tool = result.raw.tool
    parsed = result.parsed

    if tool in (ToolName.LOOKUP_MAP, ToolName.SCAN_DOOR, ToolName.CONFIRM_DOOR):
        return

    if isinstance(parsed, DoorUnlockResponse) and parsed.unlocked:
        world.apply_unlock()
        return

    if isinstance(parsed, ReportDeliveryResponse) and parsed.accepted:
        # In the spec, reporting delivery is only meaningful at the goal.
        if world.agent_pos == world.grid_map.goal:
            world.apply_report_delivery()
        return


def _verify_tool_effect(world: WorldState, result: ToolCallResult) -> dict[str, JsonValue]:
    parsed = result.parsed

    if isinstance(parsed, DoorUnlockResponse):
        ok = not world.door_locked
        return {"ok": ok, "kind": "door_unlock", "door_locked": world.door_locked}

    if isinstance(parsed, ReportDeliveryResponse):
        ok = world.delivered
        return {"ok": ok, "kind": "report_delivery", "delivered": world.delivered}

    if isinstance(parsed, ConfirmDoorResponse):
        # Verification is "we received a boolean" (validation already enforced this).
        return {"ok": True, "kind": "confirm_door", "is_locked": parsed.is_locked}

    return {"ok": True, "kind": result.raw.tool.value}
