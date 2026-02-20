from __future__ import annotations

from learning_compiler.env.grid import parse_ascii_map
from learning_compiler.planning.search import PlannerBudget, astar_plan, bfs_plan


def test_bfs_and_astar_find_paths() -> None:
    parsed = parse_ascii_map(
        """########
#S..#..#
#..##..#
#..#...#
#..###.#
#....G.#
########
"""
    )
    grid = parsed.grid_map
    budget = PlannerBudget(max_expansions=10_000)

    bfs = bfs_plan(grid, start=grid.start, goal=grid.goal, door_unlocked=True, budget=budget).plan
    ast = astar_plan(grid, start=grid.start, goal=grid.goal, door_unlocked=True, budget=budget).plan

    assert len(bfs) == len(ast)
    assert len(ast) > 0
