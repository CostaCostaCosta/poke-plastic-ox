
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from walklib import *

g = GBA()
boot_to_bedroom(g)
g.frame(90)
g.walk('RIGHT', target=(10,6)); g.walk('UP', target=(10,2))
g.hold(K.KEY_LEFT, 90)
g.walk('DOWN', target=(10,3))
g.walk('LEFT', target=(4,3))
g.walk('DOWN', target=(4,7))
g.hold(K.KEY_DOWN, 80)
g.frame(90)
st = g.state()
g.walk('DOWN', target=(st['x'], 9))
g.walk('RIGHT', target=(12, 9))
g.walk('UP', target=(12, 7))
g.walk('LEFT', target=(11, 7))
g.walk('UP', target=(11, 2))
g.walk('RIGHT', target=(12, 2))
g.walk('UP', target=(12, 1))
print("at trigger:", g.describe())
# A-mash the Oak cutscene; wait until in-lab scene completes and player is free
for i in range(1200):
    g.frame(10)
    st = g.state()
    if st is not None and (st['group'], st['num']) == (38,3) and g.var(0x4055) == 2:
        print(f"in lab, scene var=2 at i={i}")
        break
    if i % 6 == 0:
        g.tap(K.KEY_A, hold=1, wait=2)
else:
    print("cutscene never completed; state:", g.describe())
g.frame(120)
print("post-cutscene:", g.describe(), "var_lab:", g.var(0x4055), "var_oak:", g.var(0x4050))
g.shot("15_oak_lab.png")
# Walk to the middle starter ball at (9,4): from wherever the player is
st = g.state()
print("player pos:", st['x'], st['y'])
