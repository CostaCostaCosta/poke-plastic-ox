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
    # (5,17) is plain road (no stray stump); the Mt. Moon mouth uses the
    # donor's path-top tiles with grass at (66,13) so the approach stays open.
    assert route.blocks[17 * route.w + 5] == 0x30D9
    assert route.blocks[15 * route.w + 59] == 0x30D1
    assert [route.blocks[13 * route.w + x] for x in range(66, 69)] == [0x3000, 0x30D0, 0x30D1]
    # The tree wall closing the Surf-only grass ends in a whole tree.
    assert [route.blocks[y * route.w + 48] for y in (11, 12, 13)] == [0x041A, 0x0412, 0x0422]
    route_data = json.loads((ROOT / "data/maps/Route44_hns/map.json").read_text())
    city_data = json.loads((ROOT / "data/maps/RustboroCity/map.json").read_text())
    # Rustboro <-> Route 44 is a reciprocal camera seam, not a warp.
    assert {"map": "MAP_ROUTE44_HNS", "offset": -5, "direction": "right"} in city_data["connections"]
    assert route_data["connections"] == [{"map": "MAP_RUSTBORO_CITY", "offset": 5, "direction": "left"}]
    assert not any(e["script"].startswith("PoxRegion_rustboro_route44_b") for e in route_data["coord_events"])
    for data in (route_data, city_data):
        for event in data["coord_events"]:
            if event["script"].startswith("PoxRegion_rustboro_route44"):
                assert event["var"] == "VAR_POX_PORTAL_TRIGGER"
    assert not any((event["x"], event["y"]) == (66, 13)
                   for event in route_data["bg_events"])

    game = StoryGame()
    assert game.var(0x40FC) >= 1  # New-game save migration must not suppress the portal.
    assert game.var(0x40DB) == 0
    # Trainer battles are separate from collision and would pause a headless
    # walking test in dialogue. Keep the NPCs present as route obstacles.
    for name in ("ROUTE44", "ROUTE44_EDGAR", "ROUTE44_WILTON",
                 "ROUTE44_ZACH", "ROUTE44_ALLEN", "ROUTE44_CYBIL",
                 "ROUTE44_VANCE"):
        trainer = game.const("TRAINER_PLASTIC_OX_" + name)
        game.flag(0x4A0 + trainer - 857, True)
    # Story gate: Route 44 requires the Stone Badge on both approaches.
    game.flag("FLAG_BADGE01_GET", True)
    # Derive the whole road opening so a wider road cannot outgrow a fixed
    # list of lanes again; the stone road is five rows wide (8..12).
    city = Geometry("RustboroCity")
    lanes = [10]
    for direction in (-1, 1):
        y = 10 + direction
        while all(city.passable(x, y) for x in range(35, 40)):
            lanes.append(y)
            y += direction
    assert sorted(lanes) == list(range(8, 13)), lanes
    # Without the badge the edge trigger turns the player back.
    game.flag("FLAG_BADGE01_GET", False)
    game.warp("RustboroCity", 35, 10)
    game.tap(K.KEY_RIGHT, hold=100, wait=30)
    for _ in range(6):
        game.tap(K.KEY_A, wait=30)
    state = assert_map(game, "RustboroCity", ids)
    assert state["x"] <= 38, state
    game.flag("FLAG_BADGE01_GET", True)
    # Rows 8..11 walk onto Route 44's grass/path rows 13..16; row 12 meets
    # the route's cliff and stays in the city.
    for y in sorted(lanes):
        game.warp("RustboroCity", 35, y)
        game.tap(K.KEY_RIGHT, hold=100, wait=90)
        state = game.state()
        if y == 12:
            assert (state["group"], state["num"]) == ids["RustboroCity"], state
            assert (state["x"], state["y"]) == (39, 12), state
            continue
        assert_map(game, "Route44_hns", ids)
        assert state["y"] == y + 5 and state["x"] <= 2, state
        if y == 10:
            game.shot("route44_from_rustboro_fixed.png")
    # Mid-crossing camera: both maps on screen.
    game.warp("RustboroCity", 36, 10)
    game.tap(K.KEY_RIGHT, hold=40, wait=30)
    game.shot("route44_seam_crossing.png")
    game.warp("Route44_hns", 1, 15)
    game.frame(60)

    # Walk the actual route rather than teleporting over the formerly blocked
    # middle. This catches invisible walls and isolated visible paths.
    game.test_water = False
    navigate(game, lambda x, y: (x, y) == (65, 13))
    game.frame(120)
    game.shot("route44_full_walk_fixed.png")

    navigate(game, lambda x, y: (x, y) == (1, 15))
    game.tap(K.KEY_LEFT, hold=40, wait=90)
    state = assert_map(game, "RustboroCity", ids)
    assert state["y"] == 10 and state["x"] >= 37, state
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
