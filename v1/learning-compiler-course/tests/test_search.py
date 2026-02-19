from __future__ import annotations

from learning_compiler.planning.gridworld import GridPos, GridWorld, manhattan
from learning_compiler.planning.search import a_star_search, uniform_cost_search


def test_astar_matches_ucs_cost() -> None:
    world = GridWorld(
        width=6,
        height=4,
        walls=frozenset({GridPos(2, 0), GridPos(2, 1), GridPos(2, 2)}),
        start=GridPos(0, 0),
        goal=GridPos(5, 3),
    )
    problem = world.as_problem()

    ucs = uniform_cost_search(problem)
    astar = a_star_search(problem, heuristic=lambda s: float(manhattan(s, world.goal)))

    assert ucs.found and astar.found
    assert abs(ucs.cost - astar.cost) < 1e-9
