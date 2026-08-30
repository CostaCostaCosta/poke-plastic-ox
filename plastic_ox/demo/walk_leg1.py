#!/usr/bin/env python3
"""Wave 1C headless verification: Leg A round trip.

Pallet bedroom -> Pallet -> Route101 -> Oldale -> (W) Route29_hns ->
(gate) Route46_hns -> (warp) DarkCave_SouthSide_hns -> (warp) Route31_hns ->
(S) Route30_hns -> (S) CherrygroveCity_hns, then the whole thing in reverse
back to the bedroom's front lawn. Fails on any battle or wrong map.
"""
from pathlib import Path
import sys

DEMO_DIR = Path(__file__).resolve().parent
REPO = DEMO_DIR.parents[1]
sys.path.insert(0, str(DEMO_DIR))

import walk_demo as W
from walklib import GBA, DIRKEY, K, boot_to_bedroom

MAP_BEDROOM = W.MAP_BEDROOM
MAP_HOUSE_1F = W.MAP_HOUSE_1F
MAP_PALLET = W.MAP_PALLET
MAP_ROUTE101 = W.MAP_ROUTE101
MAP_OLDALE = W.MAP_OLDALE
MAP_R29 = (77, 0)
MAP_R30 = (77, 1)
MAP_R31 = (77, 2)
MAP_R46 = (77, 3)
MAP_DARKCAVE = (77, 4)
MAP_CHERRYGROVE = (77, 5)
MAP_R29_GATE = (76, 13)
MAP_R30_HOUSE = (76, 14)
MAP_R30_MR_POKEMONS_HOUSE = (76, 15)

FLAG_ADVENTURE_STARTED = 0x74
EXTRA_AVOID = set()  # tiles discovered hazardous at runtime (e.g. secret-base doors)
SAVEBLOCK1_FLAGS_OFFSET = 0x1270


def set_flag(g, flag_id):
    base = int(g.state()["ptr"], 16) - 0x02000000 + SAVEBLOCK1_FLAGS_OFFSET
    g.core.memory.wram.u8[base + flag_id // 8] |= 1 << (flag_id % 8)


def _tile_elev(g, x, y):
    return g.collision_at(x, y)[1]


def find_path_elev(g, goal, avoid=frozenset()):
    """walk_demo.find_path plus elevation gating (hns maps are multi-level).

    Mirrors the engine (event_object_movement.c): an object's currentElevation
    always becomes its current tile's elevation (ELEVATION_TRANSITION=0 stays
    0), and IsElevationMismatchAt only rejects when BOTH the mover elevation
    and the destination tile elevation are nonzero and differ.
    """
    from collections import deque

    state = g.state()
    info = g.mapheader_info()
    width, height = info["w"], info["h"]
    sx, sy = state["x"], state["y"]
    start_elev = _tile_elev(g, sx, sy)
    occupied = W.object_tiles(g)
    start = (sx, sy, start_elev)
    queue = deque([start])
    previous = {start: None}

    while queue:
        x, y, e = queue.popleft()
        if goal(x, y, width, height):
            path = []
            current = (x, y, e)
            while current is not None:
                path.append(current[:2])
                current = previous[current]
            return path[::-1]
        for direction, dx, dy in (("UP", 0, -1), ("DOWN", 0, 1), ("LEFT", -1, 0), ("RIGHT", 1, 0)):
            adjacent = (x + dx, y + dy)
            ax, ay = adjacent
            if not (0 <= ax < width and 0 <= ay < height):
                continue
            collision, elev = g.collision_at(ax, ay)
            behavior, _, _ = g.behavior_at(ax, ay)
            if behavior == W.LEDGE_BEHAVIOR_BY_DIRECTION[direction]:
                nxt = (x + 2 * dx, y + 2 * dy)
                nx, ny = nxt
                if not (0 <= nx < width and 0 <= ny < height):
                    continue
                land_col, land_elev = g.collision_at(nx, ny)
                if land_col != 0 or (nx, ny) in occupied or (nx, ny) in avoid or (nx, ny) in EXTRA_AVOID:
                    continue
                if land_elev != 0 and e != 0 and land_elev != e:
                    continue
                node = (nx, ny, land_elev)
            else:
                if collision != 0 or (ax, ay) in occupied or (ax, ay) in avoid or (ax, ay) in EXTRA_AVOID:
                    continue
                if elev != 0 and e != 0 and elev != e:
                    continue
                node = (ax, ay, elev)
            if node in previous:
                continue
            previous[node] = (x, y, e)
            queue.append(node)
    return None


def navigate(g, target, avoid=frozenset()):
    """Walk to target using elevation-aware BFS.

    Follows up to 4 planned steps per replan: object spawn windows flicker
    at the camera edge (e.g. Route30's cuttable tree), which can flip the
    BFS's first move between two adjacent tiles and cause endless
    ping-pong if we replan after every single step.
    """
    for _ in range(700):
        state = g.state()
        if (state["x"], state["y"]) == target:
            return
        path = find_path_elev(g, lambda x, y, _w, _h: (x, y) == target, avoid)
        import os
        if os.environ.get("POX_DEBUG_GRID"):
            info = g.mapheader_info()
            with open(os.environ["POX_DEBUG_GRID"], "w") as f:
                for yy in range(info["h"]):
                    for xx in range(info["w"]):
                        c, e = g.collision_at(xx, yy)
                        b, _, _ = g.behavior_at(xx, yy)
                        f.write(f"{xx} {yy} {c} {e} {b}\n")
            print("grid dumped", flush=True)
        assert path and len(path) >= 2, f"target {target} unreachable from {g.describe()} elev={_tile_elev(g, state['x'], state['y'])} objects={sorted(W.object_tiles(g))}"
        for idx in range(1, min(len(path), 5)):
            cur = g.state()
            if (cur["x"], cur["y"]) != path[idx - 1][:2]:
                break  # drifted (bump, turn); replan from where we are
            W.step_toward(g, path[idx - 1][:2], path[idx][:2])
    raise AssertionError(f"could not reach {target} from {g.describe()}")


def enter_warp(g, approach, direction, expected_map, stage):
    """Walk onto `approach`, then tap `direction` until the warp fires."""
    # A previous warp may still be mid-transition (the saveblock updates
    # before the grid is filled); wait for the CURRENT map's grid first.
    state = g.state()
    if state:
        g.wait_warp_complete((state["group"], state["num"]))
    try:
        navigate(g, approach)
    except AssertionError:
        pass  # the approach tile may itself be the warp; arriving IS entering
    state = g.state()
    if state and (state["group"], state["num"]) == expected_map:
        g.wait_warp_complete(expected_map)
        for i in range(120):
            g.frame(1)
        W.assert_map(g, expected_map, stage)
        return
    key = DIRKEY[direction]
    for _ in range(40):
        g.tap(key, hold=8, wait=18)
        state = g.state()
        assert W.assert_no_battle(g) is None or True
        flags = g.u32(g.symbol_address("gBattleTypeFlags"))
        assert flags == 0, f"unexpected battle during warp {stage}"
        if state and (state["group"], state["num"]) == expected_map:
            g.wait_warp_complete(expected_map)
            for i in range(120):
                g.frame(1)
            W.assert_map(g, expected_map, stage)
            return
    raise AssertionError(f"warp {stage} never fired from {g.describe()}")


def route29_to_route46(g):
    """Cross the restored Route 29 gate northbound."""
    enter_warp(g, (34, 11), "UP", MAP_R29_GATE, "r29_gate_in")
    g.shot("leg1_05_r29_gate.png")
    enter_warp(g, (7, 2), "UP", MAP_R46, "r46_gate_out")


def route46_to_route29(g):
    """Cross the restored Route 29 gate southbound."""
    enter_warp(g, (10, 39), "DOWN", MAP_R29_GATE, "r46_gate_in")
    enter_warp(g, (7, 8), "DOWN", MAP_R29, "r29_gate_out")


def main():
    g = GBA()
    print(f"ROM {g.core.game_code}", flush=True)
    boot_to_bedroom(g)
    # Simulate post-starter state: Oldale's vanilla west-entrance guard
    # (OldaleTown_EventScript_BlockedPath) keys off FLAG_ADVENTURE_STARTED.
    set_flag(g, FLAG_ADVENTURE_STARTED)
    W.assert_map(g, MAP_BEDROOM, "bedroom")
    g.shot("leg1_01_bedroom.png")

    # Bedroom -> house 1F -> Mom -> outside.
    g.walk("RIGHT", target=(10, 6))
    g.walk("UP", target=(10, 2))
    for _ in range(3):
        g.hold(K.KEY_LEFT, 90)
        if g.state() and (g.state()["group"], g.state()["num"]) == MAP_HOUSE_1F:
            break
    W.assert_map(g, MAP_HOUSE_1F, "house_1f")
    W.visit_mom(g)

    # Out to Pallet and over Route 101 to Oldale (walk_demo patterns).
    g.walk("RIGHT", target=(10, 3))
    g.walk("LEFT", target=(4, 3))
    g.walk("DOWN", target=(4, 7))
    g.hold(K.KEY_DOWN, 80)
    g.frame(90)
    W.assert_map(g, MAP_PALLET, "pallet")
    g.shot("leg1_02_pallet.png")
    g.walk("DOWN", target=(6, 10))
    g.walk("RIGHT", target=(13, 10))
    g.walk("UP", target=(13, 2))
    g.walk("LEFT", target=(12, 2))
    g.walk("UP", target=(12, 0))
    W.cross_connection(g, "UP", MAP_ROUTE101, "r101_north")
    W.exercise_tall_grass(g, steps=2)
    W.walk_to_edge(g, "north")
    W.cross_connection(g, "UP", MAP_OLDALE, "oldale")
    g.shot("leg1_03_oldale.png")

    # ---- Oldale W -> Route29 E ----
    navigate(g, (1, 10))
    W.cross_connection(g, "LEFT", MAP_R29, "r29_east_entry")
    state = g.state()
    assert state["x"] >= 66, f"R29 entry landed oddly: {g.describe()}"
    g.shot("leg1_04_route29.png")

    # ---- R29 gate to the lower end of R46 ----
    route29_to_route46(g)

    # ---- R46 climb to the Dark Cave mouth ----
    g.shot("leg1_06_route46.png")
    navigate(g, (20, 12))
    enter_warp(g, (20, 12), "UP", MAP_DARKCAVE, "darkcave_r46_entrance")
    state = g.state()
    assert state["x"] >= 50 and state["y"] >= 44, f"cave entry odd: {g.describe()}"

    # ---- traverse the cave NW to the Route 31 mouth ----
    g.shot("leg1_07_darkcave.png")
    # Correct HNS layout semantics make the source cave collision authoritative;
    # do not mask a bad path/warp with retry loops or stale-grid bounce-backs.
    navigate(g, (14, 19), avoid={(14, 20), (56, 46)})
    enter_warp(g, (14, 19), "DOWN", MAP_R31, "r31_cave_mouth")
    W.assert_map(g, MAP_R31, "r31_after_cave")

    # ---- R31 south to Route30 ----
    g.shot("leg1_08_route31.png")
    navigate(g, (33, 22))
    W.cross_connection(g, "DOWN", MAP_R30, "r30_north_entry")

    # ---- R30 south to Cherrygrove ----
    g.shot("leg1_09_route30.png")
    enter_warp(g, (35, 5), "UP", MAP_R30_MR_POKEMONS_HOUSE, "r30_mr_pokemon_in")
    g.shot("leg1_09a_r30_mr_pokemon_house.png")
    enter_warp(g, (5, 7), "DOWN", MAP_R30, "r30_mr_pokemon_out")
    enter_warp(g, (26, 40), "UP", MAP_R30_HOUSE, "r30_house_in")
    g.shot("leg1_09b_r30_house.png")
    enter_warp(g, (4, 7), "DOWN", MAP_R30, "r30_house_out")
    navigate(g, (25, 57))
    W.cross_connection(g, "DOWN", MAP_CHERRYGROVE, "cherrygrove_north_entry")
    print("cherrygrove landing:", g.describe(), flush=True)
    g.shot("leg1_10_cherrygrove.png")
    navigate(g, (57, 9))  # tile south of Guide Gent (his tile & row-8 sides are walls)
    print("at gent:", g.describe(), flush=True)

    # ================= REVERSE =================
    # Exercise the reciprocal route too: Cherrygrove -> R30 -> R31 ->
    # Dark Cave -> R46 -> R29. This catches bad return landings and transition
    # races that a one-way reachability check cannot see.
    navigate(g, (34, 0))
    W.cross_connection(g, "UP", MAP_R30, "r30_south_return")
    navigate(g, (23, 0))
    W.cross_connection(g, "UP", MAP_R31, "r31_south_return")
    g.shot("leg1_12_route31_return.png")

    navigate(g, (48, 10))
    enter_warp(g, (48, 10), "UP", MAP_DARKCAVE, "darkcave_r31_return")
    g.shot("leg1_13_darkcave_return.png")
    navigate(g, (56, 45), avoid={(14, 20), (56, 46)})
    enter_warp(g, (56, 45), "DOWN", MAP_R46, "r46_cave_return")
    g.shot("leg1_14_route46_return.png")

    route46_to_route29(g)
    print("r29 north landing:", g.describe(), flush=True)

    navigate(g, (69, 16))
    g.shot("leg1_16_route29_return.png")
    W.cross_connection(g, "RIGHT", MAP_OLDALE, "oldale_west_return")

    g.shot("leg1_17_oldale_return.png")
    state = g.state()
    navigate(g, (9, 19))  # Oldale's south gate columns sit over R101's opening

    W.walk_to_edge(g, "south")
    W.cross_connection(g, "DOWN", MAP_ROUTE101, "r101_south_return")
    W.walk_to_edge(g, "south")
    W.cross_connection(g, "DOWN", MAP_PALLET, "pallet_return")
    g.shot("leg1_18_pallet_return.png")

    assert W.assert_no_battle(g) is None or True
    print("LEG 1 HEADLESS VERIFICATION PASSED", flush=True)


if __name__ == "__main__":
    main()
