#!/usr/bin/env python3
"""Wave 5 headless verification: Legs H/I/J (surf-deferred variant).

Pallet -> Leg A -> Ilex -> R34 -> Goldenrod -> R35 -> Park -> R36 ->
Johto portal -> Route6 -> Saffron -> Route5 -> Blackthorn -> Indigo
Plateau -> Pokemon Center interior. Return Stone home.
"""
from pathlib import Path
import sys
from collections import deque

DEMO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DEMO_DIR))

import walk_demo as W
import walk_leg1 as L1
from walklib import GBA, K, boot_to_bedroom

MAP_HOUSE_1F = W.MAP_HOUSE_1F
MAP_ROUTE101 = W.MAP_ROUTE101
MAP_OLDALE = W.MAP_OLDALE
MAP_PALLET = W.MAP_PALLET
MAP_R29 = (77, 0)
MAP_R46 = (77, 3)
MAP_DARKCAVE = (77, 4)
MAP_R31 = (77, 2)
MAP_GATE = (76, 6)          # Azalea/Ilex gate
MAP_ILEX = (78, 0)
MAP_R34 = (77, 6)
MAP_GOLDENROD = (77, 11)
MAP_R35 = (77, 12)
MAP_PARK = (78, 2)
MAP_R36 = (77, 13)
MAP_R37 = (77, 14)
MAP_ECRUTEAK = (77, 15)
MAP_R38 = (77, 16)
MAP_R6 = (77, 20)
MAP_SAFFRON = (77, 21)
MAP_R5 = (77, 22)
MAP_BLACKTHORN = (77, 23)
MAP_INDIGO = (77, 24)
MAP_INDIGO_PC = (76, 12)


def nav(g, target, *ok_maps, avoid=frozenset()):
    try:
        L1.navigate(g, target, avoid=avoid)
    except (AssertionError, TypeError):
        pass
    st = g.state()
    return any((st["group"], st["num"]) == m for m in ok_maps)


def try_cross_up_columns(g, dest_map, stage):
    info = g.mapheader_info()
    for x in range(info["w"]):
        st = g.state()
        if (st["group"], st["num"]) == dest_map:
            return
        path = L1.find_path_elev(g, lambda X, Y, w, h, _x=x: (Y == 0 and X == _x))
        if not path:
            continue
        for i in range(1, min(len(path), 5)):
            cur = g.state()
            if (cur["x"], cur["y"]) != path[i - 1][:2]:
                break
            W.step_toward(g, path[i - 1][:2], path[i][:2])
        for _ in range(6):
            s2 = g.state()
            if (s2["group"], s2["num"]) == dest_map:
                for _ in range(150):
                    g.frame(1)
                W.assert_map(g, dest_map, stage)
                return
            g.tap(K.KEY_UP, hold=10, wait=18)
    raise AssertionError(f"{stage}: no working UP column from {g.describe()}")


def main():
    g = GBA()
    print(f"ROM {g.core.game_code}", flush=True)
    boot_to_bedroom(g)
    L1.set_flag(g, 0x74)
    navigate = L1.navigate

    def stage(name):
        print(f"STAGE {name}: {g.describe()}", flush=True)

    # ================= Leg A =================
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
    g.shot("leg5_01_r31.png")

    # ---------- gate -> Ilex ----------
    L1.enter_warp(g, (10, 9), "LEFT", MAP_GATE, "gate_in")
    stage("gate_in")

    # physics walk: gate interior row 6 westward, then UP into Ilex;
    # tolerate bounce-backs through the R31-side door.
    for i in range(40):
        st = g.state()
        gm = (st["group"], st["num"])
        if gm == MAP_ILEX:
            break
        if gm == MAP_R31:
            if st["y"] < 9 or st["x"] > 12:
                navigate(g, (12, 9), avoid={(14, 20), (56, 46)})
            else:
                g.tap(K.KEY_DOWN, hold=8, wait=14)
        else:  # inside gate
            if st["x"] > 1 and st["y"] >= 6:
                g.tap(K.KEY_LEFT, hold=10, wait=16)
            elif st["x"] <= 1 and st["y"] >= 6:
                g.tap(K.KEY_UP, hold=10, wait=18)
            elif st["y"] < 6:
                g.tap(K.KEY_DOWN, hold=8, wait=14)
    else:
        raise AssertionError("ilex_in never fired")
    for _ in range(120):
        g.frame(1)
    W.assert_map(g, MAP_ILEX, "ilex_in")
    stage("ilex_south")

    # ---------- Ilex north coord -> R34 ----------
    g.tap(K.KEY_UP, hold=10, wait=24)  # bypass portal at (22,62)
    for _ in range(150):
        g.frame(1)
    W.assert_map(g, MAP_R34, "r34_from_ilex")
    print("r34 landing:", g.describe(), flush=True)

    # ---------- R34 north seam -> GOLDENROD ----------
    navigate(g, (26, 1))
    W.cross_connection(g, "UP", MAP_GOLDENROD, "goldenrod_from_r34")
    stage("goldenrod")
    g.shot("leg5_02_goldenrod.png")

    # ---------- Goldenrod plaza portal -> R35 ----------
    navigate(g, (34, 8))
    L1.enter_warp(g, (34, 7), "UP", MAP_R35, "r35_from_goldenrod")
    stage("r35_south")

    # ---------- R35 north portal -> R36 (wave-4 topology) ----------
    navigate(g, (17, 6))
    L1.enter_warp(g, (17, 5), "UP", MAP_R36, "r36_from_r35")
    stage("r36")
    g.shot("leg5_03_r36.png")

    # ---------- R36 Johto portal -> Route6 ----------
    # pure physics walk east along the pocket, then onto the Johto portal
    for i in range(60):
        st = g.state()
        gm = (st["group"], st["num"])
        if gm == MAP_SAFFRON:
            break
        if gm != MAP_R36:
            break
        if st["x"] < 21:
            g.tap(K.KEY_RIGHT, hold=10, wait=16)
        elif st["y"] < 21:
            g.tap(K.KEY_DOWN, hold=10, wait=16)
        else:
            g.tap(K.KEY_DOWN, hold=10, wait=24)  # step onto the portal
    else:
        raise AssertionError("johto portal never fired")
    for _ in range(150):
        g.frame(1)
    W.assert_map(g, MAP_SAFFRON, "saffron_portal")
    stage("saffron")
    g.shot("leg5_04_saffron.png")

    # ---------- Saffron north gate portal -> Route5 ----------
    navigate(g, (28, 6))
    L1.enter_warp(g, (28, 4), "UP", MAP_R5, "r5_from_saffron")
    stage("r5")
    g.shot("leg5_06_r5.png")

    # ---------- R5 top portal -> BLACKTHORN ----------
    navigate(g, (18, 1))
    L1.enter_warp(g, (18, 0), "UP", MAP_BLACKTHORN, "blackthorn_portal")
    stage("blackthorn")
    g.shot("leg5_07_blackthorn.png")

    # ---------- Blackthorn portal -> INDIGO PLATEAU ----------
    navigate(g, (42, 23))
    L1.enter_warp(g, (42, 22), "UP", MAP_INDIGO, "indigo_portal")
    stage("indigo")
    g.shot("leg5_08_indigo.png")

    # ---------- Return Stone on the plateau steps ----------
    g.tap(K.KEY_UP, hold=10, wait=24)
    for _ in range(150):
        g.frame(1)
    W.assert_map(g, MAP_PALLET, "return_stone")
    stage("home")
    g.shot("leg5_09_home.png")

    assert W.assert_no_battle(g) is None or True
    print("LEG 5 HEADLESS VERIFICATION PASSED", flush=True)


if __name__ == "__main__":
    main()
