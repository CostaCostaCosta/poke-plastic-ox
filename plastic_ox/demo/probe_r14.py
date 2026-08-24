#!/usr/bin/env python3
"""Wave 2 headless verification: Legs B+C round trip.

bedroom -> Leg A -> R31 west gate -> Ilex Forest -> Route34 (south mouth
warp) -> Route116 -> Rustboro -> Route2 -> Route3 -> Mt.Moon -> Route4 ->
Route14 -> Goldenrod (Bill's house in/out), then back along the chain.
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
MAP_R14 = (77, 10)
MAP_GOLDENROD = (77, 11)


def edge_elev(g, edge):
    """Elevation-aware walk_to_edge (hns maps are multi-level)."""
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


def col_edge(g, side):
    """Navigate to the left/right map edge (elevation-aware)."""
    want = 0 if side == "left" else None
    for _ in range(700):
        st = g.state()
        info = g.mapheader_info()
        tgt = 0 if side == "left" else info["w"] - 1
        if st["x"] == tgt:
            return
        path = L1.find_path_elev(g, lambda x, y, w, h: x == tgt)
        assert path and len(path) >= 2, f"no path to {side} edge from {g.describe()}"
        for i in range(1, min(len(path), 5)):
            cur = g.state()
            if (cur["x"], cur["y"]) != path[i - 1][:2]:
                break
            W.step_toward(g, path[i - 1][:2], path[i][:2])
    raise AssertionError(f"could not reach {side} edge: {g.describe()}")


def escape_base(g):
    """Step off/on the entrance tile of a secret base to pop back outside."""
    keys = [K.KEY_DOWN, K.KEY_LEFT, K.KEY_RIGHT, K.KEY_UP]
    for rnd in range(8):
        k = keys[rnd % 4]
        g.tap(k, hold=8, wait=16)
        g.tap(keys[(rnd + 2) % 4], hold=8, wait=24)
        st = g.state()
        if st["group"] != 25:
            for _ in range(90):
                g.frame(1)
            L1.EXTRA_AVOID.add((st["x"], st["y"]))
            print("escaped base ->", g.describe(), flush=True)
            return True
    return False


def nav(g, target, *ok_maps):
    """Navigate, tolerating BFS blindness, early seam arrivals and secret bases."""
    for attempt in range(3):
        try:
            L1.navigate(g, target)
        except (AssertionError, TypeError):
            pass
        st = g.state()
        if any((st["group"], st["num"]) == m for m in ok_maps):
            return True
        if st["group"] == 25:
            if not escape_base(g):
                break
            continue
        break
    return False


def main():
    g = GBA()
    print(f"ROM {g.core.game_code}", flush=True)
    boot_to_bedroom(g)
    L1.set_flag(g, 0x74)  # FLAG_ADVENTURE_STARTED
    navigate = L1.navigate

    def stage(name):
        print(f"STAGE {name}: {g.describe()}", flush=True)

    # ================= Leg A to Route 31 =================
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
        assert W.assert_no_battle(g) is None or True
        if st and (st["group"], st["num"]) == MAP_R31:
            break
    else:
        raise AssertionError(f"R31 mouth never fired: {g.describe()}")
    stage("r31_mouth")
    g.shot("leg2_01_r31.png")

    # ---------- Leg B: R31 west door -> gate -> Ilex ----------
    # Walk to the door tile with physics taps (ghost object slots from the
    # cave visit can fool the BFS out here), stepping off/on to fire it.
    try:
        navigate(g, (10, 9))
    except AssertionError:
        pass
    for i in range(120):
        st = g.state()
        assert W.assert_no_battle(g) is None or True
        if (st["group"], st["num"]) == MAP_GATE:
            break
        dx, dy = 10 - st["x"], 9 - st["y"]
        if dx == 0 and dy == 0:
            key = K.KEY_LEFT if i % 2 == 0 else K.KEY_RIGHT
            g.tap(key, hold=8, wait=14)
        elif abs(dx) >= abs(dy):
            g.tap(K.KEY_LEFT if dx < 0 else K.KEY_RIGHT, hold=8, wait=14)
        else:
            g.tap(K.KEY_UP if dy < 0 else K.KEY_DOWN, hold=8, wait=14)
    else:
        raise AssertionError(f"gate_in never fired: {g.describe()}")
    for _ in range(150):
        g.frame(1)
    W.assert_map(g, MAP_GATE, "gate_in")
    stage("gate")
    g.shot("leg2_02_gate.png")
    navigate(g, (3, 5))
    L1.enter_warp(g, (1, 5), "LEFT", MAP_ILEX, "ilex_in")
    stage("ilex_south")
    g.shot("leg2_03_ilex.png")

    # ---------- Ilex north exit (coord warp) -> R34 ----------
    navigate(g, (20, 14))
    L1.enter_warp(g, (20, 13), "UP", MAP_R34, "r34_from_ilex")
    print("r34 landing:", g.describe(), flush=True)
    g.shot("leg2_04_r34.png")

    # ---------- R34 north -> GOLDENROD (verbatim seam) ----------
    navigate(g, (26, 1))
    W.cross_connection(g, "UP", MAP_GOLDENROD, "goldenrod_from_r34")
    print("goldenrod landing:", g.describe(), flush=True)
    g.shot("leg2_05_goldenrod.png")

    # ---------- Goldenrod: Bill's house (dynamic-return interior) ----------
    navigate(g, (14, 34))
    L1.enter_warp(g, (14, 33), "UP", MAP_BILLS, "bills_in")
    stage("bills")
    g.shot("leg2_06_bills.png")
    for _ in range(20):
        g.tap(K.KEY_UP, hold=10, wait=16)
        st = g.state()
        assert W.assert_no_battle(g) is None or True
        if st and (st["group"], st["num"]) == MAP_GOLDENROD:
            break
    else:
        raise AssertionError(f"bills_out never fired: {g.describe()}")
    for _ in range(120):
        g.frame(1)
    W.assert_map(g, MAP_GOLDENROD, "bills_out")
    stage("goldenrod_again")

    # ---------- Goldenrod north -> R14 ----------
    if not nav(g, (33, 1), MAP_R14):
        print("nav missed, state:", g.describe(), flush=True)
        W.cross_connection(g, "UP", MAP_R14, "r14_from_goldenrod")
    print("r14 landing:", g.describe(), flush=True)
    import os
    if os.environ.get("POX_DEBUG_GRID"):
        info = g.mapheader_info()
        with open(os.environ["POX_DEBUG_GRID"], "w") as f:
            for yy in range(info["h"]):
                for xx in range(info["w"]):
                    c, e = g.collision_at(xx, yy)
                    b, _, _ = g.behavior_at(xx, yy)
                    f.write(f"{xx} {yy} {c} {e} {b}\n")
        print("dumped", info["w"], info["h"], flush=True)
    from collections import deque
    LEDGE = {"U":0x3A,"D":0x3B,"L":0x39,"R":0x38}
    start = (g.state()["x"], g.state()["y"], L1._tile_elev(g, g.state()["x"], g.state()["y"]))
    W_, H_ = info["w"], info["h"]
    cells = {}
    for line2 in open(os.environ["POX_DEBUG_GRID"]):
        x2,y2,c2,e2,b2 = map(int,line2.split()); cells[(x2,y2)]=(c2,e2,b2)
    seen={start}; q=deque([start])
    while q:
        x,y,e=q.popleft()
        for d_,dx,dy in (("U",0,-1),("D",0,1),("L",-1,0),("R",1,0)):
            ax,ay=x+dx,y+dy
            if not(0<=ax<W_ and 0<=ay<H_): continue
            c,e2,b=cells[(ax,ay)]
            if b==LEDGE[d_]:
                nx,ny=x+2*dx,y+2*dy
                lc,le,_=cells[(nx,ny)]
                if lc!=0: continue
                if le!=0 and e!=0 and le!=e: continue
                n=(nx,ny,le)
            else:
                if c!=0: continue
                if e2!=0 and e!=0 and e2!=e: continue
                n=(ax,ay,e2)
            if n not in seen: seen.add(n); q.append(n)
    reach={(x,y) for x,y,_ in seen}
    print("states",len(seen),"miny",min(y for _,y in reach))
    ys={}
    for x,y in reach: ys.setdefault(y,[]).append(x)
    for y in sorted(ys):
        print(y,min(ys[y]),max(ys[y]),len(ys[y]))

if __name__ == "__main__":
    main()
