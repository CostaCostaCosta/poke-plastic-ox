#!/usr/bin/env python3
"""Regression coverage for Route 44's Rustboro and Mt. Moon approaches."""
import json
import sys

from test_story import StoryGame, ROOT
from test_region_walk import navigate
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

    # Route 44's donor intentionally uses the upper drawing layer on walkable
    # road and overhang blocks. Check the whole land component, not just ports.
    connected = route.component((1, 15))
    # The central grass island is separated from the road by the east trees.
    # Its 56 grass tiles remain accessible through the surrounding water.
    assert len(connected) >= 500, len(connected)
    island_grass = {(x, y) for y in range(12, 17) for x in range(31, 49)
                    if route.tile(x, y)[2] == "MB_TALL_GRASS"}
    assert len(island_grass) == 56
    assert not island_grass & connected
    assert island_grass <= route.component((1, 15), water=True)
    assert (67, 13) in connected
    assert all(route.passable(x, y) for x in range(0, 8) for y in (14, 15, 16))

    # The obsolete sign replacement belongs at (5,17), not near Mt. Moon.
    assert route.blocks[17 * route.w + 5] == 0x0473
    assert route.blocks[15 * route.w + 59] == 0x30D1
    assert [route.blocks[13 * route.w + x] for x in range(66, 69)] == [0x30D8] * 3
    route_data = json.loads((ROOT / "data/maps/Route44_hns/map.json").read_text())
    assert (route_data["coord_events"][0]["x"], route_data["coord_events"][0]["y"]) == (0, 15)
    city_data = json.loads((ROOT / "data/maps/RustboroCity/map.json").read_text())
    for data in (route_data, city_data):
        for event in data["coord_events"]:
            if event["script"].startswith("PoxRegion_rustboro_route44"):
                assert event["var"] == "VAR_POX_PORTAL_TRIGGER"
    assert not any((event["x"], event["y"]) == (66, 13)
                   for event in route_data["bg_events"])

    game = StoryGame()
    assert game.var(0x40FC) == 1  # New-game save migration must not suppress the portal.
    assert game.var(0x40DB) == 0
    # Trainer battles are separate from collision and would pause a headless
    # walking test in dialogue. Keep the NPCs present as route obstacles.
    for name in ("ROUTE44", "ROUTE44_EDGAR", "ROUTE44_WILTON",
                 "ROUTE44_ZACH", "ROUTE44_ALLEN", "ROUTE44_CYBIL",
                 "ROUTE44_VANCE"):
        trainer = game.const("TRAINER_PLASTIC_OX_" + name)
        game.flag(0x4A0 + trainer - 857, True)
    for y in (9, 10, 11):
        game.warp("RustboroCity", 35, y)
        game.tap(K.KEY_RIGHT, hold=100, wait=90)
        state = assert_map(game, "Route44_hns", ids)
        assert (state["x"], state["y"]) == (1, 15), state
        if y == 10:
            game.frame(120)
            game.shot("route44_from_rustboro_fixed.png")

    # Walk the actual route rather than teleporting over the formerly blocked
    # middle. This catches invisible walls and isolated visible paths.
    game.test_water = False
    navigate(game, lambda x, y: (x, y) == (65, 13))
    game.frame(120)
    game.shot("route44_full_walk_fixed.png")

    navigate(game, lambda x, y: (x, y) == (1, 15))
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
    state = assert_map(game, "MtMoon_1F_Frlg", ids)
    assert (state["x"], state["y"]) == (18, 37), state
    game.frame(180)
    game.shot("route44_mtmoon_fixed.png")
    print("PASS: Route 44 full walk in both directions, open road, and both approaches")


if __name__ == "__main__":
    main()
