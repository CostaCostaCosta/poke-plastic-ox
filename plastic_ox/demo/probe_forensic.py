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

def sb_ok():
    v = g.core.memory.iwram.u32[sb - 0x03000000]
    return 0x02000000 <= v < 0x02040000

snaps = {}
died = None
for i in range(400):
    snaps[i % 8] = g.core.save_raw_state()
    g.frame(1)
    if not sb_ok():
        died = i
        break
print("died after", died, "frames", flush=True)

import re, bisect
syms = []
for line in open("/home/eddie/repos/poke-plastic-ox/pokeemerald.map", errors="ignore"):
    m = re.match(r"\s*0x(0[0-9a-f]{7})\s+(\S+)", line)
    if m:
        syms.append((int(m.group(1), 16), m.group(2)))
syms.sort(); addrs = [a for a, _ in syms]
def sym(addr):
    j = bisect.bisect_right(addrs, addr) - 1
    return f"{syms[j][1]} +{addr-syms[j][0]:#x}" if j >= 0 else "?"


good = snaps[(died - 2) % 8]
g.core.load_raw_state(good)
print("rewound; logging supervisor-mode BIOS entries...", flush=True)
seen = {}
last = []
for step in range(4_000_000):
    cpu = g.core.cpu
    pc = int(cpu.pc)
    if pc < 0x00004000 and (int(cpu.cpsr.packed) & 0x1f) == 0x12:
        lr = int(cpu.lr) & ~1
        key = lr
        seen[key] = seen.get(key, 0) + 1
        last.append((step, pc, lr))
        if len(last) > 400:
            last.pop(0)
    g.core.step()

print("unique SWI return sites:", len(seen))
import bisect
def sym(addr):
    j = bisect.bisect_right(addrs, addr) - 1
    return f"{syms[j][1]} +{addr-syms[j][0]:#x}" if j >= 0 else "?"
for (st, pc, lr) in last[-25:]:
    print(f"step {st} pc={pc:#06x} ret={lr:#010x} {sym(lr)}")
