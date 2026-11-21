
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
print('state', st)
# try pressing B to cancel any dialog
g.tap(K.KEY_B, hold=2, wait=30)
g.frame(120)
st=g.state()
print('after B', g.describe())
# try pressing START
g.tap(K.KEY_START, hold=2, wait=30)
g.frame(120)
st=g.state()
print('after START', g.describe())
# now try move
g.core.set_keys(K.KEY_RIGHT)
for _ in range(30):
    g.frame(6)
g.core.clear_keys(K.KEY_RIGHT)
g.frame(30)
print('after move', g.describe())
