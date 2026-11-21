
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from walklib import *

# same path to the battle as probe6
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
for i in range(1200):
    g.frame(10)
    st = g.state()
    if st is not None and (st['group'], st['num']) == (38,3) and g.var(0x4055) == 2:
        break
    if i % 6 == 0:
        g.tap(K.KEY_A, hold=1, wait=2)
g.frame(60)
st = g.state()
g.walk('RIGHT', target=(8, st['y']))
g.hold(K.KEY_RIGHT, 10); g.frame(5)
g.tap(K.KEY_A, hold=2, wait=20)
g.tap(K.KEY_A, hold=2, wait=40)
g.tap(K.KEY_B, hold=2, wait=40)
for i in range(600):
    g.frame(12)
    if i % 5 == 0:
        g.tap(K.KEY_A, hold=1, wait=2)
    if g.var(0x4055) == 3:
        break
g.frame(60)
g.walk('DOWN', target=(7, 8))
g.core.set_keys(K.KEY_DOWN)
for i in range(40):
    g.frame(12)
    st = g.state()
    if st is not None and st['y'] >= 8:
        break
g.core.clear_keys(K.KEY_DOWN)
g.frame(30)
print("battle triggered:", g.describe(), "flags:", hex(g.u32(0x020000cc)))

def sample(label, frames, key=None):
    from collections import Counter
    c = Counter()
    seq = []
    last = None
    for i in range(frames // 2):
        g.frame(2)
        v = g.u32(0x030023fc)
        c[v] += 1
        if v != last:
            seq.append((i*2, hex(v)))
            last = v
    print(f"--- {label} ---")
    print("  distinct:", len(c), "top:", [(hex(k), v) for k, v in c.most_common(6)])
    print("  transitions:", seq[:20])

# wait for the battle intro text to settle; the first A-mash phase ended at trigger,
# so press A a few times (with pauses) to get past intro messages, then sample without input
for i in range(120):
    g.frame(15)
    if i % 10 == 0:
        g.core.set_keys(K.KEY_A); g.frame(2); g.core.clear_keys(K.KEY_A)
print("past intro; sampling with no input...")
sample("no-input phase (expect FIGHT menu or idle)", 400)
# press A once to advance/open a menu
g.core.set_keys(K.KEY_A); g.frame(2); g.core.clear_keys(K.KEY_A)
sample("after single A", 200)
g.core.set_keys(K.KEY_A); g.frame(2); g.core.clear_keys(K.KEY_A)
sample("after 2nd A", 200)
g.core.set_keys(K.KEY_DOWN); g.frame(2); g.core.clear_keys(K.KEY_DOWN)
g.core.set_keys(K.KEY_A); g.frame(2); g.core.clear_keys(K.KEY_A)
sample("after DOWN+A", 200)
