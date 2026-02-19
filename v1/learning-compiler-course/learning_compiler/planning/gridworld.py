from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Sequence

from learning_compiler.planning.search import SearchProblem


class Move(str, Enum):
    UP = "up"
    RIGHT = "right"
    DOWN = "down"
    LEFT = "left"


@dataclass(frozen=True, slots=True)
class GridPos:
    x: int
    y: int


@dataclass(frozen=True, slots=True)
class GridWorld:
    width: int
    height: int
    walls: frozenset[GridPos]
    start: GridPos
    goal: GridPos

    def as_problem(self) -> SearchProblem[GridPos, Move]:
        return _GridWorldProblem(self)

    def in_bounds(self, pos: GridPos) -> bool:
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height

    def is_wall(self, pos: GridPos) -> bool:
        return pos in self.walls


class _GridWorldProblem(SearchProblem[GridPos, Move]):
    def __init__(self, world: GridWorld) -> None:
        self._world = world

    def initial_state(self) -> GridPos:
        return self._world.start

    def is_goal(self, state: GridPos) -> bool:
        return state == self._world.goal

    def actions(self, state: GridPos) -> Sequence[Move]:
        candidates: list[tuple[Move, GridPos]] = []
        for move in _ACTION_ORDER:
            nxt = _apply(move, state)
            if not self._world.in_bounds(nxt):
                continue
            if self._world.is_wall(nxt):
                continue
            candidates.append((move, nxt))
        # Return only moves; the corresponding next state is computed in result().
        return [m for m, _ in candidates]

    def result(self, state: GridPos, action: Move) -> GridPos:
        return _apply(action, state)

    def step_cost(self, state: GridPos, action: Move, next_state: GridPos) -> float:
        return 1.0


_ACTION_ORDER: tuple[Move, ...] = (Move.UP, Move.RIGHT, Move.DOWN, Move.LEFT)


def _apply(move: Move, pos: GridPos) -> GridPos:
    match move:
        case Move.UP:
            return GridPos(pos.x, pos.y - 1)
        case Move.RIGHT:
            return GridPos(pos.x + 1, pos.y)
        case Move.DOWN:
            return GridPos(pos.x, pos.y + 1)
        case Move.LEFT:
            return GridPos(pos.x - 1, pos.y)


def manhattan(a: GridPos, b: GridPos) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def render_ascii(world: GridWorld, *, path: Iterable[GridPos] = ()) -> str:
    """Render a small ASCII grid with optional path overlay."""

    path_set = set(path)
    lines: list[str] = []
    for y in range(world.height):
        row: list[str] = []
        for x in range(world.width):
            p = GridPos(x, y)
            if p == world.start:
                row.append("S")
            elif p == world.goal:
                row.append("G")
            elif p in world.walls:
                row.append("#")
            elif p in path_set:
                row.append("*")
            else:
                row.append(".")
        lines.append("".join(row))
    return "\n".join(lines)
