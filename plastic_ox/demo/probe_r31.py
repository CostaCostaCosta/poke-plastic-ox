import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import walk_leg1 as L
import walk_demo as W
from walklib import GBA, boot_to_bedroom

g = GBA()
boot_to_bedroom(g)
L.set_flag(g, L.FLAG_ADVENTURE_STARTED)

# replay exactly to the R31 arrival
g.walk("RIGHT", target=(10, 6)); g.walk("UP", target=(10, 2))
for _ in range(3):
    g.hold(W.K.KEY_LEFT, 90)
    if g.state() and (g.state()["group"], g.state()["num"]) == L.MAP_HOUSE_1F:
        break
W.visit_mom(g)
g.walk("RIGHT", target=(10, 3)); g.walk("LEFT", target=(4, 3)); g.walk("DOWN", target=(4, 7))
g.hold(W.K.KEY_DOWN, 80); g.frame(90)
g.walk("DOWN", target=(6, 10)); g.walk("RIGHT", target=(13, 10)); g.walk("UP", target=(13, 2))
g.walk("LEFT", target=(12, 2)); g.walk("UP", target=(12, 0))
W.cross_connection(g, "UP", L.MAP_ROUTE101, "r101_north")
W.walk_to_edge(g, "north")
W.cross_connection(g, "UP", L.MAP_OLDALE, "oldale")
L.navigate(g, (1, 10))
W.cross_connection(g, "LEFT", L.MAP_R29, "r29_east")
L.navigate(g, (38, 4)); L.navigate(g, (38, 0))
W.cross_connection(g, "UP", L.MAP_R46, "r46_south")
L.navigate(g, (20, 12))
L.enter_warp(g, (20, 12), "UP", L.MAP_DARKCAVE, "dc_enter")
L.navigate(g, (14, 19))

# fire the warp manually and watch closely
for _ in range(60):
    g.tap(W.DIRKEY["DOWN"], hold=8, wait=4)
    s = g.state()
    if s and (s["group"], s["num"]) == L.MAP_R31:
        break
print("arrived:", g.describe(), flush=True)
for yy in range(5, 16):
    col = g.collision_at(48, yy); beh = g.behavior_at(48, yy)
    print(f"  tile(48,{yy}) coll={col} beh={beh}", flush=True)
for xx in range(44, 53):
    col = g.collision_at(xx, 9); beh = g.behavior_at(xx, 9)
    print(f"  tile({xx},9) coll={col} beh={beh}", flush=True)
for i in range(1200):
    g.frame(1)
    if i % 15 == 0:
        s = g.state()
        bt = g.u32(g.symbol_address("gBattleTypeFlags"))
        
        print(f"{i:4d} {g.describe()} battle={bt} ", flush=True)
        if s is None:
            print("SAVEBLOCK LOST at frame", i)
