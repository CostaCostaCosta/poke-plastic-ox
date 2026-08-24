import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import walk_leg1 as L
import walk_demo as W
from walklib import GBA, boot_to_bedroom

ROM_BASE = 0x08000000

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
L.navigate(g, (38, 4)); L.navigate(g, (38, 0))
W.cross_connection(g, "UP", L.MAP_R46, "r46_south")
L.navigate(g, (20, 12))
L.enter_warp(g, (20, 12), "UP", L.MAP_DARKCAVE, "dc_enter")
L.navigate(g, (14, 19))
for _ in range(60):
    g.tap(W.DIRKEY["DOWN"], hold=8, wait=4)
    s = g.state()
    if s and (s["group"], s["num"]) == L.MAP_R31:
        break
print("arrived:", g.describe(), flush=True)

sb = g.symbol_address("gSaveBlock1Ptr")
prev = None
for i in range(400):
    g.frame(1)
    pc = g.core.cpu.pc
    if not (ROM_BASE <= pc < ROM_BASE + 0x2000000):
        print(f"PC ESCAPED ROM at frame {i}: pc={pc:#010x} lr={g.core.cpu.lr:#010x}")
        print("gprs:", [f"r{n}={v:#010x}" for n, v in enumerate(g.core.cpu.gprs)])
        break
    if i % 25 == 0:
        print(i, hex(pc), g.describe(), flush=True)
