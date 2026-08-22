#!/usr/bin/env python3
"""Authoritative headless verification for the Plastic Ox map-stitch demo.

Flow: NEW GAME -> Pallet bedroom -> Mom -> Pallet Town -> Route 101 ->
Oldale Town -> Route 101 -> Pallet Town. The run fails immediately if a
battle starts, so a passing round trip also checks Route 101's empty table.
"""
from collections import deque
import json
from pathlib import Path
import sys

DEMO_DIR = Path(__file__).resolve().parent
REPO = DEMO_DIR.parents[1]
sys.path.insert(0, str(DEMO_DIR))

from walklib import DIRKEY, GBA, K

MAP_BEDROOM = (38, 1)
MAP_HOUSE_1F = (38, 0)
MAP_PALLET = (75, 0)
MAP_ROUTE101 = (0, 16)
MAP_OLDALE = (0, 10)
LEDGE_BEHAVIOR_BY_DIRECTION = {
    "RIGHT": 0x38,
    "LEFT": 0x39,
    "UP": 0x3A,
    "DOWN": 0x3B,
}


def check_static_invariants():
    route_encounters = (REPO / "src/data/wild_encounters.json").read_text()
    generated_encounters = (REPO / "src/data/wild_encounters.h").read_text()
    assert '"map": "MAP_ROUTE101"' not in route_encounters, "Route 101 still has a source encounter table"
    assert "gRoute101LandMons" not in generated_encounters, "Route 101 still has a compiled encounter table"

    pallet = json.loads((REPO / "data/maps/PalletTown_Frlg/map.json").read_text())
    lab = json.loads((REPO / "data/maps/PalletTown_ProfessorOaksLab_Frlg/map.json").read_text())
    route101 = json.loads((REPO / "data/maps/Route101/map.json").read_text())
    assert pallet["coord_events"] == [], "Pallet Town still has imported scene triggers"
    assert lab["coord_events"] == [], "Oak's Lab still has imported scene triggers"
    assert route101["coord_events"] == [], "Route 101 still has imported scene triggers"
    route_scripts = {event["script"] for event in route101["object_events"]}
    assert route_scripts == {
        "Route101_EventScript_Youngster",
        "Route101_EventScript_Boy",
    }, f"Route 101 still has imported story objects: {route_scripts}"

    scene_free_scripts = "\n".join(
        (REPO / path).read_text()
        for path in (
            "data/maps/PalletTown_Frlg/scripts.inc",
            "data/maps/PalletTown_PlayersHouse_1F_Frlg/scripts.inc",
            "data/maps/PalletTown_ProfessorOaksLab_Frlg/scripts.inc",
            "data/maps/PalletTown_RivalsHouse_Frlg/scripts.inc",
            "data/maps/Route101/scripts.inc",
        )
    )
    for forbidden in ("trainerbattle", "applymovement", "{RIVAL}", "ChooseStarter", "StartBirchRescue"):
        assert forbidden not in scene_free_scripts, f"imported scene command remains: {forbidden}"


def assert_map(g, expected, stage):
    state = g.state()
    actual = None if state is None else (state["group"], state["num"])
    assert actual == expected, f"{stage}: expected map {expected}, got {g.describe()}"
    print(f"STAGE {stage}: {g.describe()}", flush=True)


def assert_no_battle(g):
    flags = g.u32(g.symbol_address("gBattleTypeFlags"))
    assert flags == 0, f"unexpected battle on {g.describe()} (gBattleTypeFlags={flags:#x})"


def object_tiles(g):
    base = g.symbol_address("gObjectEvents")
    occupied = set()
    for index in range(16):
        obj = base + index * 0x24
        if not (g.u8(obj) & 1):
            continue
        if g.u8(obj + 2) & 1:  # player
            continue
        if g.u8(obj + 1) & 0x20:  # invisible
            continue
        occupied.add((g.s16(obj + 0x10) - 7, g.s16(obj + 0x12) - 7))
    return occupied


def find_path(g, goal):
    state = g.state()
    info = g.mapheader_info()
    width, height = info["w"], info["h"]
    start = (state["x"], state["y"])
    occupied = object_tiles(g)
    queue = deque([start])
    previous = {start: None}

    while queue:
        x, y = queue.popleft()
        if goal(x, y, width, height):
            path = []
            current = (x, y)
            while current is not None:
                path.append(current)
                current = previous[current]
            return path[::-1]
        for direction, dx, dy in (("UP", 0, -1), ("DOWN", 0, 1), ("LEFT", -1, 0), ("RIGHT", 1, 0)):
            adjacent = (x + dx, y + dy)
            ax, ay = adjacent
            if not (0 <= ax < width and 0 <= ay < height):
                continue

            collision, _ = g.collision_at(ax, ay)
            behavior, _, _ = g.behavior_at(ax, ay)
            if behavior == LEDGE_BEHAVIOR_BY_DIRECTION[direction]:
                # A ledge is a directed two-tile graph edge. During the jump,
                # the engine briefly reports the ledge coordinate before the
                # player lands on the tile beyond it; treating that midpoint
                # as the final move is the apparent "off-by-one" seen by the
                # old verifier.
                nxt = (x + 2 * dx, y + 2 * dy)
                nx, ny = nxt
                if not (0 <= nx < width and 0 <= ny < height):
                    continue
                landing_collision, _ = g.collision_at(nx, ny)
                if landing_collision != 0 or adjacent in occupied:
                    continue
            else:
                nxt = adjacent
                nx, ny = nxt
                if collision != 0:
                    continue

            if nxt in previous or nxt in occupied:
                continue
            previous[nxt] = (x, y)
            queue.append(nxt)
    return None


def step_toward(g, current, nxt):
    x, y = current
    nx, ny = nxt
    direction = "UP" if ny < y else "DOWN" if ny > y else "LEFT" if nx < x else "RIGHT"
    distance = abs(nx - x) + abs(ny - y)
    assert distance in (1, 2), f"unsupported movement edge: {current} -> {nxt}"
    for _ in range(5):
        actual = (g.state()["x"], g.state()["y"])
        if actual == nxt:
            return
        assert actual == current, f"movement drifted from {current} toward {nxt}, got {actual}"
        g.tap(DIRKEY[direction], hold=8, wait=30 if distance == 2 else 18)
        assert_no_battle(g)
    actual = (g.state()["x"], g.state()["y"])
    assert actual == nxt, f"movement did not advance from {current} toward {nxt}, got {actual}"


def navigate_to(g, target):
    for _ in range(700):
        state = g.state()
        if (state["x"], state["y"]) == target:
            return
        path = find_path(g, lambda x, y, _w, _h: (x, y) == target)
        assert path and len(path) >= 2, f"target {target} is unreachable from {g.describe()}"
        step_toward(g, path[0], path[1])
    raise AssertionError(f"could not reach {target} from {g.describe()}")


def walk_to_edge(g, edge, mid_shot=None):
    for _ in range(700):
        state = g.state()
        info = g.mapheader_info()
        target_y = 0 if edge == "north" else info["h"] - 1
        if state["y"] == target_y:
            return
        path = find_path(g, lambda _x, y, _w, h: y == (0 if edge == "north" else h - 1))
        if not path or len(path) < 2:
            g.frame(30)
            continue
        step_toward(g, path[0], path[1])
        state = g.state()
        if mid_shot and edge == "north" and state["y"] <= info["h"] // 2:
            g.shot(mid_shot)
            mid_shot = None
    raise AssertionError(f"could not reach {edge} edge from {g.describe()}")


def exercise_tall_grass(g, steps=80):
    """Deliberately walk in encounter-bearing terrain and reject any battle."""
    grass = (12, 10)
    partner = (13, 10)

    for _ in range(300):
        state = g.state()
        if (state["x"], state["y"]) == grass:
            break
        path = find_path(g, lambda x, y, _w, _h: (x, y) == grass)
        assert path and len(path) >= 2, f"Route 101 grass tile {grass} is unreachable"
        step_toward(g, path[0], path[1])
    else:
        raise AssertionError("could not enter Route 101 tall grass")

    assert g.behavior_at(*grass)[0] == 2, f"{grass} is no longer MB_TALL_GRASS"
    assert g.behavior_at(*partner)[0] == 2, f"{partner} is no longer MB_TALL_GRASS"

    def move_adjacent(src, dst):
        for _ in range(4):
            actual = (g.state()["x"], g.state()["y"])
            if actual == dst:
                return
            assert actual == src, f"grass movement drifted to {actual}, expected {src}"
            step_toward(g, src, dst)
        actual = (g.state()["x"], g.state()["y"])
        assert actual == dst, f"failed grass step: {src} -> {dst}, got {actual}"

    # Move between two encounter-bearing tiles repeatedly. This catches both a
    # stale compiled encounter table and any unexpected battle transition.
    for _ in range(steps):
        move_adjacent(grass, partner)
        move_adjacent(partner, grass)
    assert_no_battle(g)


def exercise_route101_ledge(g):
    """Verify the vanilla one-way, two-tile jump at Route 101's lower ledge."""
    approach = (9, 12)
    ledge = (9, 13)
    landing = (9, 14)
    navigate_to(g, approach)
    assert g.behavior_at(*ledge)[0] == LEDGE_BEHAVIOR_BY_DIRECTION["DOWN"], (
        f"{ledge} is no longer a south-jump ledge"
    )
    assert g.collision_at(*ledge)[0] != 0, f"ledge {ledge} unexpectedly has no collision"
    assert g.collision_at(*landing)[0] == 0, f"ledge landing {landing} is blocked"
    g.shot("verified_06a_ledge_approach.png")

    coordinates = []
    g.core.set_keys(DIRKEY["DOWN"])
    try:
        for _ in range(40):
            g.frame(1)
            state = g.state()
            position = (state["x"], state["y"])
            coordinates.append(position)
            assert position in (approach, ledge, landing), f"ledge jump drifted to {position}"
            if position == landing:
                break
        else:
            raise AssertionError(f"ledge jump did not land: {coordinates}")
    finally:
        g.core.clear_keys(DIRKEY["DOWN"])
    g.frame(20)
    assert (g.state()["x"], g.state()["y"]) == landing, f"ledge landed at {g.describe()}"
    assert ledge in coordinates, "ledge jump never reported its normal midpoint coordinate"

    # South-facing ledges are intentionally one-way. Walking back north must
    # collide instead of jumping or entering the ledge tile.
    g.tap(DIRKEY["UP"], hold=8, wait=20)
    assert (g.state()["x"], g.state()["y"]) == landing, "south ledge allowed reverse traversal"
    g.shot("verified_06b_ledge_landing.png")


def assert_not_forced_blank(g, stage, frame):
    extrema = g.fb.to_pil().convert("RGB").getextrema()
    assert not all(low == high == 255 for low, high in extrema), (
        f"{stage}: all-white forced-blank frame at transition frame {frame}"
    )


def cross_connection(g, direction, expected_map, stage):
    key = DIRKEY[direction]
    transition_frame = 0
    for _ in range(20):
        g.core.set_keys(key)
        for _ in range(8):
            g.frame(1)
            assert_not_forced_blank(g, stage, transition_frame)
            transition_frame += 1
        g.core.clear_keys(key)
        for _ in range(18):
            g.frame(1)
            assert_not_forced_blank(g, stage, transition_frame)
            transition_frame += 1
        assert_no_battle(g)
        state = g.state()
        if state and (state["group"], state["num"]) == expected_map:
            for _ in range(150):  # let queued tileset DMA and palette work settle
                g.frame(1)
                assert_not_forced_blank(g, stage, transition_frame)
                transition_frame += 1
            assert_no_battle(g)
            assert_map(g, expected_map, stage)
            return
    raise AssertionError(f"failed {direction} connection into {expected_map}: {g.describe()}")


def visit_mom(g):
    g.walk("DOWN", target=(9, 3))
    g.walk("LEFT", target=(8, 3))
    g.tap(K.KEY_DOWN, hold=2, wait=12)
    g.tap(K.KEY_A, hold=2, wait=20)
    for _ in range(24):
        g.tap(K.KEY_A, hold=1, wait=20)
    g.tap(K.KEY_B, hold=2, wait=20)
    g.shot("verified_02_mom.png")


def main():
    check_static_invariants()
    g = GBA()
    g_battle = g.symbol_address("gBattleTypeFlags")
    print(f"ROM {g.core.game_code} battle_flags={g_battle:#x}", flush=True)

    from walklib import boot_to_bedroom
    boot_to_bedroom(g)
    assert_map(g, MAP_BEDROOM, "bedroom")
    state = g.state()
    assert (state["x"], state["y"]) == (6, 6), f"wrong new-game position: {g.describe()}"
    g.shot("verified_01_bedroom.png")

    # Bedroom stairs: approach (10,2), then step left across the FRLG stair warp.
    g.walk("RIGHT", target=(10, 6))
    g.walk("UP", target=(10, 2))
    for _ in range(3):
        g.hold(K.KEY_LEFT, 90)
        if g.state() and (g.state()["group"], g.state()["num"]) == MAP_HOUSE_1F:
            break
    assert_map(g, MAP_HOUSE_1F, "house_1f")
    visit_mom(g)

    # Leave home and route around the Pallet sign/NPCs to the north opening.
    g.walk("RIGHT", target=(10, 3))
    g.walk("LEFT", target=(4, 3))
    g.walk("DOWN", target=(4, 7))
    g.hold(K.KEY_DOWN, 80)
    g.frame(90)
    assert_map(g, MAP_PALLET, "pallet")
    g.shot("verified_03_pallet.png")
    g.walk("DOWN", target=(6, 10))
    g.walk("RIGHT", target=(13, 10))
    g.walk("UP", target=(13, 2))
    g.walk("LEFT", target=(12, 2))
    g.walk("UP", target=(12, 0))
    g.shot("verified_04_pallet_north_edge.png")

    cross_connection(g, "UP", MAP_ROUTE101, "route101_northbound")
    g.shot("verified_05_route101_entry.png")
    exercise_tall_grass(g)
    exercise_route101_ledge(g)
    walk_to_edge(g, "north", mid_shot="verified_06_route101_mid.png")
    cross_connection(g, "UP", MAP_OLDALE, "oldale")
    g.shot("verified_07_oldale.png")

    walk_to_edge(g, "south")
    cross_connection(g, "DOWN", MAP_ROUTE101, "route101_southbound")
    g.shot("verified_08_route101_return.png")
    walk_to_edge(g, "south")
    cross_connection(g, "DOWN", MAP_PALLET, "pallet_return")
    g.shot("verified_09_pallet_return.png")

    print("HEADLESS DEMO VERIFICATION PASSED", flush=True)


if __name__ == "__main__":
    main()
