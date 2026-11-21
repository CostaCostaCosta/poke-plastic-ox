
import os
os.environ.setdefault('LD_LIBRARY_PATH', '/tmp/mgba-0.10.3/build:/usr/lib/x86_64-linux-gnu')
import sys
sys.path.insert(0, '/home/eddie/repos/poke-plastic-ox/plastic_ox/demo')
from walklib import GBA, K
import time

shots_dir = '/home/eddie/repos/poke-plastic-ox/plastic_ox/demo/shots'
os.makedirs(shots_dir, exist_ok=True)

def shot(g, name):
    path = os.path.join(shots_dir, name+'.png')
    g.fb.to_pil().convert("RGB").save(path)
    print('saved', path)

def log(msg):
    print(msg)

g = GBA()
log('Boot')
g.frame(600)
shot(g,'flow_boot')
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

wait=0
st=None
while wait<5000:
    st=g.state()
    if st and st['group']==38 and st['num']==1:
        log('Reached bedroom: '+g.describe())
        break
    g.frame(30)
    wait+=30
shot(g,'flow_bedroom')
assert st and st['group']==38 and st['num']==1
assert st['x']==6 and st['y']==6, f'pos {st["x"]},{st["y"]}'

for _ in range(20):
    g.tap(K.KEY_DOWN, hold=2, wait=10)
    g.frame(30)
st=g.state()
log('After downstairs: '+g.describe())
shot(g,'flow_1f')
assert st and st['group']==38 and st['num']==0

# walk out to Pallet Town
for _ in range(30):
    g.tap(K.KEY_DOWN, hold=2, wait=10)
    g.frame(30)
st=g.state()
# hold down until map change
for _ in range(200):
    g.core.set_keys(K.KEY_DOWN)
    g.frame(6)
    st=g.state()
    if st and st['group']==75 and st['num']==0:
        break
g.core.clear_keys(K.KEY_DOWN)
g.frame(30)
log('Pallet Town: '+g.describe())
shot(g,'flow_pallet_town')
assert st and st['group']==75 and st['num']==0

# walk north to Route101
for _ in range(400):
    g.core.set_keys(K.KEY_UP)
    g.frame(6)
    st=g.state()
    if st and st['group']==0 and st['num']==16:
        break
g.core.clear_keys(K.KEY_UP)
g.frame(30)
log('Route101: '+g.describe())
shot(g,'flow_route101')
assert st and st['group']==0 and st['num']==16

# walk north to Oldale
for _ in range(400):
    g.core.set_keys(K.KEY_UP)
    g.frame(6)
    st=g.state()
    if st and st['group']==0 and st['num']==10:
        break
g.core.clear_keys(K.KEY_UP)
g.frame(30)
log('Oldale: '+g.describe())
shot(g,'flow_oldale')
assert st and st['group']==0 and st['num']==10

# back south to Route101
for _ in range(400):
    g.core.set_keys(K.KEY_DOWN)
    g.frame(6)
    st=g.state()
    if st and st['group']==0 and st['num']==16:
        break
g.core.clear_keys(K.KEY_DOWN)
g.frame(30)
log('Back Route101: '+g.describe())
shot(g,'flow_route101_back')
assert st and st['group']==0 and st['num']==16

# back south to Pallet
for _ in range(400):
    g.core.set_keys(K.KEY_DOWN)
    g.frame(6)
    st=g.state()
    if st and st['group']==75 and st['num']==0:
        break
g.core.clear_keys(K.KEY_DOWN)
g.frame(30)
log('Back Pallet: '+g.describe())
shot(g,'flow_pallet_back')
assert st and st['group']==75 and st['num']==0

print('VERIFICATION PASSED')
