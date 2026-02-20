from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from learning_compiler.tools.contracts import ToolName
from learning_compiler.tools.faults import FaultPlan
from learning_compiler.tools.wrappers import ToolAllowlist, ToolCallBudget


class CourseStage(str, Enum):
    LAB1 = "lab1"
    LAB2 = "lab2"
    LAB3 = "lab3"
    LAB4 = "lab4"
    LAB5 = "lab5"
    LAB6 = "lab6"


@dataclass(frozen=True, slots=True)
class RunBudgets:
    max_steps: int
    max_tool_attempts: int
    planner_max_expansions: int
    max_retries_per_tool_call: int


def default_budgets(stage: CourseStage) -> RunBudgets:
    match stage:
        case CourseStage.LAB1:
            return RunBudgets(max_steps=50, max_tool_attempts=5, planner_max_expansions=0, max_retries_per_tool_call=0)
        case CourseStage.LAB2:
            return RunBudgets(max_steps=100, max_tool_attempts=5, planner_max_expansions=10_000, max_retries_per_tool_call=0)
        case CourseStage.LAB3:
            return RunBudgets(max_steps=120, max_tool_attempts=15, planner_max_expansions=10_000, max_retries_per_tool_call=0)
        case CourseStage.LAB4:
            return RunBudgets(max_steps=120, max_tool_attempts=5, planner_max_expansions=0, max_retries_per_tool_call=0)
        case CourseStage.LAB5:
            return RunBudgets(max_steps=200, max_tool_attempts=40, planner_max_expansions=10_000, max_retries_per_tool_call=2)
        case CourseStage.LAB6:
            return RunBudgets(max_steps=200, max_tool_attempts=40, planner_max_expansions=10_000, max_retries_per_tool_call=2)


def default_tool_allowlist(stage: CourseStage) -> ToolAllowlist:
    match stage:
        case CourseStage.LAB1:
            allowed = {ToolName.LOOKUP_MAP}
        case CourseStage.LAB2:
            allowed = {ToolName.LOOKUP_MAP}
        case CourseStage.LAB3:
            allowed = {ToolName.LOOKUP_MAP, ToolName.SCAN_DOOR, ToolName.CONFIRM_DOOR, ToolName.DOOR_UNLOCK}
        case CourseStage.LAB4:
            allowed = {ToolName.LOOKUP_MAP}
        case CourseStage.LAB5 | CourseStage.LAB6:
            allowed = {
                ToolName.LOOKUP_MAP,
                ToolName.CONFIRM_DOOR,
                ToolName.DOOR_UNLOCK,
                ToolName.REPORT_DELIVERY,
            }
    return ToolAllowlist(allowed=frozenset(allowed))


def default_fault_plan(stage: CourseStage, *, seed: int) -> FaultPlan:
    if stage in (CourseStage.LAB5, CourseStage.LAB6):
        return FaultPlan(seed=seed, fault_rate=0.15)
    return FaultPlan(seed=seed, fault_rate=0.0)


def tool_call_budget(budgets: RunBudgets) -> ToolCallBudget:
    return ToolCallBudget(max_retries_per_call=budgets.max_retries_per_tool_call)
