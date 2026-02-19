"""Feature extraction for learning policies.

This intentionally uses simple, discrete features:
- relative position to goal (dx, dy)
- whether each neighbor direction is blocked

The goal is to keep math light and make the representation inspectable.
"""
from __future__ import annotations

from dataclasses import dataclass

from learning_compiler.env.grid import GridMap
from learning_compiler.env.types import Direction, Position


@dataclass(frozen=True, slots=True)
class LocalGridFeatures:
    dx_to_goal: int
    dy_to_goal: int
    blocked_north: bool
    blocked_south: bool
    blocked_east: bool
    blocked_west: bool

    def as_vector(self) -> tuple[int, int, int, int, int, int]:
        return (
            self.dx_to_goal,
            self.dy_to_goal,
            int(self.blocked_north),
            int(self.blocked_south),
            int(self.blocked_east),
            int(self.blocked_west),
        )


def extract_local_features(
    grid_map: GridMap,
    *,
    position: Position,
    goal: Position,
    door_unlocked: bool,
) -> LocalGridFeatures:
    def blocked(direction: Direction) -> bool:
        nxt = position.moved(direction)
        return not grid_map.passable(nxt, door_unlocked=door_unlocked)

    return LocalGridFeatures(
        dx_to_goal=goal.x - position.x,
        dy_to_goal=goal.y - position.y,
        blocked_north=blocked(Direction.NORTH),
        blocked_south=blocked(Direction.SOUTH),
        blocked_east=blocked(Direction.EAST),
        blocked_west=blocked(Direction.WEST),
    )
