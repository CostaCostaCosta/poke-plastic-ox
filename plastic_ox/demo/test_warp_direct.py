
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
base=int(st['ptr'],16)-0x02000000
# set position to warp tile
g.core.memory.wram.s16[base+0]=10
g.core.memory.wram.s16[base+2]=2
# set elevation? elevation stored in saveblock? Maybe in player state.
g.frame(60)
st=g.state()
print('after set', g.describe())
# try triggering warp by pressing down? Actually stepping onto warp tile triggers automatically.
# Let's try to force warp by setting player on warp tile and then doing a step.
g.core.set_keys(K.KEY_DOWN)
g.frame(6)
g.core.clear_keys(K.KEY_DOWN)
g.frame(30)
st=g.state()
print('after down', g.describe())
