from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, slots=True, order=True)
class Position:
    """A grid coordinate.

    Convention: (x, y) where x increases to the east and y increases to the south.
    """

    x: int
    y: int

    def moved(self, direction: Direction) -> Position:
        dx, dy = direction.delta()
        return Position(self.x + dx, self.y + dy)


class Direction(str, Enum):
    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"

    def delta(self) -> tuple[int, int]:
        match self:
            case Direction.NORTH:
                return (0, -1)
            case Direction.SOUTH:
                return (0, 1)
            case Direction.EAST:
                return (1, 0)
            case Direction.WEST:
                return (-1, 0)

    @staticmethod
    def all() -> tuple[Direction, ...]:
        return (Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST)


def manhattan(a: Position, b: Position) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def iter_neighbors(pos: Position) -> Iterable[tuple[Direction, Position]]:
    for d in Direction.all():
        yield (d, pos.moved(d))
