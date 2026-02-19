"""Grid maps for CourierBot.

Maps are represented as ASCII, because it is easy to teach and easy to diff in run journals.

Legend:
- `#` wall (impassable)
- `.` free space
- `S` start
- `G` goal/destination
- `D` door tile (passable only if door is unlocked)
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum

from learning_compiler.core.json import JsonValue
from learning_compiler.env.types import Direction, Position, iter_neighbors


class Tile(str, Enum):
    WALL = "#"
    FREE = "."
    START = "S"
    GOAL = "G"
    DOOR = "D"


@dataclass(frozen=True, slots=True)
class GridMap:
    width: int
    height: int
    walls: frozenset[Position]
    start: Position
    goal: Position
    door: Position | None

    def in_bounds(self, pos: Position) -> bool:
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height

    def is_wall(self, pos: Position) -> bool:
        return pos in self.walls

    def is_door(self, pos: Position) -> bool:
        return self.door == pos

    def passable(self, pos: Position, *, door_unlocked: bool) -> bool:
        return (
            self.in_bounds(pos)
            and not self.is_wall(pos)
            and (door_unlocked or not self.is_door(pos))
        )

    def neighbors(self, pos: Position, *, door_unlocked: bool) -> Iterable[tuple[Direction, Position]]:
        for d, nxt in iter_neighbors(pos):
            if self.passable(nxt, door_unlocked=door_unlocked):
                yield (d, nxt)


@dataclass(frozen=True, slots=True)
class ParsedMap:
    grid_map: GridMap
    raw_lines: tuple[str, ...]


class MapParseError(ValueError):
    pass


def parse_ascii_map(text: str) -> ParsedMap:
    lines = tuple(line.rstrip("\n") for line in text.splitlines() if line.strip() != "")
    if not lines:
        raise MapParseError("empty map")

    width = len(lines[0])
    if any(len(line) != width for line in lines):
        raise MapParseError("all rows must have equal width")

    height = len(lines)
    walls: set[Position] = set()
    start: Position | None = None
    goal: Position | None = None
    door: Position | None = None

    allowed = {t.value for t in Tile}

    for y, line in enumerate(lines):
        for x, ch in enumerate(line):
            if ch not in allowed:
                raise MapParseError(f"invalid tile '{ch}' at {(x, y)}")
            pos = Position(x, y)
            if ch == Tile.WALL.value:
                walls.add(pos)
            elif ch == Tile.START.value:
                if start is not None:
                    raise MapParseError("multiple starts")
                start = pos
            elif ch == Tile.GOAL.value:
                if goal is not None:
                    raise MapParseError("multiple goals")
                goal = pos
            elif ch == Tile.DOOR.value:
                if door is not None:
                    raise MapParseError("multiple doors")
                door = pos

    if start is None or goal is None:
        raise MapParseError("map must contain exactly one S and one G")

    return ParsedMap(
        grid_map=GridMap(
            width=width,
            height=height,
            walls=frozenset(walls),
            start=start,
            goal=goal,
            door=door,
        ),
        raw_lines=lines,
    )


def render_ascii_map(
    grid_map: GridMap,
    *,
    agent: Position | None = None,
    door_unlocked: bool,
) -> str:
    # Note: this function is for *debugging and journaling*, not for parsing.
    rows: list[list[str]] = [[Tile.FREE.value for _ in range(grid_map.width)] for _ in range(grid_map.height)]
    for w in grid_map.walls:
        rows[w.y][w.x] = Tile.WALL.value
    rows[grid_map.start.y][grid_map.start.x] = Tile.START.value
    rows[grid_map.goal.y][grid_map.goal.x] = Tile.GOAL.value
    if grid_map.door is not None:
        rows[grid_map.door.y][grid_map.door.x] = Tile.DOOR.value if not door_unlocked else Tile.FREE.value
    if agent is not None:
        rows[agent.y][agent.x] = "@"  # not a real tile; for visualization only
    return "\n".join("".join(row) for row in rows)


def map_to_dict(parsed: ParsedMap) -> dict[str, JsonValue]:
    """A small structured representation for journals/tests."""

    obj: dict[str, JsonValue] = {
        "width": parsed.grid_map.width,
        "height": parsed.grid_map.height,
        "start": {"x": parsed.grid_map.start.x, "y": parsed.grid_map.start.y},
        "goal": {"x": parsed.grid_map.goal.x, "y": parsed.grid_map.goal.y},
        "door": (
            None
            if parsed.grid_map.door is None
            else {"x": parsed.grid_map.door.x, "y": parsed.grid_map.door.y}
        ),
        "raw_lines": list(parsed.raw_lines),
    }
    return obj
