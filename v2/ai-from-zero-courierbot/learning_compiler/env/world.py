"""The CourierBot world simulator.

This is a tiny deterministic environment:
- movement in a grid map
- an optional door that blocks movement until unlocked
- a delivery flag once the destination is reported

The environment is intentionally simple so students can reason about it from run journals.
"""
from __future__ import annotations

from dataclasses import dataclass

from learning_compiler.env.grid import GridMap
from learning_compiler.env.types import Direction, Position


@dataclass(frozen=True, slots=True)
class WorldObservation:
    position: Position
    goal: Position
    at_goal: bool
    blocked_north: bool
    blocked_south: bool
    blocked_east: bool
    blocked_west: bool

    def blocked(self, direction: Direction) -> bool:
        match direction:
            case Direction.NORTH:
                return self.blocked_north
            case Direction.SOUTH:
                return self.blocked_south
            case Direction.EAST:
                return self.blocked_east
            case Direction.WEST:
                return self.blocked_west


@dataclass(slots=True)
class WorldState:
    grid_map: GridMap
    agent_pos: Position
    door_locked: bool
    delivered: bool

    @staticmethod
    def initial(grid_map: GridMap, *, door_locked: bool = True) -> WorldState:
        return WorldState(
            grid_map=grid_map,
            agent_pos=grid_map.start,
            door_locked=door_locked if grid_map.door is not None else False,
            delivered=False,
        )

    def observe(self) -> WorldObservation:
        pos = self.agent_pos

        def blocked(direction: Direction) -> bool:
            nxt = pos.moved(direction)
            return not self.grid_map.passable(nxt, door_unlocked=not self.door_locked)

        return WorldObservation(
            position=pos,
            goal=self.grid_map.goal,
            at_goal=(pos == self.grid_map.goal),
            blocked_north=blocked(Direction.NORTH),
            blocked_south=blocked(Direction.SOUTH),
            blocked_east=blocked(Direction.EAST),
            blocked_west=blocked(Direction.WEST),
        )

    def apply_move(self, direction: Direction) -> bool:
        """Attempts to move. Returns True if the move succeeded."""

        nxt = self.agent_pos.moved(direction)
        if not self.grid_map.passable(nxt, door_unlocked=not self.door_locked):
            return False
        self.agent_pos = nxt
        return True

    def apply_unlock(self) -> None:
        if self.grid_map.door is None:
            return
        self.door_locked = False

    def apply_report_delivery(self) -> None:
        self.delivered = True
