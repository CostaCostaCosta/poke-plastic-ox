
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from walklib import *

for target, name in [(8, 'bulbasaur(8,4)'), (10, 'charmander(10,4)')]:
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
    print(f"--- {name}: player at {st['x']},{st['y']} ---")
    # approach from below: go to (target, 6), then UP to (target, 5), face UP -> ball at (target,4)
    g.walk('DOWN', target=(st['x'], 6))
    g.walk('RIGHT', target=(target, 6))
    g.walk('UP', target=(target, 5))
    st = g.state()
    print(f"   at {st['x']},{st['y']} (below ball)")
    g.hold(K.KEY_UP, 12)
    g.frame(5)
    g.tap(K.KEY_A, hold=2, wait=30)
    print(f"   after A: at {g.describe()} VAR_STARTER_MON={g.var(0x4023)}")
    g.tap(K.KEY_A, hold=2, wait=40)
    g.tap(K.KEY_B, hold=2, wait=40)
    for i in range(600):
        g.frame(12)
        if i % 5 == 0:
            g.tap(K.KEY_A, hold=1, wait=2)
        if g.var(0x4055) == 3:
            break
    print(f"   var_lab={g.var(0x4055)} final VAR_STARTER_MON={g.var(0x4023)}")
    print()
