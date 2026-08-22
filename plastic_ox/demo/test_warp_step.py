
import os
os.environ.setdefault('LD_LIBRARY_PATH', '/tmp/mgba-0.10.3/build:/usr/lib/x86_64-linux-gnu')
import sys
sys.path.insert(0, '/home/eddie/repos/poke-plastic-ox/plastic_ox/demo')
from walklib import GBA, K
g=GBA()
g.frame(600)
for _ in range(3):
    g.tap(K.KEY_A, hold=2, wait=30)
    g.frame(120)
for i in range(80):
    g.set_text_speed_fast()
    g.tap(K.KEY_A, hold=1, wait=2)
    g.frame(20)
st=g.state()
print('start', g.describe())
# teleport to 9,2 then step down
base=int(st['ptr'],16)-0x02000000
g.core.memory.wram.s16[base+0]=9
g.core.memory.wram.s16[base+2]=2
g.frame(30)
st=g.state()
print('teleport', g.describe())
# step down to 9,3? Actually warp at 10,2. Let's step right then down?
g.core.set_keys(K.KEY_RIGHT)
g.frame(6)
g.core.clear_keys(K.KEY_RIGHT)
g.frame(30)
st=g.state()
print('after right', g.describe())
g.core.set_keys(K.KEY_DOWN)
g.frame(6)
g.core.clear_keys(K.KEY_DOWN)
g.frame(30)
st=g.state()
print('after down', g.describe())
# Now try moving up onto warp
g.core.set_keys(K.KEY_UP)
for _ in range(10):
    g.frame(6)
g.core.clear_keys(K.KEY_UP)
g.frame(30)
st=g.state()
print('after up', g.describe())
