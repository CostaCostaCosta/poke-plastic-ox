
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from walklib import *

g = GBA()
boot_to_bedroom(g)
g.frame(90)
g.walk('RIGHT', target=(10,6)); g.walk('UP', target=(10,2))
g.hold(K.KEY_LEFT, 90)          # warp to 1F
g.walk('DOWN', target=(10,3))
g.walk('LEFT', target=(4,3))
g.walk('DOWN', target=(4,7))
g.hold(K.KEY_DOWN, 80)          # step onto arrow door + warp
g.frame(90)
print("outside:", g.describe())

# route around Oak at (10,8)
st = g.state()
g.walk('DOWN', target=(st['x'], 9))
g.walk('RIGHT', target=(12, 9))
g.walk('UP', target=(12, 7))
g.walk('LEFT', target=(11, 7))
g.walk('UP', target=(11, 2))
g.walk('RIGHT', target=(12, 2))
g.walk('UP', target=(12, 1))
print("after route:", g.describe())
g.frame(60)
print("post-trigger wait:", g.describe())
g.shot("14_oak_trigger.png")
# A-mash through the Oak cutscene text / auto-walk to the lab
for i in range(600):
    g.frame(12)
    g.tap(K.KEY_A, hold=2, wait=3)
    st = g.state()
    if i % 120 == 0:
        print(f"  cutscene i={i}: {g.describe()}")
    if st is not None and (st['group'], st['num']) == (38,3):
        print(f"IN OAK LAB at i={i}: {g.describe()}")
        break
g.frame(120)
print("lab:", g.describe())
g.shot("15_oak_lab.png")
print("lab header:", g.mapheader_info())
# probe lab starter area tiles
for xy in [(8,4),(9,4),(10,4),(5,4),(11,4),(9,5),(9,3),(12,5)]:
    try:
        b, mt, blk = g.behavior_at(*xy)
        print(f"  lab tile {xy}: behavior=0x{b:02x} mt={mt}")
    except Exception as e:
        print(f"  lab tile {xy}: ERR {e}")
