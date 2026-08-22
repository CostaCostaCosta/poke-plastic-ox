
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
# walk right 4 steps to x=10
g.walk('RIGHT', target=(10,6), timeout=2000)
st=g.state()
print('after right', g.describe())
# walk up to y=2
g.walk('UP', target=(10,2), timeout=2000)
st=g.state()
print('after up', g.describe())
g.frame(60)
st=g.state()
print('final', g.describe())
