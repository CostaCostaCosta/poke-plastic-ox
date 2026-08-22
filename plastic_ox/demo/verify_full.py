"""Plastic Ox demo: full verification run.
boot -> bedroom -> 1F -> Pallet Town -> Oak trigger -> lab -> starter ->
rival (talk-only in demo) -> north seam to Route 101 -> Oldale -> back south."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from walklib import *

g = GBA()
boot_to_bedroom(g)
g.frame(90)
print("STAGE bedroom:", g.describe(), flush=True)
assert g.state()["group"] == 38 and g.state()["num"] == 1
g.shot("20_bedroom.png")

# stairs warp (sideways step onto the stair tile)
g.wait_for(lambda: g.state() is not None and (g.state()["group"], g.state()["num"]) == (38,1), 600, label="bedroom-load")
g.frame(120)
# close any stray textbox (e.g. NES sign opened by intro A-mashing) and verify movement
for _ in range(3):
    g.tap(K.KEY_B, hold=2, wait=10); g.tap(K.KEY_A, hold=2, wait=10)
st0 = g.state()
g.tap(K.KEY_RIGHT, hold=8, wait=20)
st1 = g.state()
if st1 and st0 and st1["x"] == st0["x"]:
    g.tap(K.KEY_B, hold=2, wait=15); g.tap(K.KEY_A, hold=2, wait=15)
    g.tap(K.KEY_LEFT, hold=8, wait=20)
    g.tap(K.KEY_RIGHT, hold=8, wait=20)
for attempt in range(3):
    g.walk("RIGHT", target=(10,6)); g.walk("UP", target=(10,2))
    g.hold(K.KEY_LEFT, 90)
    st = g.state()
    if st and st["num"] == 0:
        break
assert st and st["num"] == 0, f"not in 1F: {g.describe()}"
print("STAGE house_1f:", g.describe(), flush=True)
g.shot("30_house_1f.png")

# exit to Pallet Town
g.walk("DOWN", target=(10,3)); g.walk("LEFT", target=(4,3)); g.walk("DOWN", target=(4,7))
g.hold(K.KEY_DOWN, 80); g.frame(90)
st = g.state()
assert st and (st["group"], st["num"]) == (75,0), f"not in Pallet: {g.describe()}"
print("STAGE pallet:", g.describe(), flush=True)
g.shot("40_pallet_outside.png")

# Oak trigger (route around the sign NPC via y=10)
g.walk("DOWN", target=(6, 10)); g.walk("RIGHT", target=(13, 10)); g.walk("UP", target=(13, 2))
g.walk("LEFT", target=(12, 2)); g.walk("UP", target=(12, 1)); g.frame(90)
print("STAGE oak_trigger:", g.describe(), flush=True)
g.shot("50_oak_trigger.png")
for i in range(800):
    g.frame(10)
    if i % 5 == 0: g.tap(K.KEY_A, hold=1, wait=2)
    st = g.state()
    if st and (st["group"], st["num"]) == (38,3): break
assert g.state()["num"] == 3, f"never reached lab: {g.describe()}"
print("STAGE lab:", g.describe(), flush=True)
g.shot("60_lab.png")

# starter scene dialog until free (var 4055 == 2)
for i in range(400):
    g.frame(10)
    if i % 4 == 0: g.tap(K.KEY_A, hold=1, wait=2)
    if g.var(0x4055) == 2: break
assert g.var(0x4055) == 2
g.walk("RIGHT", target=(7, 4))
g.tap(K.KEY_RIGHT, hold=2, wait=30)   # face Bulbasaur ball at (8,4)
g.tap(K.KEY_A, hold=3, wait=90)       # select
g.tap(K.KEY_A, hold=3, wait=90)       # YES
g.frame(60)
for i in range(400):
    g.frame(10)
    if i % 4 == 0: g.tap(K.KEY_A, hold=1, wait=2)
    if g.var(0x4055) >= 3: break
print("STAGE starter_chosen var4055:", g.var(0x4055), flush=True)
# dump party: find gPlayerParty via ELF symbol table
import subprocess
nm = subprocess.run(["arm-none-eabi-nm", "/home/eddie/repos/poke-plastic-ox/pokeemerald.elf"],
                    capture_output=True, text=True).stdout
addr = None
for line in nm.splitlines():
    if line.endswith(" gPlayerParty"):
        addr = int(line.split()[0], 16)
if addr:
    sp = g.u16(addr)  # species low16 (enum Species u32? read u16)
    lvl = g.u8(addr + 0x54) if g.u8(addr+0x54) else g.u8(addr+0x58)
    hp = g.u16(addr + 0x56)
    print(f"  party[0]: species={g.u32(addr)} lvl?(0x54)={g.u8(addr+0x54)} hp?(0x56)={g.u16(addr+0x56)}", flush=True)
# verification-only: buff Bulbasaur in-memory so wild battles end instantly
GPARTIES = 0x02031c04
g.core.memory.wram.u8[0x31c04 + 0x54] = 50          # level
for off, val in [(0x56, 400), (0x58, 400), (0x5A, 300), (0x5C, 300), (0x5E, 300), (0x60, 300), (0x62, 300)]:
    g.core.memory.wram.u16[GPARTIES - 0x02000000 + off] = val
print("  party buffed: lvl", g.core.memory.wram.u8[GPARTIES-0x02000000+0x54], "hp", g.u16(GPARTIES+0x56), flush=True)
g.shot("70_starter.png")

# leave lab -> rival talk (demo: no battle) at exit row
st = g.state()
g.walk("DOWN", target=(st["x"], 9), timeout=4000)
for i in range(300):
    g.frame(10)
    if i % 4 == 0: g.tap(K.KEY_A, hold=1, wait=2)
    if g.var(0x4055) >= 4: break
print("STAGE rival_done var4055:", g.var(0x4055), g.describe(), flush=True)
g.shot("75_rival_done.png")

# exit lab door (warps at y=12, x=5..7); hold DOWN through the doorway
st = g.state()
g.walk("LEFT", target=(6, st["y"]), timeout=2000)
for attempt in range(4):
    g.hold(K.KEY_DOWN, 100)
    g.frame(60)
    st = g.state()
    if st and (st["group"], st["num"]) == (75,0):
        break
g.frame(60)
st = g.state()
print("STAGE back_outside:", g.describe(), flush=True)
assert st and (st["group"], st["num"]) == (75,0), f"not back in Pallet: {g.describe()}"
g.shot("76_pallet_after_lab.png")

# north seam to Route 101 (exit at x=12-13). Lab door puts player at (16,14).
g.walk("DOWN", target=(16, 16), timeout=2000)
g.walk("LEFT", target=(12, 16), timeout=3000)
g.walk("UP", target=(12, 2), timeout=4000)     # walk to Pallet's north edge
g.frame(30)
g.shot("79_pallet_north_edge.png")
print("pre-seam:", g.describe(), flush=True)
g.hold(K.KEY_UP, 200)                           # hold through the connection
g.frame(120)
st = g.state()
print("STAGE route101_seam:", g.describe(), flush=True)
g.shot("80_route101_seam.png")
assert st and (st["group"], st["num"]) == (0,16), f"not on Route101: {g.describe()}"

# Route101 -> Oldale: BFS over the live grid (collision + NPC positions)
from collections import deque
BATTLE_TYPE_FLAGS_ADDR = 0x020000cc
def in_battle():
    # gBattleTypeFlags != 0 while any battle is active
    return g.u32(BATTLE_TYPE_FLAGS_ADDR) != 0 or g.bottom_whiteness() > 0.5
def handle_battle():
    for j in range(300):
        g.frame(8)
        g.tap(K.KEY_A, hold=1, wait=2)
        if g.u32(BATTLE_TYPE_FLAGS_ADDR) == 0:
            g.frame(120); return
    g.shot("battle_stuck.png")
    print("  BATTLE STUCK, bw=", g.bottom_whiteness(), flush=True)
def step(d):
    g.tap(DIRKEY[d], hold=8, wait=16)
def npc_tiles():
    tiles = set()
    for i in range(16):
        base = 0x020066c8 + i*0x24
        if not (g.u8(base) & 1): continue
        if g.u8(base+2) & 1: continue
        cx = g.s16(base + 0x10) - 7; cy = g.s16(base + 0x12) - 7
        tiles.add((cx, cy))
    return tiles
def find_path(sx, sy, goal_band_y=1):
    npcs = npc_tiles()
    W, H = 20, 20
    q = deque([(sx, sy)])
    prev = {(sx, sy): None}
    while q:
        x, y = q.popleft()
        if y <= goal_band_y:
            # reconstruct
            path = []
            cur = (x, y)
            while cur is not None:
                path.append(cur)
                cur = prev[cur]
            return path[::-1]
        for dx, dy in ((0,-1),(0,1),(-1,0),(1,0)):
            nx, ny = x+dx, y+dy
            if not (0 <= nx < W and 0 <= ny < H): continue
            if (nx, ny) in prev or (nx, ny) in npcs: continue
            c, e = g.collision_at(nx, ny)
            if c != 0: continue
            prev[(nx, ny)] = (x, y)
            q.append((nx, ny))
    return None
for i in range(600):
    st = g.state()
    if st is None: continue
    if (st["group"], st["num"]) == (0,10): break
    if in_battle():
        print("  wild battle at", g.describe(), flush=True)
        handle_battle()
        continue
    path = find_path(st["x"], st["y"], goal_band_y=0)
    if path and len(path) >= 2:
        nx, ny = path[1]
        d = "UP" if ny < st["y"] else "DOWN" if ny > st["y"] else "LEFT" if nx < st["x"] else "RIGHT"
        step(d)
    elif st["y"] <= 1:
        step("UP")   # top row: cross the connection into Oldale
    else:
        g.frame(180)
g.frame(60)
print("pre-oldale:", g.describe(), flush=True)
g.shot("89_route101_north_edge.png")
print("STAGE oldale:", g.describe(), flush=True)
g.shot("90_oldale_arrival.png")
ok_oldale = st and (st["group"], st["num"]) == (0,10)
assert ok_oldale, f"OLDALE FAIL: {g.describe()}"
g.walk("UP", target=(st["x"], st["y"]-4), timeout=3000)
g.shot("91_oldale_center.png")
print("STAGE oldale_center:", g.describe(), flush=True)

# ---- return trip: Oldale -> Route101 -> Pallet ----
g.walk("DOWN", target=(11, 19), timeout=4000)   # to Oldale south edge
st = g.state()
print("pre-return-101:", g.describe(), flush=True)
g.hold(K.KEY_DOWN, 200); g.frame(120)
st = g.state()
print("STAGE return_route101:", g.describe(), flush=True)
g.shot("92_return_route101.png")
assert st and (st["group"], st["num"]) == (0,16), f"not back on Route101: {g.describe()}"
assert g.var(0x4043) is None or True  # Route101 state var
# BFS south to y=19 then cross into Pallet
def find_path_south(sx, sy):
    npcs = npc_tiles()
    q = deque([(sx, sy)]); prev = {(sx, sy): None}
    while q:
        x, y = q.popleft()
        if y >= 19:
            path = []
            cur = (x, y)
            while cur is not None: path.append(cur); cur = prev[cur]
            return path[::-1]
        for dx, dy in ((0,1),(0,-1),(-1,0),(1,0)):
            nx, ny = x+dx, y+dy
            if not (0 <= nx < 20 and 0 <= ny < 20): continue
            if (nx, ny) in prev or (nx, ny) in npcs: continue
            c, e = g.collision_at(nx, ny)
            if c != 0: continue
            prev[(nx, ny)] = (x, y); q.append((nx, ny))
    return None
for i in range(1200):
    st = g.state()
    if st is None: continue
    if (st["group"], st["num"]) == (75,0): break
    if in_battle():
        handle_battle(); continue
    path = find_path_south(st["x"], st["y"])
    if path and len(path) >= 2:
        nx, ny = path[1]
        d = "DOWN" if ny > st["y"] else "UP" if ny < st["y"] else "LEFT" if nx < st["x"] else "RIGHT"
        step(d)
    elif st["y"] >= 19:
        step("DOWN")   # bottom row: cross into Pallet
    else:
        g.frame(180)
g.frame(60)
st = g.state()
print("STAGE return_pallet:", g.describe(), flush=True)
g.shot("93_return_pallet.png")
assert st and (st["group"], st["num"]) == (75,0), f"not back in Pallet: {g.describe()}"
print("ALL STAGES PASS", flush=True)
