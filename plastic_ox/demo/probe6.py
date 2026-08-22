
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from walklib import *
import struct

MOVE_LIST_HANDLER = 0x0805c949
FIGHT_MENU_HANDLER = 0x0805d901
G_BATTLE_MONS = 0x020004e8
B_OUTCOME = 0x0200014c
G_MOVE_SEL_CURSOR = 0x02000348
G_CHOSEN_MOVE = 0x0200025c

def mon_stats(g, off):
    base = G_BATTLE_MONS + off
    raw = bytes(g.u8(base+i) for i in range(0x30))
    sp = g.u16(base)  # low16 of species u32
    # try offsets common to this expansion: lvl u8 somewhere, hp/maxHP u16
    return dict(species=sp, raw0=raw[:16].hex(), raw16=raw[16:32].hex(), raw32=raw[32:48].hex())
def run_winning_battle(g, attack_slot=0, max_frames=40000):
    frames = 0
    detects = 0
    idle = 0
    turns = 0
    last_turn_state = None
    while frames < max_frames:
        f0 = g.u32(0x030023fc)
        if f0 == MOVE_LIST_HANDLER:
            detects += 1
            cur = g.u8(G_MOVE_SEL_CURSOR)
            if turns == 0:
                raw = bytes(g.u8(G_BATTLE_MONS+i) for i in range(0x230))
                # find candidate mon starts: scan for plausible species u32 low16 values
                for i in range(0, 0x230, 2):
                    v = struct.unpack('<H', raw[i:i+2])[0]
                    if v in (1,4,7) and i < 0x100:
                        print(f"    species marker {v} at off 0x{i:03x}")
                print(f"    P+0 raw:{raw[0:64].hex()}")
                print(f"    +0x64 raw:{raw[0x64:0x64+48].hex()}")
                print(f"    +0x8C raw:{raw[0x8C:0x8C+48].hex()}")
                print(f"    +0x10  raw:{raw[0x10:0x10+48].hex()}")
                print(f"    +0x118 raw:{raw[0x118:0x118+48].hex()}")
            print(f"    turn {turns}: cur={cur}")
            turns += 1
            if cur == attack_slot:
                g.tap(K.KEY_A, hold=1, wait=2)
            elif attack_slot == 2 and cur == 0:
                g.tap(K.KEY_DOWN, hold=1, wait=2); g.frame(1); g.tap(K.KEY_A, hold=1, wait=2)
            elif attack_slot == 0 and cur == 2:
                g.tap(K.KEY_UP, hold=1, wait=2); g.frame(1); g.tap(K.KEY_A, hold=1, wait=2)
            else:
                g.tap(K.KEY_A, hold=1, wait=2)
            frames += 8
            idle = 0
        elif f0 == FIGHT_MENU_HANDLER:
            g.tap(K.KEY_A, hold=1, wait=2)
            frames += 5
            idle = 0
        elif g.bottom_whiteness() > 0.35:
            g.tap(K.KEY_A, hold=1, wait=2)
            frames += 5
            idle = 0
        else:
            g.frame(2)
            frames += 2
            idle += 2
            if idle >= 900:
                g.tap(K.KEY_A, hold=1, wait=2)
                frames += 5
                idle = 0
        if g.u16(B_OUTCOME) == 1:
            print(f"  WON at frames={frames} detects={detects}")
            return True
        if g.u16(B_OUTCOME) == 2:
            print(f"  LOST at frames={frames} detects={detects}")
            return False
        if frames % 8000 == 0:
            print(f"  battle frames={frames}: outcome={g.u16(B_OUTCOME)}")
    print("  battle timeout")
    return None

def walk_battle_aware(g, direction, target, timeout=6000):
    key = DIRKEY[direction]
    frames = 0
    last_pos = None
    stuck = 0
    while frames < timeout:
        st = g.state()
        pos = (st['x'], st['y']) if st else None
        if st is not None:
            x, y = st['x'], st['y']
            if direction == 'RIGHT' and x >= target[0]: break
            if direction == 'LEFT' and x <= target[0]: break
            if direction == 'DOWN' and y >= target[1]: break
            if direction == 'UP' and y <= target[1]: break
        if pos != last_pos:
            stuck = 0
            last_pos = pos
        else:
            stuck += 1
        g.core.set_keys(key)
        g.frame(2)
        frames += 2
        if stuck > 300:
            g.core.clear_keys(key)
            print(f"    stall at {pos}; battle-mash...")
            run_battle_mash(g, attack_slot=0)
            stuck = 0
            last_pos = None
    g.core.clear_keys(key)
    g.frame(8)
    return g.describe()

def run_battle_mash(g, attack_slot=0, max_frames=15000):
    frames = 0
    idle = 0
    while frames < max_frames:
        f0 = g.u32(0x030023fc)
        if f0 == MOVE_LIST_HANDLER:
            cur = g.u8(G_MOVE_SEL_CURSOR)
            if cur == attack_slot:
                g.tap(K.KEY_A, hold=1, wait=2)
            elif attack_slot == 0 and cur == 2:
                g.tap(K.KEY_UP, hold=1, wait=2); g.frame(1); g.tap(K.KEY_A, hold=1, wait=2)
            else:
                g.tap(K.KEY_A, hold=1, wait=2)
            frames += 8
            idle = 0
        elif g.bottom_whiteness() > 0.35 or f0 == FIGHT_MENU_HANDLER:
            g.tap(K.KEY_A, hold=1, wait=2)
            frames += 5
            idle = 0
        else:
            g.frame(2)
            frames += 2
            idle += 2
            if idle >= 900:
                g.tap(K.KEY_A, hold=1, wait=2)
                frames += 5
                idle = 0
        if g.u16(B_OUTCOME) in (1, 2, 4):
            print(f"   battle over: outcome={g.u16(B_OUTCOME)}")
            return
    print("   battle mash timeout")

g = GBA()
boot_to_bedroom(g)
g.frame(90)
print("1. bedroom:", g.describe())
g.shot("20_bedroom.png")
g.walk('RIGHT', target=(10,6)); g.walk('UP', target=(10,2))
g.hold(K.KEY_LEFT, 90)          # DOWN_LEFT_STAIR_WARP -> hold LEFT
print("2. 1F:", g.describe())
g.shot("21_house_1f.png")
g.walk('DOWN', target=(10,3))
g.walk('LEFT', target=(4,3))
g.walk('DOWN', target=(4,7))
g.hold(K.KEY_DOWN, 80)          # SOUTH_ARROW_WARP door
g.frame(90)
print("3. pallet town:", g.describe())
g.shot("22_pallet_town.png")
st = g.state()
g.walk('DOWN', target=(st['x'], 9))
g.walk('RIGHT', target=(12, 9))
g.walk('UP', target=(12, 7))
g.walk('LEFT', target=(11, 7))
g.walk('UP', target=(11, 2))
g.walk('RIGHT', target=(12, 2))
g.walk('UP', target=(12, 1))
# Oak cutscene
for i in range(1200):
    g.frame(10)
    st = g.state()
    if st is not None and (st['group'], st['num']) == (38,3) and g.var(0x4055) == 2:
        break
    if i % 6 == 0:
        g.tap(K.KEY_A, hold=1, wait=2)
g.frame(60)
print("4. in lab:", g.describe(), "var_lab:", g.var(0x4055))
# choose Charmander ball at (10,4) from (10,5)
st = g.state()
g.walk('DOWN', target=(st['x'], 6))
g.walk('RIGHT', target=(10, 6))
g.walk('UP', target=(10, 5))
g.hold(K.KEY_UP, 12)
g.frame(5)
g.tap(K.KEY_A, hold=2, wait=30)
g.tap(K.KEY_A, hold=2, wait=40)
g.tap(K.KEY_B, hold=2, wait=40)
for i in range(600):
    g.frame(12)
    if i % 5 == 0:
        g.tap(K.KEY_A, hold=1, wait=2)
    if g.var(0x4055) == 3:
        print("   rival took his ball; var_lab=3 at i=", i)
        break
g.frame(60)
print("5. starter chosen (Charmander), var_lab:", g.var(0x4055), "starter_mon:", g.var(0x4023))
print("   BUG WORKAROUND: rival battle loads a Surskit (broken trainer data); skipping via var_lab=4")
g.setvar(0x4055, 4)   # skip broken rival battle
g.frame(30)
print("   after skip: var_lab =", g.var(0x4055))
# walk to the lab exit door: DOWN->(10,7), LEFT->(7,7), DOWN->(7,12)
g.walk('DOWN', target=(10, 7))
g.walk('LEFT', target=(7, 7))
g.walk('DOWN', target=(7, 12))
print("6. at lab exit:", g.describe())
# the exit warps at (5,12),(6,12),(7,12): check behavior of (7,12)/(6,12)
for xy in [(7,12),(6,12),(5,12)]:
    try:
        b, mt, blk = g.behavior_at(*xy)
        print(f"   exit tile {xy}: behavior=0x{b:02x} mt={mt}")
    except Exception as e:
        print(f"   exit tile {xy}: ERR {e}")
print("mapheader:", g.mapheader_info())
# WORKAROUND for broken door behaviors: repoint the tile at (6,12) to metatile 19
# (SOUTH_ARROW_WARP 0x65, same tileset) -> press DOWN to warp out
g.set_block_metatile(6, 12, 19)
print("   patched (6,12) block -> mt19:", g.behavior_at(6,12))
# move the player onto (6,12)
g.walk('LEFT', target=(6, 12))
print("7. on patched door tile:", g.describe())
g.hold(K.KEY_DOWN, 90)
g.frame(120)
print("8. after DOWN:", g.describe())
g.shot("23_back_in_pallet.png")

# NORTH SEAM: walk to x=12/13, then UP past the map border into Route 101
st = g.state()
print("at pallet, pos:", st['x'], st['y'])
# from (16,14), go LEFT to x=13, then UP all the way (through y=0 and the border)
g.walk('LEFT', target=(13, st['y']))
g.walk('UP', target=(13, 8))
g.walk('LEFT', target=(12, 8))
g.walk('UP', target=(12, 7))
g.walk('LEFT', target=(11, 7))
g.walk('UP', target=(11, 2))
g.walk('RIGHT', target=(12, 2))
g.walk('UP', target=(12, -2), timeout=8000)
print("after north walk:", g.describe())
g.frame(60)
print("post-walk wait:", g.describe())
g.shot("24_pallet_north_seam.png")
print("in Route 101 at:", g.describe())

print("in Route 101 at:", g.describe())
g.shot("25_route101_entry.png")

# zigzag path north through Route 101 (straight N blocked at several rows)
segments = [
    ('DOWN', (10, 15)),
    ('LEFT', (6, 15)),
    ('UP', (6, 8)),
    ('RIGHT', (10, 8)),
    ('UP', (10, 7)),
    ('LEFT', (7, 7)),
    ('UP', (7, 2)),
    ('RIGHT', (10, 2)),
]
for (d, tgt) in segments:
    st = g.state()
    print(f"  walk {d} from {st['x']},{st['y']} toward {tgt}...")
    walk_battle_aware(g, d, tgt)
    print(f"    -> {g.describe()}")
# north seam into Oldale
walk_battle_aware(g, 'UP', (10, -2), timeout=8000)
print("north exit result:", g.describe())
g.frame(120)
print("arrival:", g.describe())
if g.state() is not None and (g.state()['group'], g.state()['num']) == (0, 10):
    g.shot("26_oldale_arrival.png")
    # walk into the town center
    st = g.state()
    walk_battle_aware(g, 'DOWN', (st['x'], st['y'] + 3), timeout=3000)
    print("oldale center:", g.describe())
    g.shot("27_oldale_center.png")
else:
    print("DID NOT REACH OLDALE, at:", g.describe())
