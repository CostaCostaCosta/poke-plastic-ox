#!/usr/bin/env python3
"""Targeted emulator checks for the 2026-11-11 review fix pass.

Covers the transitions the fix agents could not build/test themselves:
Ilex north exit, a Dark Cave mouth, Route 44 badge gate, Blackthorn and
Goldenrod Gym doors, Ecruteak's east road, Victory Road's return band, and the
Fortree Kecleon roadblock.

Run with the mGBA venv:
  LD_LIBRARY_PATH=~/.venvs/mgba311/lib:~/.venvs/mgba311/lib64 \
    ~/.venvs/mgba311/bin/python plastic_ox/demo/test_review_fixes.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_story import StoryGame  # noqa: E402
from walklib import K  # noqa: E402

GROUPS = json.loads((ROOT / "data/maps/map_groups.json").read_text())
ORDER = GROUPS["group_order"]


def map_index(name: str) -> tuple[int, int]:
    for group_id, group_name in enumerate(ORDER):
        if name in GROUPS[group_name]:
            return group_id, GROUPS[group_name].index(name)
    raise KeyError(name)


def current(game: StoryGame) -> str:
    state = game.state()
    for group_id, group_name in enumerate(ORDER):
        members = GROUPS[group_name]
        if group_id == state["group"] and state["num"] < len(members):
            return members[state["num"]]
    return f"?{state['group']},{state['num']}"


def pos(game: StoryGame) -> tuple[int, int]:
    state = game.state()
    return state["x"], state["y"]


def step(game: StoryGame, direction: str, frames: int = 26, mash: bool = True) -> None:
    game.frame(20)
    game.tap({"UP": K.KEY_UP, "DOWN": K.KEY_DOWN, "LEFT": K.KEY_LEFT, "RIGHT": K.KEY_RIGHT}[direction],
             hold=frames, wait=20)
    game.frame(60)
    if mash:
        for _ in range(3):
            game.tap(K.KEY_A, hold=3, wait=25)


def flush(game: StoryGame) -> None:
    """Finish any open message/field script before the next injected warp."""
    for _ in range(30):
        if game.u8(game.syms["sGlobalScriptContextStatus"]) == 2:
            break
        game.tap(K.KEY_A, hold=3, wait=25)
    game.frame(30)


def go(game: StoryGame, name: str, x: int, y: int) -> None:
    flush(game)
    game.warp(name, x, y)
    game.frame(160)


def expect(game: StoryGame, name: str, label: str) -> None:
    actual = current(game)
    assert actual == name, f"{label}: expected {name}, got {actual} at {pos(game)}"
    print(f"  ok  {label}: {actual} {pos(game)}")


def main() -> int:
    g = StoryGame()
    print("boot:", current(g), pos(g))

    # 1. Ilex Forest north exit (tileset attribute fix).
    g.flag("FLAG_POX_STORY_ILEX", True)
    go(g, "IlexForest_hns", 20, 16)
    step(g, "UP", 26)
    expect(g, "Route2_ViridianForest_NorthEntrance_Frlg", "Ilex north exit")

    # 2. Dark Cave south mouth -> Route 46 (tileset attribute fix).
    go(g, "DarkCave_SouthSide_hns", 56, 45)
    step(g, "DOWN", 26)
    expect(g, "Route46_hns", "Dark Cave east mouth")

    # 3. Route 44 badge gate.
    g.flag("FLAG_BADGE01_GET", False)
    go(g, "Route44_hns", 66, 13)
    step(g, "RIGHT", 16)
    assert current(g) == "Route44_hns", f"Route 44 gate let the player through without a badge: {pos(g)}"
    print("  ok  Route 44 without badge: refused at", pos(g))
    g.flag("FLAG_BADGE01_GET", True)
    go(g, "Route44_hns", 66, 13)
    step(g, "RIGHT", 26)
    if current(g) == "Route44_hns":
        step(g, "RIGHT", 26)
    expect(g, "MtMoon_1F_Frlg", "Route 44 with Stone Badge")

    # 4. Blackthorn Gym door and return.
    go(g, "BlackthornCity_hns", 16, 29)
    step(g, "UP", 16)
    expect(g, "PlasticOx_ClairGym", "Blackthorn Gym door")
    go(g, "PlasticOx_ClairGym", 5, 18)
    step(g, "DOWN", 26)
    expect(g, "BlackthornCity_hns", "Blackthorn Gym exit")

    # 5. Goldenrod Gym door and return.
    go(g, "GoldenrodCity_hns", 39, 14)
    step(g, "UP", 16)
    expect(g, "PlasticOx_WhitneyGym", "Goldenrod Gym door")
    go(g, "PlasticOx_WhitneyGym", 5, 18)
    step(g, "DOWN", 26)
    expect(g, "GoldenrodCity_hns", "Goldenrod Gym exit")

    # 6. Ecruteak east road and return.
    g.flag("FLAG_POX_STORY_BURNED_TOWER", True)
    go(g, "EcruteakCity_hns", 64, 42)
    step(g, "RIGHT", 16, mash=False)
    expect(g, "Route119", "Ecruteak east road")
    g.frame(240)
    step(g, "LEFT", 26, mash=False)
    expect(g, "EcruteakCity_hns", "Route 119 west return")

    # 7. Victory Road arrival must not eject on the first step south.
    go(g, "PlasticOx_VictoryRoad", 27, 48)
    step(g, "DOWN", 12)
    assert current(g) == "PlasticOx_VictoryRoad", f"Victory Road ejected after one step: {current(g)} {pos(g)}"
    print("  ok  Victory Road first step keeps the map at", pos(g))

    # 8. Fortree Kecleon blocks the east exit until badge 4.
    g.flag("FLAG_BADGE04_GET", False)
    go(g, "FortreeCity", 37, 10)
    step(g, "RIGHT", 14)
    assert current(g) == "FortreeCity" and pos(g)[0] <= 38, f"Kecleon did not block: {current(g)} {pos(g)}"
    print("  ok  Fortree east exit blocked before badge 4 at", pos(g))
    g.flag("FLAG_BADGE04_GET", True)
    go(g, "FortreeCity", 37, 10)
    g.frame(60)
    g.core.set_keys(K.KEY_RIGHT)
    g.frame(30)
    g.core.clear_keys(K.KEY_RIGHT)
    g.frame(40)
    for _ in range(14):
        g.tap(K.KEY_A, hold=8, wait=30)
        if g.flag("FLAG_KECLEON_FLED_FORTREE"):
            break
    assert g.flag("FLAG_KECLEON_FLED_FORTREE"), "Kecleon never revealed/fled after badge 4"
    step(g, "RIGHT", 14, mash=False)
    step(g, "RIGHT", 14, mash=False)
    expect(g, "Route110", "Fortree east exit after badge 4")

    print("\nPASS: review-fix transitions (8 scenarios)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
