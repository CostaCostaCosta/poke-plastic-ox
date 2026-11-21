
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from walklib import *

g = GBA()
boot_to_bedroom(g)
g.frame(90)
print("bedroom:", g.describe())
# stairs: RIGHT to (10,6), UP to (10,2), hold LEFT to warp
g.walk('RIGHT', target=(10,6)); g.walk('UP', target=(10,2))
g.hold(K.KEY_LEFT, 90)          # warp to 1F
g.walk('DOWN', target=(10,3))   # move off the stairs so we don't re-warp
g.walk('LEFT', target=(4,3))
g.walk('DOWN', target=(4,7))
print("1F door area:", g.describe())
g.hold(K.KEY_DOWN, 80)          # step onto (4,8) arrow warp + trigger
g.frame(90)
print("outside:", g.describe())

# probe tiles along row 8 and 9 to find the blocker
for y in (7, 8, 9):
    row = []
    for x in range(6, 15):
        try:
            col, elev = g.collision_at(x, y)
            b, mt, blk = g.behavior_at(x, y)
            row.append(f"{x}:c{col}e{elev}b0x{b:02x}")
        except Exception as e:
            row.append(f"{x}:ERR")
    print(f"row {y}:", " | ".join(row))

# now step RIGHT one tile at a time from current position, printing each state
for i in range(10):
    g.hold(K.KEY_RIGHT, 40)
    st = g.state()
    print(f"  step right {i}: {g.describe()}")
    if st and st['x'] >= 12: break
