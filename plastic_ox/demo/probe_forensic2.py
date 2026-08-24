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
for i in range(500):
    snaps[i % 12] = g.core.save_raw_state()
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
    return f"{syms[j][1]}+{addr-syms[j][0]:#x}" if j >= 0 else "?"

# try rewinds from just-before-death backwards until one reproduces within budget
ring = []
for back in range(1, 8):
    good = snaps[(died - back) % 12]
    g.core.load_raw_state(good)
    ring.clear()
    hit = False
    for step in range(2_000_000):
        cpu = g.core.cpu
        pc = int(cpu.pc)
        lr = int(cpu.lr)
        ring.append((pc, lr))
        if len(ring) > 160:
            ring.pop(0)
        if not sb_ok():
            hit = True
            break
        g.core.step()
    if hit:
        print(f"reproduced from snapshot -{back} at step {step}")
        seen = []
        for pc, lr in ring[-90:]:
            t = f"{sym(pc & ~1)} <- {sym(lr & ~1)}"
            if not seen or seen[-1][0] != t:
                seen.append((t, pc))
        for t, pc in seen[-45:]:
            print(f"  {pc:#010x}  {t}")
        cpu = g.core.cpu
        print(f"final PC={int(cpu.pc):#010x} LR={int(cpu.lr):#010x}")
        break
else:
    print("could not reproduce within budgets")
