from __future__ import annotations

from learning_compiler.env.grid import parse_ascii_map, render_ascii_map
from learning_compiler.env.world import WorldState


def test_parse_and_render_roundtrip_no_door() -> None:
    text = """######
#S...#
#....#
#....#
#...G#
######
"""
    parsed = parse_ascii_map(text)
    world = WorldState.initial(parsed.grid_map, door_locked=False)
    rendered = render_ascii_map(parsed.grid_map, agent=world.agent_pos, door_unlocked=True)
    assert "@" in rendered
