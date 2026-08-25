#!/usr/bin/env python3
"""Does a warp-first coord fire on the lab map? Step onto (9,11)."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import walk_demo as W
import walk_leg1 as L1
from walklib import GBA, K, boot_to_bedroom

MAP_LAB = (38, 3)
g = GBA()
boot_to_bedroom(g)
L1.set_flag(g, 0x74)
g.walk("RIGHT", target=(10, 6)); g.walk("UP", target=(10, 2))
for i in range(3):
    g.hold(K.KEY_LEFT, 90)
    if (g.state()["group"], g.state()["num"]) == (38, 0):
        break
W.visit_mom(g)
g.walk("RIGHT", target=(10, 3)); g.walk("LEFT", target=(4, 3)); g.walk("DOWN", target=(4, 7))
g.hold(K.KEY_DOWN, 80); g.frame(90)
assert (g.state()["group"], g.state()["num"]) == W.MAP_PALLET, g.describe()
g.walk("DOWN", target=(6, 14))
g.walk("RIGHT", target=(15, 14))
for i in range(10):
    st = g.state()
    if (st["group"], st["num"]) == MAP_LAB:
        break
    if st["y"] < 14:
        g.tap(K.KEY_DOWN, hold=10, wait=16)
    elif st["x"] < 16:
        g.tap(K.KEY_RIGHT, hold=10, wait=16)
    else:
        g.tap(K.KEY_UP, hold=10, wait=20)
for _ in range(120):
    g.frame(1)
W.assert_map(g, MAP_LAB, "lab_in")
print("in lab:", g.describe(), flush=True)

# spawn is ON the door row; step UP first, then east along row 11
def flag264():
    save_ptr_addr = g.symbol_address("gSaveBlock1Ptr")
    s1 = g.core.memory.iwram.u32[save_ptr_addr - 0x03000000]
    base = s1 - 0x02000000
    b = g.core.memory.wram.u8[base + 0x1270 + 0x264 // 8]
    return bool(b & (1 << (0x264 % 8)))

for i in range(30):
    st = g.state()
    if flag264():
        print(f"STARTER FLAG SET after {i} steps; player at {g.describe()}", flush=True)
        break
    if (st["group"], st["num"]) != (38, 3):
        print("left lab:", g.describe(), flush=True)
        break
    dx, dy = 9 - st["x"], 11 - st["y"]
    if dy < 0:
        g.tap(K.KEY_UP, hold=10, wait=16)
    elif dx > 0:
        g.tap(K.KEY_RIGHT, hold=10, wait=16)
    else:
        g.tap(K.KEY_UP, hold=8, wait=14)
else:
    print("flag never set; stuck at", g.describe(), flush=True)

if __name__ == "__main__":
    pass
