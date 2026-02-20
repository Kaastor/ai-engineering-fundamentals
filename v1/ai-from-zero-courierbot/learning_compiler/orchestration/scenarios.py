"""Small built-in scenarios (ASCII maps) for the lab scripts.

Import-time rule: avoid running logic with failure modes at import. We keep map strings as data and parse on demand.
"""
from __future__ import annotations

from dataclasses import dataclass

from learning_compiler.env.grid import ParsedMap, parse_ascii_map


@dataclass(frozen=True, slots=True)
class ScenarioSpec:
    name: str
    map_text: str

    def parse(self) -> ParsedMap:
        return parse_ascii_map(self.map_text)


LAB1_TINY = ScenarioSpec(
    name="lab1_tiny",
    map_text=(
        """######
#S...#
#....#
#....#
#...G#
######
"""
    ),
)

LAB2_OBSTACLES = ScenarioSpec(
    name="lab2_obstacles",
    map_text=(
        """########
#S..#..#
#..##..#
#..#...#
#..###.#
#....G.#
########
"""
    ),
)

LAB3_DOOR = ScenarioSpec(
    name="lab3_door",
    map_text=(
        """########
#S.....#
#..###.#
#..D#..#
#..###.#
#.....G#
########
"""
    ),
)

LAB5_FAILURES = ScenarioSpec(
    name="lab5_failures",
    map_text=(
        """##########
#S..#....#
#..##.##.#
#..D..#..#
#.#######.
#......#.#
#.######.#
#......#.#
#....#..G#
##########
"""
    ),
)
