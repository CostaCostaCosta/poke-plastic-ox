
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
print('start', g.describe())
# teleport to 10,2
base=int(st['ptr'],16)-0x02000000
g.core.memory.wram.s16[base+0]=10
g.core.memory.wram.s16[base+2]=2
g.frame(30)
st=g.state()
print('after teleport', g.describe())
# let warp trigger
g.frame(60)
st=g.state()
print('after frames', g.describe())
