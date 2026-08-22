
import os
os.environ.setdefault('LD_LIBRARY_PATH', '/tmp/mgba-0.10.3/build:/usr/lib/x86_64-linux-gnu')
import sys
sys.path.insert(0, '/home/eddie/repos/poke-plastic-ox/plastic_ox/demo')
from walklib import GBA, K
g=GBA()
g.frame(600)
g.tap(K.KEY_A, hold=2, wait=30)
g.frame(120)
g.tap(K.KEY_A, hold=2, wait=30)
g.frame(120)
g.tap(K.KEY_A, hold=2, wait=30)
g.frame(600)
for i in range(80):
    g.set_text_speed_fast()
    g.tap(K.KEY_A, hold=1, wait=2)
    g.frame(20)
st=g.state()
print('start', st)
# Move to stairs at 10,2? Actually warp at 10,2
# Player at 6,6. Need to walk to 10,2
# Move right 4, up? Let's just hold right then up
for _ in range(60):
    g.core.set_keys(K.KEY_RIGHT)
    g.frame(6)
st=g.state()
print('right', st)
for _ in range(60):
    g.core.set_keys(K.KEY_UP)
    g.frame(6)
st=g.state()
print('up', st)
g.core.clear_keys(K.KEY_UP)
# step onto warp
for _ in range(10):
    g.core.set_keys(K.KEY_UP)
    g.frame(6)
st=g.state()
print('final', st, g.describe())
