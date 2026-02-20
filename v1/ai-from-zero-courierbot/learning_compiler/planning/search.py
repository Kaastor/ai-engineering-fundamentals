"""Graph search planners (BFS and A*).

These planners operate over `GridMap` from `learning_compiler.env.grid`.
They return *plans* (a sequence of `Direction` moves) plus small statistics that are useful for journals.

We keep the implementations intentionally explicit (no clever metaprogramming) because this is a teaching codebase.
"""
from __future__ import annotations

import heapq
from collections import deque
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from learning_compiler.core.errors import BudgetExceededError
from learning_compiler.env.grid import GridMap
from learning_compiler.env.types import Direction, Position, manhattan


@dataclass(frozen=True, slots=True)
class Plan:
    moves: tuple[Direction, ...]

    def __len__(self) -> int:
        return len(self.moves)


@dataclass(frozen=True, slots=True)
class PlannerStats:
    expansions: int
    max_frontier: int


@dataclass(frozen=True, slots=True)
class PlannerResult:
    plan: Plan
    stats: PlannerStats


Heuristic = Callable[[Position, Position], int]


@dataclass(frozen=True, slots=True)
class PlannerBudget:
    max_expansions: int


class NoPathError(RuntimeError):
    pass


def bfs_plan(
    grid_map: GridMap,
    *,
    start: Position,
    goal: Position,
    door_unlocked: bool,
    budget: PlannerBudget,
) -> PlannerResult:
    frontier: deque[Position] = deque([start])
    came_from: dict[Position, tuple[Position, Direction] | None] = {start: None}
    expansions = 0
    max_frontier = 1

    while frontier:
        if expansions >= budget.max_expansions:
            raise BudgetExceededError("BFS expansion budget exceeded")

        current = frontier.popleft()
        expansions += 1
        if current == goal:
            return PlannerResult(plan=_reconstruct_plan(came_from, goal), stats=PlannerStats(expansions, max_frontier))

        for direction, nxt in grid_map.neighbors(current, door_unlocked=door_unlocked):
            if nxt in came_from:
                continue
            came_from[nxt] = (current, direction)
            frontier.append(nxt)
        max_frontier = max(max_frontier, len(frontier))

    raise NoPathError("no path found (BFS)")


def astar_plan(
    grid_map: GridMap,
    *,
    start: Position,
    goal: Position,
    door_unlocked: bool,
    budget: PlannerBudget,
    heuristic: Heuristic = manhattan,
) -> PlannerResult:
    # Priority queue entries: (f_score, tie_break, position)
    frontier: list[tuple[int, int, Position]] = []
    heapq.heappush(frontier, (0, 0, start))

    came_from: dict[Position, tuple[Position, Direction] | None] = {start: None}
    g_score: dict[Position, int] = {start: 0}

    expansions = 0
    max_frontier = 1
    tie = 0

    while frontier:
        if expansions >= budget.max_expansions:
            raise BudgetExceededError("A* expansion budget exceeded")

        _, _, current = heapq.heappop(frontier)
        expansions += 1

        if current == goal:
            return PlannerResult(plan=_reconstruct_plan(came_from, goal), stats=PlannerStats(expansions, max_frontier))

        for direction, nxt in grid_map.neighbors(current, door_unlocked=door_unlocked):
            tentative_g = g_score[current] + 1
            known_g = g_score.get(nxt)
            if known_g is not None and tentative_g >= known_g:
                continue

            came_from[nxt] = (current, direction)
            g_score[nxt] = tentative_g

            f = tentative_g + heuristic(nxt, goal)
            tie += 1
            heapq.heappush(frontier, (f, tie, nxt))

        max_frontier = max(max_frontier, len(frontier))

    raise NoPathError("no path found (A*)")


def _reconstruct_plan(
    came_from: Mapping[Position, tuple[Position, Direction] | None],
    goal: Position,
) -> Plan:
    moves: list[Direction] = []
    current = goal
    while True:
        prev = came_from.get(current)
        if prev is None:
            break
        prev_pos, direction = prev
        moves.append(direction)
        current = prev_pos
    moves.reverse()
    return Plan(tuple(moves))
