
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from walklib import *

BM = 0x020004e8   # gBattleMons[0] player; rival = +0x64? need struct size; both player and opp at [0] and [1]
# offsets (assumed): hp u16 @45, maxHP u16 @49, level u8 @47, statStages s8[8] @26, moves[4] @14
# Let me dump raw and parse.
def dmp(g, base, label):
    raw = bytes(g.core.memory.wram.u8[base - 0x02000000 + i] for i in range(0x70))
    return raw

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
print("battle started:", g.describe(), "outcome:", g.u16(0x0200014c))

# step through the battle: log compressed handler runs, A every 10 frames
last = None
run_start = 0
for step in range(6000):
    g.frame(1)
    f0 = g.u32(0x030023fc)
    if f0 != last:
        if last is not None:
            print(f"  frames {run_start}-{step}: ctrl={hex(last)} (len {step-run_start})")
        last = f0
        run_start = step
        if f0 == 0x0805c949:
            print(f"    >>> MOVE LIST at {step}: gMoveSelCursor={g.u8(0x02000348)} multiCur={g.u8(0x03002485)}")
        else:
            print(f"    bw={g.bottom_whiteness():.2f}")
    if f0 == 0x0805c949:
        cur = g.u8(0x02000348)
        target = 1
        if cur == target:
            g.tap(K.KEY_A, hold=1, wait=2)
        else:
            g.tap(K.KEY_DOWN, hold=1, wait=2)
            g.frame(1); g.tap(K.KEY_A, hold=1, wait=2)
        step += 6
        last = None
    elif f0 == 0x0805d901:
        g.tap(K.KEY_A, hold=1, wait=2)
    elif g.bottom_whiteness() > 0.35:
        g.tap(K.KEY_A, hold=1, wait=2)
    elif step % 40 == 0:
        g.tap(K.KEY_A, hold=1, wait=1)
    if step % 1000 == 0 and step > 0:
        print(f"  == progress {step}: outcome={g.u16(0x0200014c)}")
    if g.u16(0x0200014c) != 0:
        print("OUTCOME:", g.u16(0x0200014c))
        break
