
import os, hashlib, time, sys
os.environ.setdefault('LD_LIBRARY_PATH', '/tmp/mgba-0.10.3/build:/usr/lib/x86_64-linux-gnu')
import mgba.core, mgba.image, mgba.gba, mgba.log
mgba.log.silence()

ROM = "/home/eddie/repos/poke-plastic-ox/pokeemerald.gba"
SHOTS = "/home/eddie/repos/poke-plastic-ox/plastic_ox/demo/shots"
LOGF = "/home/eddie/repos/poke-plastic-ox/plastic_ox/demo/timeline.log"

class GBA:
    def __init__(self, rom=ROM):
        self.core = mgba.core.load_path(rom)
        self.fb = mgba.image.Image(*self.core.desired_video_dimensions())
        self.core.set_video_buffer(self.fb)
        self.core.reset()
        self.fb = mgba.image.Image(*self.core.desired_video_dimensions())
        self.core.set_video_buffer(self.fb)
        self.K = mgba.gba.GBA
    def frame(self, n=1):
        for _ in range(n):
            self.core.run_frame()
    def tap(self, key, hold=2, wait=8):
        self.core.set_keys(key); self.frame(hold); self.core.clear_keys(key); self.frame(wait)
    def hold(self, key, n):
        self.core.set_keys(key); self.frame(n); self.core.clear_keys(key)
    def hash(self):
        return hashlib.md5(self.fb.to_pil().convert("RGB").tobytes()).hexdigest()
    def state(self):
        s1 = self.core.memory.iwram.u32[0x51D4]
        if not (0x02000000 <= s1 < 0x02040000):
            return None
        base = s1 - 0x02000000
        return dict(ptr=hex(s1), group=self.core.memory.wram.s8[base+4],
                    num=self.core.memory.wram.s8[base+5],
                    x=self.core.memory.wram.s16[base+0],
                    y=self.core.memory.wram.s16[base+2],
                    textspeed=self.core.memory.wram.u16[base+0x14] & 7)
    def shot(self, name):
        path = os.path.join(SHOTS, name)
        self.fb.to_pil().convert("RGB").save(path)
        return path
    def bottom_whiteness(self):
        im = self.fb.to_pil().convert("RGB")
        w, h = im.size
        crop = im.crop((0, h-40, w, h))
        hist = crop.convert("L").histogram()
        return sum(hist[201:]) / (w * 40)

g = GBA()
log = open(LOGF, "w")
t0 = time.time()
prev = None
seq = 0

def ev(tag, extra=""):
    st = g.state()
    print(f"t={t:7d} {tag:28s} f={g.hash()} st={st} bw={g.bottom_whiteness():.3f} {extra}", file=log, flush=True)

# Phase 1: boot, 300 frames, hash-change detection
t = 0
g.frame(300); t = 300
ev("boot300")
# tap A occasionally through the game-freak animation and title
for i in range(200):
    g.frame(30); t += 30
    if i % 4 == 0:
        g.tap(g.K.KEY_A, hold=1, wait=3)
    if i % 40 == 0:
        ev(f"intro-mash i={i}")
# Now try pressing START to get to the main menu; then A for NEW GAME
g.tap(g.K.KEY_START, hold=2, wait=30); t += 32
ev("start_press")
g.frame(120); t += 120
ev("after_start_120")
g.tap(g.K.KEY_A, hold=2, wait=30); t += 32
ev("A_newgame")
g.frame(240); t += 240
ev("after_A_240")

# Now the Birch intro: set FAST text as soon as saveblock valid
for i in range(2000):
    g.frame(30); t += 30
    st = g.state()
    if st is not None:
        base = int(st['ptr'],16) - 0x02000000
        g.core.memory.wram.u16[base+0x14] = (g.core.memory.wram.u16[base+0x14] & ~7) | 2
    # adaptive: mostly mash A but with pauses
    if i % 3 == 0:
        g.tap(g.K.KEY_A, hold=1, wait=2)
    if i % 100 == 0:
        ev(f"birch-mash i={i}")
    if st is not None and st['group'] == 38 and st['num'] == 1:
        ev("REACHED_BEDROOM")
        break
print("elapsed wall: %.1fs for %d frames" % (time.time()-t0, t))
print("done", file=log, flush=True)
log.close()
