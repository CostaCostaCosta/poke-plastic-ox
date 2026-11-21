
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from walklib import *

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
# Oak cutscene A-mash until var_lab==2
for i in range(1200):
    g.frame(10)
    st = g.state()
    if st is not None and (st['group'], st['num']) == (38,3) and g.var(0x4055) == 2:
        print("scene var=2 at i=", i)
        break
    if i % 6 == 0:
        g.tap(K.KEY_A, hold=1, wait=2)
g.frame(60)
print("post-cutscene:", g.describe(), "var_lab:", g.var(0x4055), "var_oak:", g.var(0x4050))
# walk to ball at (9,4): stand at (8,4)? player at (6,4); walk to (8,4) and face right? Actually ball at (9,4)
st = g.state()
px, py = st['x'], st['y']
g.walk('RIGHT', target=(8, py))
print("at (8,4)?:", g.describe())
# face the ball at (9,4): press right briefly then A
g.hold(K.KEY_RIGHT, 10)
g.frame(5)
g.tap(K.KEY_A, hold=2, wait=20)
print("after A on ball:", g.describe(), "var_lab:", g.var(0x4055))
# YES on confirm
g.frame(30)
g.tap(K.KEY_A, hold=2, wait=40)
print("after YES:", g.describe(), "var_lab:", g.var(0x4055))
# nickname prompt: B for NO
g.frame(30)
g.tap(K.KEY_B, hold=2, wait=40)
print("after B (nickname NO):", g.describe(), "var_lab:", g.var(0x4055))
# mash through rival-taking texts until var_lab==3
for i in range(600):
    g.frame(12)
    if i % 5 == 0:
        g.tap(K.KEY_A, hold=1, wait=2)
    if g.var(0x4055) == 3:
        print("var_lab=3 at i=", i)
        break
g.frame(90)
print("after rival takes starter:", g.describe(), "var_lab:", g.var(0x4055))
g.shot("16_rival_took_starter.png")

# trigger the rival battle: walk DOWN to the trigger row y=8
st = g.state()
print("walking down from", st['x'], st['y'])
g.core.set_keys(K.KEY_DOWN)
battle_started = False
for i in range(200):
    g.frame(12)
    h = g.hash()
    if i % 10 == 0:
        st = g.state()
        print(f"  walk-down i={i}: {g.describe()}")
    if st is not None and st['y'] >= 8:
        print("reached trigger row")
        break
g.core.clear_keys(K.KEY_DOWN)
g.frame(30)
print("at:", g.describe())

# battle: mash A, detect battle UI via framebuffer changes (bottom row menu)
import hashlib
prev = None
for i in range(3000):
    g.tap(K.KEY_A, hold=1, wait=2)
    g.frame(6)
    st = g.state()
    h = g.hash()
    if i % 250 == 0:
        print(f"  battle i={i}: {g.describe()} hash={h[:8]}")
    # try to detect: player able to move = battle over (test a quick DOWN nudge)
    if st is not None and (st['group'], st['num']) == (38,3) and i > 200 and i % 60 == 59:
        pass
print("post-battle state:", g.describe())
g.shot("17_post_rival_battle.png")
from PIL import Image
im = g.fb.to_pil().convert("RGB")
w,h = im.size
# sample rows
import collections
for y in range(0, h, 8):
    rowpix = [im.getpixel((x,y)) for x in range(0, w, 8)]
    counts = collections.Counter(rowpix).most_common(3)
    print(f"y={y:3d}: {counts}")
# average color per band
band = im.crop((0,0,w,40))
print("top band avg:", tuple(int(sum(c[i] for c in band.getdata())/ (w*40)) for i in range(3)))
mid = im.crop((0,60,w,100))
print("mid band avg:", tuple(int(sum(c[i] for c in mid.getdata())/ (w*40)) for i in range(3)))
bot = im.crop((0,120,w,h))
print("bot band avg:", tuple(int(sum(c[i] for c in bot.getdata())/ (w*40)) for i in range(3)))
# text-box presence: bottom 40 rows whiteness
hist = im.crop((0,h-40,w,h)).convert("L").histogram()
print("bottom whiteness:", sum(hist[201:])/(w*40))
g.shot("17b_stuck_battle.png")
print("battleTypeFlags:", hex(g.u32(0x020000cc)))
print("battleOutcome:", g.u16(0x0200014c))
# gBattleMainFunc is a function pointer (iwram 0x0300241c)
pf = g.u32(0x0300241c)
print("gBattleMainFunc ptr:", hex(pf) if pf else None)
# search for the function name in the map
import subprocess as sp
r = sp.run(['grep', '-n', hex(pf) if pf else 'zzz', '/home/eddie/repos/poke-plastic-ox/pokeemerald.map'], capture_output=True, text=True)
print("map hit:", r.stdout[:400])
g.core.set_keys(K.KEY_B)
for _ in range(60): g.core.run_frame()
g.core.clear_keys(K.KEY_B)
g.frame(10)
print("after B:", g.describe(), "flags:", hex(g.u32(0x020000cc)))
g.shot("17c_after_B.png")


