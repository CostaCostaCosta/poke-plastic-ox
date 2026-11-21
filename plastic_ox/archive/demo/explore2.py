
import os, hashlib
os.environ.setdefault('LD_LIBRARY_PATH', '/tmp/mgba-0.10.3/build:/usr/lib/x86_64-linux-gnu')
import mgba.core, mgba.image, mgba.gba, mgba.log
mgba.log.silence()

ROM = "/home/eddie/repos/poke-plastic-ox/pokeemerald.gba"
SHOTS = "/home/eddie/repos/poke-plastic-ox/plastic_ox/demo/shots"

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
        # bottom 40 rows
        box = (0, h-40, w, h)
        crop = im.crop(box)
        hist = crop.convert("L").histogram()
        # count pixels with luminance > 200
        bright = sum(hist[201:])
        total = w * 40
        return bright / total

g = GBA()
prev = None
seq = 0
for i in range(2400):
    g.frame(30)
    h = g.hash()
    st = g.state()
    bw = g.bottom_whiteness()
    if h != prev:
        g.shot(f"s{seq:03d}_t{i*30}.png")
        print(f"t={i*30:5d} seq={seq:3d} hash={h} state={st} bottomwhite={bw:.3f}")
        seq += 1
        last_change = i
        prev = h
    elif i % 20 == 0:
        print(f"t={i*30:5d} (same) state={st} bottomwhite={bw:.3f}")
    if i % 60 == 0 and i > 120:
        g.tap(g.K.KEY_A, hold=1, wait=3)
print("final state:", g.state())
