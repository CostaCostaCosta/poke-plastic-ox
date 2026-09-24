#!/usr/bin/env python3
"""Regression coverage for Route 44's Rustboro and Mt. Moon approaches."""
import json
import sys

from test_story import StoryGame, ROOT
from walklib import K

sys.path.insert(0, str(ROOT / "plastic_ox/alpha"))
from region_geometry import Geometry


def map_ids():
    groups = json.loads((ROOT / "data/maps/map_groups.json").read_text())
    return {name: (group, number)
            for group, key in enumerate(groups["group_order"])
            for number, name in enumerate(groups[key])}


def assert_map(game, expected, ids):
    state = game.state()
    assert (state["group"], state["num"]) == ids[expected], state
    return state


def main():
    ids = map_ids()
    route = Geometry("Route44_hns")

    # No passable covered block may remain: these were the tiles that hid the
    # player inside tree rows and cliff faces.
    for y in range(route.h):
        for x in range(route.w):
            value = route.blocks[y * route.w + x]
            metatile = value & 0x3FF
            bank = metatile >= route.partition
            attr_index = metatile - route.partition if bank else metatile
            layer = (route.attrs[bank][attr_index] >> 12) & 3
            assert not (layer == 1 and route.tile(x, y)[0] == 0), (x, y, hex(value))

    # The obsolete sign replacement belongs at (5,17), not near Mt. Moon.
    assert route.blocks[17 * route.w + 5] == 0x0473
    assert route.blocks[15 * route.w + 59] == 0x34D1
    assert [route.blocks[13 * route.w + x] for x in range(66, 69)] == [0x30D8] * 3
    route_data = json.loads((ROOT / "data/maps/Route44_hns/map.json").read_text())
    assert not any((event["x"], event["y"]) == (66, 13)
                   for event in route_data["bg_events"])

    game = StoryGame()
    for y in (9, 10, 11):
        game.warp("RustboroCity", 38, y)
        game.tap(K.KEY_RIGHT, hold=24, wait=90)
        state = assert_map(game, "Route44_hns", ids)
        assert (state["x"], state["y"]) == (1, 13), state

    game.warp("Route44_hns", 1, 13)
    game.tap(K.KEY_LEFT, hold=24, wait=90)
    state = assert_map(game, "RustboroCity", ids)
    assert (state["x"], state["y"]) == (38, 10), state
    game.shot("route44_rustboro_fixed.png")

    game.flag("FLAG_BADGE01_GET", True)
    game.warp("Route44_hns", 65, 13)
    game.frame(180)
    game.shot("route44_mtmoon_approach_fixed.png")
    game.walk("RIGHT", target=(67, 13))
    game.tap(K.KEY_RIGHT, hold=24, wait=90)
    state = assert_map(game, "MtMoon_Cave_hns", ids)
    assert (state["x"], state["y"]) == (3, 11), state
    game.frame(180)
    game.shot("route44_mtmoon_fixed.png")
    print("PASS: Route 44 scenery collision and both approaches")


if __name__ == "__main__":
    main()
