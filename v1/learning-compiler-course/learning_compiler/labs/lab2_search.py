from __future__ import annotations

from dataclasses import dataclass

from learning_compiler.planning.gridworld import GridPos, GridWorld, Move, manhattan, render_ascii
from learning_compiler.planning.search import SearchResult, a_star_search, breadth_first_search, uniform_cost_search


@dataclass(frozen=True, slots=True)
class SearchDemoResult:
    bfs: SearchResult[Move]
    ucs: SearchResult[Move]
    astar: SearchResult[Move]
    world: GridWorld
    path: tuple[GridPos, ...]


def run(*, seed: int) -> tuple[str, SearchDemoResult]:
    # Seed is unused here, but included for interface consistency and future extensions.
    _ = seed

    world = GridWorld(
        width=7,
        height=5,
        walls=frozenset(
            {
                GridPos(3, 0),
                GridPos(3, 1),
                GridPos(3, 2),
                GridPos(1, 3),
                GridPos(2, 3),
            }
        ),
        start=GridPos(0, 0),
        goal=GridPos(6, 4),
    )

    problem = world.as_problem()

    bfs = breadth_first_search(problem)
    ucs = uniform_cost_search(problem)
    astar = a_star_search(problem, heuristic=lambda s: float(manhattan(s, world.goal)))

    path = _positions_from_plan(world=world, plan=astar.plan)

    lines: list[str] = []
    lines.append("# Lab 2 — Search & Planning")
    lines.append("")
    lines.append("GridWorld:")
    lines.append("```")
    lines.append(render_ascii(world))
    lines.append("```")
    lines.append("")
    lines.append(_format("BFS", bfs))
    lines.append(_format("UCS", ucs))
    lines.append(_format("A*", astar))
    lines.append("")
    lines.append("A* path overlay:")
    lines.append("```")
    lines.append(render_ascii(world, path=path))
    lines.append("```")

    return (
        "\n".join(lines),
        SearchDemoResult(bfs=bfs, ucs=ucs, astar=astar, world=world, path=path),
    )


def _format(name: str, r: SearchResult[Move]) -> str:
    plan_str = ", ".join(a.value for a in r.plan) if r.plan else "(empty)"
    return (
        f"## {name}\n"
        f"- found: {r.found}\n"
        f"- cost: {r.cost:.1f}\n"
        f"- steps: {len(r.plan)}\n"
        f"- expanded nodes: {r.expanded}\n"
        f"- max frontier: {r.frontier_max}\n"
        f"- plan: {plan_str}\n"
    )


def _positions_from_plan(*, world: GridWorld, plan: tuple[Move, ...]) -> tuple[GridPos, ...]:
    pos = world.start
    out = [pos]
    for move in plan:
        pos = world.as_problem().result(pos, move)
        out.append(pos)
    return tuple(out)
