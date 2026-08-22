
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
print("outside:", g.describe())
st = g.state()
g.walk('DOWN', target=(st['x'], 9))
g.walk('RIGHT', target=(12, 9))
g.walk('UP', target=(12, 7))
g.walk('LEFT', target=(11, 7))
g.walk('UP', target=(11, 2))
g.walk('RIGHT', target=(12, 2))
g.walk('UP', target=(12, 1))
print("after trigger walk:", g.describe())
# Now wait WITHOUT mashing, watch the cutscene unfold: sample state every 30f for 3000f
for i in range(100):
    g.frame(30)
    st = g.state()
    if i % 5 == 0:
        print(f"  t={i*30}: {g.describe()} var_lab={g.var(0x4055)} var_oak={g.var(0x4050)} player_facing?")
    if st is not None and (st['group'], st['num']) == (38,3):
        print("in lab:", g.describe())
    if st is not None and (st['group'], st['num']) == (38,3) and st['y'] <= 6:
        print("player walked into lab interior:", g.describe())
        break
# keep watching until scene settles (text boxes present -> mash A)
for i in range(200):
    g.frame(20)
    st = g.state()
    if i % 10 == 0:
        print(f"  lab t={i*20}: {g.describe()} var_lab={g.var(0x4055)} var_oak={g.var(0x4050)}")
    if st is not None and st['group'] == 38 and st['num'] == 3 and st['y'] < 6 and (st['x'], st['y']) != (6,12):
        pass
