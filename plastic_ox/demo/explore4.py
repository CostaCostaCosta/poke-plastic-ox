
import os, hashlib, time
os.environ.setdefault('LD_LIBRARY_PATH', '/tmp/mgba-0.10.3/build:/usr/lib/x86_64-linux-gnu')
import mgba.core, mgba.image, mgba.gba, mgba.log
mgba.log.silence()

ROM = "/home/eddie/repos/poke-plastic-ox/pokeemerald.gba"
SHOTS = "/home/eddie/repos/poke-plastic-ox/plastic_ox/demo/shots"

K = mgba.gba.GBA
DIR = {K.KEY_UP: (0,-1), K.KEY_DOWN: (0,1), K.KEY_LEFT: (-1,0), K.KEY_RIGHT: (1,0)}
MAP_NAMES = {(38,1): "PALLET_2F", (38,0): "PALLET_1F", (75,0): "PALLET_TOWN", (38,3): "OAK_LAB", (0,16): "ROUTE101", (0,10): "OLDALE"}

class GBA:
    def __init__(self, rom=ROM):
        self.core = mgba.core.load_path(rom)
        self.fb = mgba.image.Image(*self.core.desired_video_dimensions())
        self.core.set_video_buffer(self.fb)
        self.core.reset()
        self.fb = mgba.image.Image(*self.core.desired_video_dimensions())
        self.core.set_video_buffer(self.fb)
    def frame(self, n=1):
        for _ in range(n):
            self.core.run_frame()
    def keys(self, *ks):
        for k in ks: self.core.set_keys(k)
    def release(self, *ks):
        for k in ks: self.core.clear_keys(k)
    def tap(self, key, hold=2, wait=8):
        self.keys(key); self.frame(hold); self.release(key); self.frame(wait)
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
    def describe(self):
        st = self.state()
        if st is None: return "no-saveblock"
        mn = MAP_NAMES.get((st['group'], st['num']), f"({st['group']},{st['num']})")
        return f"{mn} at ({st['x']},{st['y']})"

def boot_to_bedroom(g):
    g.frame(300)
    for i in range(200):
        g.frame(30)
        if i % 4 == 0:
            g.tap(K.KEY_A, hold=1, wait=3)
    g.tap(K.KEY_START, hold=2, wait=30)
    g.frame(120)
    g.tap(K.KEY_A, hold=2, wait=30)
    g.frame(240)
    for i in range(2000):
        g.frame(30)
        st = g.state()
        if st is not None:
            base = int(st['ptr'],16) - 0x02000000
            g.core.memory.wram.u16[base+0x14] = (g.core.memory.wram.u16[base+0x14] & ~7) | 2
        if i % 3 == 0:
            g.tap(K.KEY_A, hold=1, wait=2)
        if st is not None and st['group'] == 38 and st['num'] == 1:
            return
    raise RuntimeError("never reached bedroom")

def walk(g, direction, target=None, timeout=4000, steps=None, mash_during_text=True):
    """Hold a direction; optionally stop when state x/y matches target; mash A if text box appears."""
    dx, dy = DIR[direction]
    g.keys(direction)
    moved_any = False
    frames = 0
    while frames < timeout:
        # mash if text box present
        if mash_during_text and g.bottom_whiteness() > 0.5:
            g.release(direction)
            g.tap(K.KEY_A, hold=1, wait=3)
            g.keys(direction)
            frames += 10
            continue
        g.frame(10)
        frames += 10
        st = g.state()
        if st is None: continue
        if target is not None and (st['x'], st['y']) == target:
            break
    g.release(direction)
    g.frame(8)
    return g.describe()

g = GBA()
boot_to_bedroom(g)
print("bedroom:", g.describe())
g.frame(90)  # let the fade-in complete
g.shot("10_bedroom.png")
print("bedroom rendered:", g.describe(), "bw:", round(g.bottom_whiteness(),3))

# walk to stairs: RIGHT to x=10, UP to y=2
walk(g, K.KEY_RIGHT, target=(10, g.state()['y']))
walk(g, K.KEY_UP, target=(10, 2))
print("at stairs:", g.describe())
# wait for warp (fade + transition), poll map change
for i in range(60):
    g.frame(30)
    st = g.state()
    if st is not None and (st['group'], st['num']) != (38, 1):
        print(f"WARPED at +{i*30}f to {g.describe()}")
        break
else:
    print("NO WARP after 1800f:", g.describe())
g.frame(90)
print("stabilized:", g.describe())
