import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import walk_leg1 as L
import walk_demo as W
from walklib import GBA, boot_to_bedroom

MODE = sys.argv[1] if len(sys.argv) > 1 else "r31_from_r30"

g = GBA()
boot_to_bedroom(g)
L.set_flag(g, L.FLAG_ADVENTURE_STARTED)

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

if MODE == "r29_idle":
    print("idling on R29...", flush=True)
    for i in range(2400):
        g.frame(1)
        if i % 300 == 0:
            s = g.state()
            print(i, g.describe(), flush=True)
            if s is None:
                print("SAVEBLOCK LOST"); break
    print("done", flush=True); sys.exit(0)

# R29 -> west edge -> Cherrygrove
tgt=None
for yy in range(4, 28):
    try:
        L.navigate(g, (1, yy)); tgt=(1,yy); break
    except AssertionError:
        continue
assert tgt, "no west-edge tile reachable"
print("west-edge at", tgt, flush=True)
W.cross_connection(g, "LEFT", L.MAP_CHERRYGROVE, "cherry_entry")
print("cherrygrove:", g.describe(), flush=True)

if MODE == "cherry_idle":
    for i in range(2400):
        g.frame(1)
        if i % 300 == 0:
            s = g.state()
            print(i, g.describe(), flush=True)
            if s is None:
                print("SAVEBLOCK LOST"); break
    print("done", flush=True); sys.exit(0)

# north door to R30: find R30 entry — Cherrygrove top edge near x=?
L.navigate(g, (52, 1))
W.cross_connection(g, "UP", L.MAP_R30, "r30_south_entry")
print("r30:", g.describe(), flush=True)
L.navigate(g, (32, 1))
W.cross_connection(g, "UP", L.MAP_R31, "r31_south_entry")
print("r31:", g.describe(), flush=True)

for i in range(2400):
    g.frame(1)
    if i % 300 == 0:
        s = g.state()
        print(i, g.describe(), flush=True)
        if s is None:
            print("SAVEBLOCK LOST on R31 via R30 route"); break
print("done", flush=True)
