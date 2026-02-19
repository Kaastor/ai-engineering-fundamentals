from __future__ import annotations

import heapq
from collections import deque
from dataclasses import dataclass
from typing import Callable, Generic, Hashable, Protocol, Sequence, TypeVar


StateT = TypeVar("StateT", bound=Hashable)
ActionT = TypeVar("ActionT")


class SearchProblem(Protocol[StateT, ActionT]):
    """A classical search problem definition (Russell/Norvig-style)."""

    def initial_state(self) -> StateT: ...
    def is_goal(self, state: StateT) -> bool: ...
    def actions(self, state: StateT) -> Sequence[ActionT]: ...
    def result(self, state: StateT, action: ActionT) -> StateT: ...
    def step_cost(self, state: StateT, action: ActionT, next_state: StateT) -> float: ...


Heuristic = Callable[[StateT], float]


@dataclass(frozen=True, slots=True)
class SearchResult(Generic[ActionT]):
    found: bool
    plan: tuple[ActionT, ...]
    cost: float
    expanded: int
    frontier_max: int


@dataclass(frozen=True, slots=True)
class _Node(Generic[StateT, ActionT]):
    state: StateT
    parent: _Node[StateT, ActionT] | None
    action: ActionT | None
    cost: float
    depth: int


def breadth_first_search(problem: SearchProblem[StateT, ActionT]) -> SearchResult[ActionT]:
    start = problem.initial_state()
    if problem.is_goal(start):
        return SearchResult(found=True, plan=(), cost=0.0, expanded=0, frontier_max=1)

    frontier: deque[_Node[StateT, ActionT]] = deque()
    frontier.append(_Node(state=start, parent=None, action=None, cost=0.0, depth=0))
    visited: set[StateT] = {start}

    expanded = 0
    frontier_max = 1

    while frontier:
        frontier_max = max(frontier_max, len(frontier))
        node = frontier.popleft()
        expanded += 1

        for action in problem.actions(node.state):
            nxt = problem.result(node.state, action)
            if nxt in visited:
                continue
            visited.add(nxt)
            child = _Node(
                state=nxt,
                parent=node,
                action=action,
                cost=node.cost + problem.step_cost(node.state, action, nxt),
                depth=node.depth + 1,
            )
            if problem.is_goal(nxt):
                plan = _reconstruct_plan(child)
                return SearchResult(
                    found=True, plan=tuple(plan), cost=child.cost, expanded=expanded, frontier_max=frontier_max
                )
            frontier.append(child)

    return SearchResult(found=False, plan=(), cost=float("inf"), expanded=expanded, frontier_max=frontier_max)


def depth_first_search(problem: SearchProblem[StateT, ActionT], *, depth_limit: int | None = None) -> SearchResult[ActionT]:
    start = problem.initial_state()
    frontier: list[_Node[StateT, ActionT]] = [_Node(state=start, parent=None, action=None, cost=0.0, depth=0)]
    visited: set[StateT] = set()

    expanded = 0
    frontier_max = 1

    while frontier:
        frontier_max = max(frontier_max, len(frontier))
        node = frontier.pop()

        if node.state in visited:
            continue
        visited.add(node.state)

        if problem.is_goal(node.state):
            plan = _reconstruct_plan(node)
            return SearchResult(
                found=True, plan=tuple(plan), cost=node.cost, expanded=expanded, frontier_max=frontier_max
            )

        if depth_limit is not None and node.depth >= depth_limit:
            continue

        expanded += 1

        actions = list(problem.actions(node.state))
        # Deterministic: push reversed so the first action is explored first.
        for action in reversed(actions):
            nxt = problem.result(node.state, action)
            child = _Node(
                state=nxt,
                parent=node,
                action=action,
                cost=node.cost + problem.step_cost(node.state, action, nxt),
                depth=node.depth + 1,
            )
            frontier.append(child)

    return SearchResult(found=False, plan=(), cost=float("inf"), expanded=expanded, frontier_max=frontier_max)


def uniform_cost_search(problem: SearchProblem[StateT, ActionT]) -> SearchResult[ActionT]:
    return _best_first_search(problem, heuristic=lambda _s: 0.0)


def a_star_search(problem: SearchProblem[StateT, ActionT], *, heuristic: Heuristic[StateT]) -> SearchResult[ActionT]:
    return _best_first_search(problem, heuristic=heuristic)


def _best_first_search(problem: SearchProblem[StateT, ActionT], *, heuristic: Heuristic[StateT]) -> SearchResult[ActionT]:
    start = problem.initial_state()
    start_node = _Node(state=start, parent=None, action=None, cost=0.0, depth=0)

    counter = 0
    frontier: list[tuple[float, int, _Node[StateT, ActionT]]] = []
    heapq.heappush(frontier, (heuristic(start), counter, start_node))
    best_cost: dict[StateT, float] = {start: 0.0}

    expanded = 0
    frontier_max = 1

    while frontier:
        frontier_max = max(frontier_max, len(frontier))
        _priority, _tiebreak, node = heapq.heappop(frontier)

        if problem.is_goal(node.state):
            plan = _reconstruct_plan(node)
            return SearchResult(
                found=True, plan=tuple(plan), cost=node.cost, expanded=expanded, frontier_max=frontier_max
            )

        expanded += 1

        for action in problem.actions(node.state):
            nxt = problem.result(node.state, action)
            step = problem.step_cost(node.state, action, nxt)
            new_cost = node.cost + step

            prev = best_cost.get(nxt)
            if prev is not None and new_cost >= prev:
                continue

            best_cost[nxt] = new_cost
            counter += 1
            priority = new_cost + heuristic(nxt)
            child = _Node(
                state=nxt,
                parent=node,
                action=action,
                cost=new_cost,
                depth=node.depth + 1,
            )
            heapq.heappush(frontier, (priority, counter, child))

    return SearchResult(found=False, plan=(), cost=float("inf"), expanded=expanded, frontier_max=frontier_max)


def _reconstruct_plan(node: _Node[StateT, ActionT]) -> list[ActionT]:
    actions: list[ActionT] = []
    current: _Node[StateT, ActionT] | None = node
    while current is not None and current.action is not None:
        actions.append(current.action)
        current = current.parent
    actions.reverse()
    return actions
