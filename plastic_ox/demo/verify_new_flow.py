
import os, sys
os.environ.setdefault('LD_LIBRARY_PATH', '/tmp/mgba-0.10.3/build:/usr/lib/x86_64-linux-gnu')
from walklib import GBA, K
import time

shots_dir = '/home/eddie/repos/poke-plastic-ox/plastic_ox/demo/shots'
os.makedirs(shots_dir, exist_ok=True)

def log(msg):
    print(msg)

g = GBA()
log('Boot')
g.frame(600)
g.shot('flow_boot')
# tap through copyright/title
g.tap(K.KEY_A, hold=2, wait=30)
g.frame(120)
g.tap(K.KEY_A, hold=2, wait=30)
g.frame(120)
g.tap(K.KEY_A, hold=2, wait=30)  # NEW GAME
g.frame(600)

# fast-forward through any remaining intro screens
for i in range(80):
    g.set_text_speed_fast()
    g.tap(K.KEY_A, hold=1, wait=2)
    g.frame(20)

# Wait for saveblock to appear and bedroom
wait = 0
while wait < 5000:
    st = g.state()
    if st and st['group']==38 and st['num']==1:
        log('Reached bedroom: '+g.describe())
        break
    g.frame(30)
    wait += 30

g.shot('flow_bedroom')
assert st and st['group']==38 and st['num']==1, 'Not in bedroom'
assert st['x']==6 and st['y']==6, f'Bedroom pos wrong {st["x"]},{st["y"]}'

# walk downstairs: need warp? Player starts at 6,6 bedroom, downstairs warp to 1F at? Let's just walk down
# Down stairs is probably south? In FRLG players house 2F -> 1F warp at 6,7? Let's just tap down a few times then wait.
for _ in range(20):
    g.tap(K.KEY_DOWN, hold=2, wait=10)
    g.frame(30)

st = g.state()
log('After downstairs: '+g.describe())
g.shot('flow_1f')
# Expect 38,0
assert st and st['group']==38 and st['num']==0, 'Not in 1F'

# Walk out to Pallet Town: warp at door
# We'll just walk south repeatedly
for _ in range(30):
    g.tap(K.KEY_DOWN, hold=2, wait=10)
    g.frame(30)
st = g.state()
log('After house exit: '+g.describe())
g.shot('flow_pallet_town_entry')
# Might still be 1F, try walking to warp
# Let's hold down until map changes to 75,0
for _ in range(200):
    g.core.set_keys(K.KEY_DOWN)
    g.frame(6)
    st = g.state()
    if st and st['group']==75 and st['num']==0:
        break
g.core.clear_keys(K.KEY_DOWN)
g.frame(30)
log('Pallet Town: '+g.describe())
g.shot('flow_pallet_town')
assert st and st['group']==75 and st['num']==0, 'Not in Pallet Town'

# Walk north to Route 101
# target y? Pallet north exit around y=0? Let's just hold up
for _ in range(400):
    g.core.set_keys(K.KEY_UP)
    g.frame(6)
    st = g.state()
    if st and st['group']==0 and st['num']==16:
        break
g.core.clear_keys(K.KEY_UP)
g.frame(30)
log('Route101: '+g.describe())
g.shot('flow_route101')
assert st and st['group']==0 and st['num']==16, 'Not in Route101'

# Walk north to Oldale
for _ in range(400):
    g.core.set_keys(K.KEY_UP)
    g.frame(6)
    st = g.state()
    if st and st['group']==0 and st['num']==10:
        break
g.core.clear_keys(K.KEY_UP)
g.frame(30)
log('Oldale: '+g.describe())
g.shot('flow_oldale')
assert st and st['group']==0 and st['num']==10, 'Not in Oldale'

# Return south to Route101
for _ in range(400):
    g.core.set_keys(K.KEY_DOWN)
    g.frame(6)
    st = g.state()
    if st and st['group']==0 and st['num']==16:
        break
g.core.clear_keys(K.KEY_DOWN)
g.frame(30)
log('Back to Route101: '+g.describe())
g.shot('flow_route101_back')
assert st and st['group']==0 and st['num']==16

# Return south to Pallet
for _ in range(400):
    g.core.set_keys(K.KEY_DOWN)
    g.frame(6)
    st = g.state()
    if st and st['group']==75 and st['num']==0:
        break
g.core.clear_keys(K.KEY_DOWN)
g.frame(30)
log('Back to Pallet: '+g.describe())
g.shot('flow_pallet_back')
assert st and st['group']==75 and st['num']==0

print('VERIFICATION PASSED')
