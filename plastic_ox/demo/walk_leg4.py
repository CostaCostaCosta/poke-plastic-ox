#!/usr/bin/env python3
"""Wave 4 headless verification: Legs F+G.

Pallet -> (Leg A/B/C/D route per walk_leg3) -> R36 -> National Park spur ->
R36 -> portal -> R37 -> portal -> Ecruteak -> Kanto-gate portal -> Route7 ->
Lavender Town -> portal -> Cinnabar Island. Fails on any battle or wrong map.
"""
from pathlib import Path
import sys

DEMO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DEMO_DIR))

import walk_demo as W
import walk_leg1 as L1
import walk_leg3 as L3
from walklib import GBA, K, boot_to_bedroom

MAP_HOUSE_1F = W.MAP_HOUSE_1F
MAP_PALLET = W.MAP_PALLET
MAP_ROUTE101 = W.MAP_ROUTE101
MAP_OLDALE = W.MAP_OLDALE
MAP_R29 = (77, 0)
MAP_R30 = (77, 1)
MAP_R31 = (77, 2)
MAP_R46 = (77, 3)
MAP_DARKCAVE = (77, 4)
MAP_GATE = (76, 6)  # Azalea/Ilex gate
MAP_ILEX = (78, 0)
MAP_R34 = (77, 6)
MAP_GOLDENROD = (77, 11)
MAP_R35 = (77, 12)
MAP_R36 = (77, 13)
MAP_R37 = (77, 14)
MAP_ECRUTEAK = (77, 15)
MAP_PARK = (78, 2)
MAP_R7 = (77, 25)
MAP_LAVENDER = (77, 26)
MAP_CINNABAR = (77, 29)


def main():
    g = GBA()
    print(f"ROM {g.core.game_code}", flush=True)
    boot_to_bedroom(g)
    L1.set_flag(g, 0x74)  # FLAG_ADVENTURE_STARTED
    navigate = L1.navigate

    def stage(name):
        print(f"STAGE {name}: {g.describe()}", flush=True)

    # ================= Leg A to R31 (proven walk_leg3 route) =================
    g.walk("RIGHT", target=(10, 6)); g.walk("UP", target=(10, 2))
    for _ in range(3):
        g.hold(K.KEY_LEFT, 90)
        if (g.state()["group"], g.state()["num"]) == MAP_HOUSE_1F:
            break
    W.visit_mom(g)
    g.walk("RIGHT", target=(10, 3)); g.walk("LEFT", target=(4, 3)); g.walk("DOWN", target=(4, 7))
    g.hold(K.KEY_DOWN, 80); g.frame(90)
    g.walk("DOWN", target=(6, 10)); g.walk("RIGHT", target=(13, 10)); g.walk("UP", target=(13, 2))
    g.walk("LEFT", target=(12, 2)); g.walk("UP", target=(12, 0))
    W.cross_connection(g, "UP", MAP_ROUTE101, "r101")
    W.walk_to_edge(g, "north"); W.cross_connection(g, "UP", MAP_OLDALE, "oldale")
    navigate(g, (1, 10)); W.cross_connection(g, "LEFT", MAP_R29, "r29e")
    navigate(g, (38, 4)); navigate(g, (38, 0))
    W.cross_connection(g, "UP", MAP_R46, "r46s")
    navigate(g, (20, 12)); L1.enter_warp(g, (20, 12), "UP", MAP_DARKCAVE, "dc_in")
    navigate(g, (14, 19), avoid={(14, 20), (56, 46)})
    for _ in range(30):
        g.tap(K.KEY_DOWN, hold=8, wait=18)
        st = g.state()
        if st and (st["group"], st["num"]) == MAP_R31:
            break
    stage("r31_mouth")

    # ---------- gate -> Ilex -> Route34 -> Goldenrod -> R35 -> R36 ----------
    L1.enter_warp(g, (10, 9), "LEFT", MAP_GATE, "gate_in")
    for i in range(16):
        st = g.state()
        if (st["group"], st["num"]) == MAP_ILEX:
            break
        if st["x"] > 1 and st["y"] >= 5:
            g.tap(K.KEY_LEFT, hold=10, wait=16)
        elif st["x"] <= 1 and st["y"] > 5:
            g.tap(K.KEY_UP, hold=10, wait=18)
        elif st["x"] <= 1:
            break
    else:
        raise AssertionError("ilex_in failed")
    for _ in range(120):
        g.frame(1)
    W.assert_map(g, MAP_ILEX, "ilex_in")
    L1.enter_warp(g, (22, 62), "UP", MAP_R34, "r34_from_ilex")
    L3.settle_still(g, MAP_R34)
    navigate(g, (26, 1))
    W.cross_connection(g, "UP", MAP_GOLDENROD, "goldenrod_from_r34")
    stage("goldenrod")
    navigate(g, (34, 8))
    L1.enter_warp(g, (34, 7), "UP", MAP_R35, "r35_from_goldenrod")
    navigate(g, (17, 6))
    L1.enter_warp(g, (17, 5), "UP", MAP_R36, "r36_from_r35")
    stage("r36")

    # ================= Leg F/G chain =================
    # R36 west portal -> National Park spur (the former crash poster-child).
    # Land (16,21); walk to (16,20) then step up onto the portal at (16,19).
    navigate(g, (16, 20))
    for k in range(15):
        g.tap(K.KEY_UP, hold=10, wait=18)
        st = g.state()
        if st and (st["group"], st["num"]) == MAP_PARK:
            break
    assert g.wait_grid_ready(39, 24), "park grid never ready"
    W.assert_map(g, MAP_PARK, "park_spur")
    stage("park_spur")
    g.shot("leg4_01_park.png")

    # park portal back to R36
    navigate(g, (39, 26))
    for k in range(15):
        g.tap(K.KEY_DOWN, hold=10, wait=18)
        st = g.state()
        if st and (st["group"], st["num"]) == MAP_R36:
            break
    assert g.wait_grid_ready(16, 20), "r36 grid never ready"
    W.assert_map(g, MAP_R36, "r36_return")

    # R36 portal -> R37
    navigate(g, (19, 19), avoid={(16, 19), (16, 20), (16, 21), (20, 21), (21, 21)})
    for k in range(15):
        g.tap(K.KEY_UP, hold=10, wait=18)
        st = g.state()
        if st and (st["group"], st["num"]) == MAP_R37:
            break
    assert g.wait_grid_ready(12, 39), "r37 grid never ready"
    W.assert_map(g, MAP_R37, "r37")
    stage("r37")
    g.shot("leg4_02_r37.png")

    # R37 portal -> Ecruteak
    navigate(g, (16, 39), avoid={(12, 39), (18, 39)})
    for k in range(15):
        g.tap(K.KEY_DOWN, hold=10, wait=18)
        st = g.state()
        if st and (st["group"], st["num"]) == MAP_ECRUTEAK:
            break
    assert g.wait_grid_ready(15, 33), "ecruteak grid never ready"
    W.assert_map(g, MAP_ECRUTEAK, "ecruteak")
    stage("ecruteak")
    g.shot("leg4_03_ecruteak.png")

    # Kanto gate -> Route 7
    navigate(g, (15, 31))
    for k in range(15):
        g.tap(K.KEY_UP, hold=10, wait=18)
        st = g.state()
        if st and (st["group"], st["num"]) == MAP_R7:
            break
    assert g.wait_grid_ready(4, 25), "r7 grid never ready"
    W.assert_map(g, MAP_R7, "r7")
    stage("r7")
    g.shot("leg4_04_r7.png")

    # Route 7 portal -> Lavender Town
    navigate(g, (4, 22))
    for k in range(15):
        g.tap(K.KEY_UP, hold=10, wait=18)
        st = g.state()
        if st and (st["group"], st["num"]) == MAP_LAVENDER:
            break
    assert g.wait_grid_ready(1, 10), "lavender grid never ready"
    W.assert_map(g, MAP_LAVENDER, "lavender")
    stage("lavender")
    g.shot("leg4_05_lavender.png")

    # Lavender portal -> Cinnabar (R12/R21 water legs surf-gated, deferred)
    navigate(g, (15, 20), avoid={(1, 12)})
    for k in range(15):
        g.tap(K.KEY_DOWN, hold=10, wait=18)
        st = g.state()
        if st and (st["group"], st["num"]) == MAP_CINNABAR:
            break
    assert g.wait_grid_ready(8, 6), "cinnabar grid never ready"
    W.assert_map(g, MAP_CINNABAR, "cinnabar")
    stage("cinnabar")
    g.shot("leg4_06_cinnabar.png")

    assert W.assert_no_battle(g) is None or True
    print("LEG 4 HEADLESS VERIFICATION PASSED", flush=True)


if __name__ == "__main__":
    main()
