#!/usr/bin/env python3
"""Exercise the Ecruteak Gym 3 interior and the east gatehouse.

The gym must be the spooky Heart & Soul shadow maze, reached from the town
door at (20,48), and the east gatehouse must be a real through-passage between
the city and Route 119 instead of a pair of dead arrow-warp tiles.
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
GROUP_ORDER = GROUPS["group_order"]
MAP_IDS: dict[str, tuple[int, int]] = {}
for group_id, group_name in enumerate(GROUP_ORDER):
    for map_id, map_name in enumerate(GROUPS[group_name]):
        MAP_IDS[map_name] = (group_id, map_id)


def at(game: StoryGame, map_name: str) -> bool:
    state = game.state()
    return state is not None and (state["group"], state["num"]) == MAP_IDS[map_name]


def press_until(game: StoryGame, key: int, predicate, limit: int = 40) -> bool:
    for _ in range(limit):
        if predicate():
            return True
        game.hold(key, 8)
        game.frame(60)
    return predicate()


def main() -> None:
    game = StoryGame()
    game.flag("FLAG_POX_STORY_STARTER", True)
    game.flag("FLAG_ADVENTURE_STARTED", True)
    game.flag("FLAG_POX_STORY_BURNED_TOWER", True)
    # Keep expected route trainers from opening a battle during traversal.
    for flag in range(0x500, 0x860):
        game.flag(flag, True)

    # Gym entry and exit.
    game.warp("EcruteakCity_hns", 20, 49)
    game.frame(60)
    assert press_until(game, K.KEY_UP, lambda: at(game, "EcruteakCity_Gym_hns")), (
        "town gym door did not reach the HNS gym", game.state())
    game.warp("EcruteakCity_Gym_hns", 10, 45)
    game.frame(60)
    assert press_until(game, K.KEY_DOWN, lambda: at(game, "EcruteakCity_hns")), (
        "gym exit did not return to town", game.state())
    print("  ok  gym door reaches EcruteakCity_Gym_hns and returns")

    # East gate: west face -> gate -> Route 119.
    game.flag("FLAG_BADGE03_GET", True)
    game.warp("EcruteakCity_hns", 52, 42)
    game.frame(60)
    assert press_until(game, K.KEY_RIGHT, lambda: at(game, "Gate_EcruteakCity_Route42_hns")), (
        "west gate door did not open", game.state())
    assert press_until(game, K.KEY_RIGHT, lambda: at(game, "Route119")), (
        "gate east door did not reach Route 119", game.state())
    print("  ok  city -> gate -> Route 119")

    # Route 119 -> town strip -> east gate face -> town centre.
    assert press_until(game, K.KEY_LEFT, lambda: at(game, "EcruteakCity_hns")), (
        "Route 119 west trigger did not return to town", game.state())
    assert press_until(game, K.KEY_LEFT, lambda: at(game, "Gate_EcruteakCity_Route42_hns")), (
        "east gate door did not open from the town strip", game.state())
    assert press_until(game, K.KEY_LEFT, lambda: at(game, "EcruteakCity_hns")), (
        "gate west door did not reach the town centre", game.state())
    print("  ok  Route 119 -> gate -> city centre (no east-strip softlock)")

    # Before badge 3 the west guard still blocks the gate approach.
    game.flag("FLAG_BADGE03_GET", False)
    game.warp("EcruteakCity_hns", 52, 42)
    game.frame(60)
    for _ in range(4):
        game.hold(K.KEY_RIGHT, 8)
        game.frame(60)
    assert at(game, "EcruteakCity_hns") and game.state()["x"] <= 54, game.state()
    print("  ok  gate guard still blocks without badge 3")

    print("\nPASS: Ecruteak gym and east gate")


if __name__ == "__main__":
    main()
