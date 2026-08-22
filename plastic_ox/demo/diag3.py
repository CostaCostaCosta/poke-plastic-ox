
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from walklib import *

g = GBA()
boot_to_bedroom(g)
g.frame(90)
g.walk('RIGHT', target=(10,6)); g.walk('UP', target=(10,2))
g.hold(K.KEY_LEFT, 90)
g.walk('DOWN', target=(10,3)); g.walk('LEFT', target=(4,3)); g.walk('DOWN', target=(4,7))
g.hold(K.KEY_DOWN, 80)
g.frame(90)
st = g.state()
g.walk('DOWN', target=(st['x'], 9)); g.walk('RIGHT', target=(12, 9)); g.walk('UP', target=(12, 7))
g.walk('LEFT', target=(11, 7)); g.walk('UP', target=(11, 2)); g.walk('RIGHT', target=(12, 2))
g.walk('UP', target=(12, 1))
for i in range(1200):
    g.frame(10)
    st = g.state()
    if st is not None and (st['group'], st['num']) == (38,3) and g.var(0x4055) == 2:
        break
    if i % 6 == 0:
        g.tap(K.KEY_A, hold=1, wait=2)
g.frame(60)
st = g.state()
g.walk('DOWN', target=(st['x'], 6)); g.walk('RIGHT', target=(10, 6)); g.walk('UP', target=(10, 5))
g.hold(K.KEY_UP, 12); g.frame(5)
g.tap(K.KEY_A, hold=2, wait=30); g.tap(K.KEY_A, hold=2, wait=40); g.tap(K.KEY_B, hold=2, wait=40)
for i in range(600):
    g.frame(12)
    if i % 5 == 0:
        g.tap(K.KEY_A, hold=1, wait=2)
    if g.var(0x4055) == 3:
        break
g.frame(60)
g.setvar(0x4055, 4)
g.frame(30)
g.walk('DOWN', target=(10, 7)); g.walk('LEFT', target=(7, 7)); g.walk('DOWN', target=(7, 12))
g.set_block_metatile(6, 12, 19)
g.walk('LEFT', target=(6, 12)); g.hold(K.KEY_DOWN, 90); g.frame(120)
print("back in Pallet:", g.describe())
# north to Route 101 via known route
st = g.state()
g.walk('LEFT', target=(13, st['y']))
g.walk('UP', target=(13, 8)); g.walk('LEFT', target=(12, 8)); g.walk('UP', target=(12, 7))
g.walk('LEFT', target=(11, 7)); g.walk('UP', target=(11, 2)); g.walk('RIGHT', target=(12, 2))
g.walk('UP', target=(12, -2), timeout=8000)
print("Route 101 entry:", g.describe())
# zigzag to (7,7)
g.walk('DOWN', target=(10, 15)); g.walk('LEFT', target=(6, 15)); g.walk('UP', target=(6, 8))
g.walk('RIGHT', target=(10, 8)); g.walk('UP', target=(10, 7)); g.walk('LEFT', target=(7, 7))
print("at (7,7):", g.describe())
# probe the way north
for xy in [(7,6),(7,5),(7,4),(7,3),(8,6),(6,6),(7,7)]:
    try:
        col, elev = g.collision_at(*xy)
        b, mt, blk = g.behavior_at(*xy)
        print(f"  tile {xy}: col={col} elev={elev} mt={mt} beh=0x{b:02x}")
    except Exception as e:
        print(f"  tile {xy}: ERR {e}")
# objects
for i in range(16):
    o = 0x020066c8 + i*0x24
    local = g.u8(o+8)
    x = g.s16(o+0x10); y = g.s16(o+0x12)
    if local != 255 and local != 0:
        print(f"  obj {i}: local={local} pos=({x},{y})")
# try stepping up slowly
g.core.set_keys(K.KEY_UP)
for i in range(40):
    g.frame(12)
    st = g.state()
    if st and st['y'] < 7:
        print(f"  MOVED UP to ({st['x']},{st['y']}) at step {i}")
        break
else:
    print("  STILL STUCK after 480f of UP")
g.core.clear_keys(K.KEY_UP)
