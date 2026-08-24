import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import walk_leg1 as L
import walk_demo as W
from walklib import GBA, boot_to_bedroom

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

# brute-force push west across the seam
for _ in range(400):
    g.hold(W.K.KEY_LEFT, 12)
    st = g.state()
    if st and (st["group"], st["num"]) == L.MAP_CHERRYGROVE:
        break
print("after push:", g.describe(), flush=True)
st = g.state()
assert st and (st["group"], st["num"]) == L.MAP_CHERRYGROVE, "seam to Cherrygrove failed"

L.navigate(g, (52, 1))
W.cross_connection(g, "UP", L.MAP_R30, "r30_south_entry")
L.navigate(g, (32, 1))
W.cross_connection(g, "UP", L.MAP_R31, "r31_south_entry")
print("ON R31 (south approach):", g.describe(), flush=True)

for i in range(2400):
    g.frame(1)
    if i % 400 == 0:
        print(i, g.describe(), flush=True)
        if g.state() is None:
            print("SAVEBLOCK LOST — crashes from south approach too")
            sys.exit(1)
print("STABLE — R31 survives 2400 frames via south approach")
