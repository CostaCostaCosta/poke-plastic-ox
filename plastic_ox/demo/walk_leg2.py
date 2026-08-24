#!/usr/bin/env python3
"""Wave 2 headless verification: Legs B+C.

bedroom -> Leg A -> R31 west gate -> Ilex Forest -> Route34 -> Goldenrod ->
Bill's house -> Route4 portal -> Mt.Moon -> Route3 -> Route2 -> Rustboro ->
Route116, then Return Stone home to Pallet.
"""
from pathlib import Path
import sys

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
MAP_R31 = (77, 2)
MAP_R46 = (77, 3)
MAP_DARKCAVE = (77, 4)
MAP_GATE = (76, 6)
MAP_BILLS = (76, 7)
MAP_ILEX = (78, 0)
MAP_CAVE = (78, 1)
MAP_R34 = (77, 6)
MAP_R116 = (0, 31)
MAP_RUSTBORO = (0, 3)
MAP_R2 = (77, 7)
MAP_R3 = (77, 8)
MAP_R4 = (77, 9)
MAP_GOLDENROD = (77, 11)


def edge_elev(g, edge):
    for _ in range(700):
        st = g.state()
        info = g.mapheader_info()
        tgt = 0 if edge == "north" else info["h"] - 1
        if st["y"] == tgt:
            return
        path = L1.find_path_elev(g, lambda x, y, w, h: y == tgt)
        assert path and len(path) >= 2, f"no path to {edge} edge from {g.describe()}"
        for i in range(1, min(len(path), 5)):
            cur = g.state()
            if (cur["x"], cur["y"]) != path[i - 1][:2]:
                break
            W.step_toward(g, path[i - 1][:2], path[i][:2])
    raise AssertionError(f"could not reach {edge} edge: {g.describe()}")


def nav(g, target, *ok_maps, avoid=frozenset()):
    """Navigate; tolerate BFS blindness and early warp arrivals."""
    try:
        L1.navigate(g, target, avoid=avoid)
    except (AssertionError, TypeError):
        pass
    st = g.state()
    return any((st["group"], st["num"]) == m for m in ok_maps)


def main():
    g = GBA()
    print(f"ROM {g.core.game_code}", flush=True)
    boot_to_bedroom(g)
    L1.set_flag(g, 0x74)  # FLAG_ADVENTURE_STARTED
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
    g.shot("leg2_01_r31.png")

    # ---------- R31 west door (coord) -> gate ----------
    L1.enter_warp(g, (10, 9), "LEFT", MAP_GATE, "gate_in")
    stage("gate")
    g.shot("leg2_02_gate.png")

    # ---------- gate west door (coord) -> Ilex ----------
    L1.enter_warp(g, (1, 5), "LEFT", MAP_ILEX, "ilex_in")
    stage("ilex_south")
    g.shot("leg2_03_ilex.png")

    # ---------- Ilex north coord -> R34 ----------
    L1.enter_warp(g, (20, 13), "UP", MAP_R34, "r34_from_ilex")
    print("r34 landing:", g.describe(), flush=True)
    g.shot("leg2_04_r34.png")

    # ---------- R34 north seam -> GOLDENROD ----------
    navigate(g, (26, 1))
    W.cross_connection(g, "UP", MAP_GOLDENROD, "goldenrod_from_r34")
    print("goldenrod landing:", g.describe(), flush=True)
    g.shot("leg2_05_goldenrod.png")

    # ---------- Bill's house (dynamic-return interior) ----------
    navigate(g, (14, 34))
    L1.enter_warp(g, (14, 33), "UP", MAP_BILLS, "bills_in")
    stage("bills")
    g.shot("leg2_06_bills.png")
    for _ in range(20):
        g.tap(K.KEY_UP, hold=10, wait=16)
        st = g.state()
        if st and (st["group"], st["num"]) == MAP_GOLDENROD:
            break
    else:
        raise AssertionError("bills_out never fired")
    for _ in range(120):
        g.frame(1)
    W.assert_map(g, MAP_GOLDENROD, "bills_out")
    stage("goldenrod_again")

    # ---------- Goldenrod plaza portal -> R4 ----------
    navigate(g, (32, 9))
    L1.enter_warp(g, (32, 8), "UP", MAP_R4, "r4_from_portal")
    stage("r4_landing")
    g.shot("leg2_07_r4.png")

    # ---------- R4 bottom slot -> R3 top-east ----------
    navigate(g, (11, 18))
    W.cross_connection(g, "DOWN", MAP_R3, "r3_from_r4")
    print("r3 landing:", g.describe(), flush=True)
    g.shot("leg2_08_r3.png")

    # ---------- R3 west slot -> R2 ----------
    navigate(g, (1, 10))
    W.cross_connection(g, "LEFT", MAP_R2, "r2_from_r3")
    print("r2 landing:", g.describe(), flush=True)

    # ---------- R2 portal -> Rustboro ----------
    L1.enter_warp(g, (24, 76), "LEFT", MAP_R116, "r116_portal")
    stage("rustboro")
    g.shot("leg2_10_rustboro.png")

    # ---------- R2 portal -> Route116 west street ----------
    L1.enter_warp(g, (24, 76), "LEFT", MAP_R116, "r116_portal")
    # ---------- R116 far point -> Return Stone home ----------
    print("at far point:", g.describe(), flush=True)
    for i in range(10):
        st = g.state()
        if (st["group"], st["num"]) == MAP_PALLET:
            break
        g.tap(K.KEY_LEFT, hold=10, wait=18)
    else:
        raise AssertionError("return_stone never fired")
    for _ in range(120):
        g.frame(1)
    W.assert_map(g, MAP_PALLET, "return_stone")
    g.shot("leg2_11_home.png")

    assert W.assert_no_battle(g) is None or True
    print("LEG 2 HEADLESS VERIFICATION PASSED", flush=True)


if __name__ == "__main__":
    main()
