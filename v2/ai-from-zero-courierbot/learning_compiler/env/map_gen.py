"""Seeded random map generation for evaluation and learning.

The generator is intentionally simple:
- fixed width/height
- randomly placed walls with a target density
- optional door on the shortest path (to force tool usage)

Because this is a teaching repository, we optimize for:
1) deterministic generation given a seed,
2) maps that are usually solvable,
3) small, inspectable sizes.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from learning_compiler.core.hashing import stable_hash_int
from learning_compiler.env.grid import GridMap
from learning_compiler.env.types import Position


@dataclass(frozen=True, slots=True)
class MapGenConfig:
    width: int = 10
    height: int = 10
    wall_density: float = 0.18
    place_door: bool = True


class MapGenError(RuntimeError):
    pass


def _seeded_rng(seed: int, tag: str) -> random.Random:
    return random.Random(stable_hash_int([str(seed), tag], bits=32))


def generate_map(seed: int, cfg: MapGenConfig) -> GridMap:
    rng = _seeded_rng(seed, f"map:{cfg.width}x{cfg.height}:{cfg.wall_density}:{cfg.place_door}")

    if cfg.width < 4 or cfg.height < 4:
        raise MapGenError("map must be at least 4x4")

    start = Position(1, 1)
    goal = Position(cfg.width - 2, cfg.height - 2)

    attempts = 0
    while attempts < 200:
        attempts += 1
        walls: set[Position] = set()
        for y in range(cfg.height):
            for x in range(cfg.width):
                pos = Position(x, y)
                if x == 0 or y == 0 or x == cfg.width - 1 or y == cfg.height - 1:
                    walls.add(pos)
                    continue
                if pos in (start, goal):
                    continue
                if rng.random() < cfg.wall_density:
                    walls.add(pos)

        base = GridMap(
            width=cfg.width,
            height=cfg.height,
            walls=frozenset(walls),
            start=start,
            goal=goal,
            door=None,
        )

        # Quick solvability check by BFS in an unlocked world.
        if _is_solvable(base):
            door = _place_door_on_manhattan_line(base, rng) if cfg.place_door else None
            return GridMap(
                width=base.width,
                height=base.height,
                walls=base.walls,
                start=base.start,
                goal=base.goal,
                door=door,
            )

    raise MapGenError("failed to generate a solvable map after many attempts")


def _is_solvable(grid_map: GridMap) -> bool:
    frontier: list[Position] = [grid_map.start]
    seen: set[Position] = {grid_map.start}
    while frontier:
        cur = frontier.pop(0)
        if cur == grid_map.goal:
            return True
        for _, nxt in grid_map.neighbors(cur, door_unlocked=True):
            if nxt in seen:
                continue
            seen.add(nxt)
            frontier.append(nxt)
    return False


def _place_door_on_manhattan_line(grid_map: GridMap, rng: random.Random) -> Position | None:
    """Places a door on a naive Manhattan route between start and goal, when possible.

    This is *not* guaranteed to be on the true shortest path, but it's deterministic and simple.
    """

    start, goal = grid_map.start, grid_map.goal
    # Candidate positions along a simple L-shaped path: move horizontally then vertically.
    candidates: list[Position] = []
    x_step = 1 if goal.x >= start.x else -1
    for x in range(start.x, goal.x + x_step, x_step):
        candidates.append(Position(x, start.y))
    y_step = 1 if goal.y >= start.y else -1
    for y in range(start.y, goal.y + y_step, y_step):
        candidates.append(Position(goal.x, y))
    candidates = [p for p in candidates if p not in (start, goal) and p not in grid_map.walls]

    if not candidates:
        return None

    # Pick a candidate near the middle so it usually matters.
    middle = len(candidates) // 2
    window = candidates[max(0, middle - 2) : min(len(candidates), middle + 3)]
    return rng.choice(window)
