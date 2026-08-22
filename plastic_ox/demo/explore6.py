
import os, hashlib, time
os.environ.setdefault('LD_LIBRARY_PATH', '/tmp/mgba-0.10.3/build:/usr/lib/x86_64-linux-gnu')
import mgba.core, mgba.image, mgba.gba, mgba.log
mgba.log.silence()

ROM = "/home/eddie/repos/poke-plastic-ox/pokeemerald.gba"
SHOTS = "/home/eddie/repos/poke-plastic-ox/plastic_ox/demo/shots"
K = mgba.gba.GBA
DIRV = {'UP':(0,-1),'DOWN':(0,1),'LEFT':(-1,0),'RIGHT':(1,0)}
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
    def tap(self, key, hold=2, wait=8):
        self.core.set_keys(key); self.frame(hold); self.core.clear_keys(key); self.frame(wait)
    def state(self):
        s1 = self.core.memory.iwram.u32[0x51D4]
        if not (0x02000000 <= s1 < 0x02040000):
            return None
        base = s1 - 0x02000000
        return dict(ptr=hex(s1), group=self.core.memory.wram.s8[base+4],
                    num=self.core.memory.wram.s8[base+5],
                    x=self.core.memory.wram.s16[base+0],
                    y=self.core.memory.wram.s16[base+2])
    def _seg(self, addr):
        m = self.core.memory
        if 0x02000000 <= addr < 0x02040000: return m.wram, addr-0x02000000
        if 0x03000000 <= addr < 0x03008000: return m.iwram, addr-0x03000000
        if 0x08000000 <= addr < 0x0A000000: return m.rom, addr-0x08000000
        if 0x0A000000 <= addr < 0x0C000000: return m.cart1, addr-0x0A000000
        if 0x0C000000 <= addr < 0x0E000000: return m.cart2, addr-0x0C000000
        return None, 0
    def u8(self, a): seg, o = self._seg(a); return seg.u8[o]
    def s8(self, a): seg, o = self._seg(a); return seg.s8[o]
    def u16(self, a): seg, o = self._seg(a); return seg.u16[o]
    def s16(self, a): seg, o = self._seg(a); return seg.s16[o]
    def u32(self, a): seg, o = self._seg(a); return seg.u32[o]
    def s32(self, a): seg, o = self._seg(a); return seg.s32[o]
    def mapheader_info(self):
        mh = 0x02001664
        w = self.core.memory.wram
        layout = w.u32[mh-0x02000000]
        events = w.u32[(mh-0x02000000)+4]
        if layout == 0 or events == 0: return None
        width = self.s32(layout); height = self.s32(layout+4)
        warp_count = self.u8(events+1)
        warps_ptr = self.u32(events+8)
        warps = []
        for i in range(warp_count):
            woff = warps_ptr + i*8
            warps.append((self.s16(woff), self.s16(woff+2), self.u8(woff+4), self.u8(woff+5), self.u8(woff+6), self.u8(woff+7)))
        return dict(w=width, h=height, warps=warps)
    def behavior_at(self, mx, my):
        # map-local (mx,my) -> grid block -> metatile -> behavior
        base = 0x030024f8
        iw = self.core.memory.iwram
        off = base - 0x03000000
        width = iw.s32[off]; height = iw.s32[off+4]
        map_ptr = self.u32(base+8)
        idx = (mx + 7) + width*(my + 7)
        block = self.u16(map_ptr + idx*2)
        metatile = block & 0x03FF
        mh = 0x02001664
        layout = self.core.memory.wram.u32[mh-0x02000000]
        prim = self.u32(layout+0x10)
        attrs = self.u32(prim+0x10)
        attr = self.u32(attrs + metatile*4)
        behavior = attr & 0x1FF
        return behavior, metatile, block
    def describe(self):
        st = self.state()
        if st is None: return "no-saveblock"
        mn = MAP_NAMES.get((st['group'], st['num']), f"({st['group']},{st['num']})")
        return f"{mn} ({st['group']},{st['num']}) at ({st['x']},{st['y']})"
    def shot(self, name):
        path = os.path.join(SHOTS, name)
        self.fb.to_pil().convert("RGB").save(path)
        return path

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

def walk(g, direction, target=None, timeout=4000, mash=True):
    key = {'UP':K.KEY_UP,'DOWN':K.KEY_DOWN,'LEFT':K.KEY_LEFT,'RIGHT':K.KEY_RIGHT}[direction]
    g.core.set_keys(key)
    frames = 0
    while frames < timeout:
        g.frame(10)
        frames += 10
        st = g.state()
        if st is None: continue
        if target is not None and (st['x'], st['y']) == target:
            break
        # also break if map changed
        if st is not None and (st['group'], st['num']) not in ((38,1),(38,0)):
            break
    g.core.clear_keys(key)
    g.frame(8)
    return g.describe()

g = GBA()
boot_to_bedroom(g)
g.frame(90)
print("bedroom:", g.describe())
walk(g,'RIGHT',target=(10,6))
walk(g,'UP',target=(10,2))
print("stairs:", g.describe())
# press LEFT on the down-left stair warp
g.core.set_keys(K.KEY_LEFT)
for i in range(60):
    g.frame(30)
    st = g.state()
    if st and (st['group'], st['num']) == (38,0):
        print(f"warped to 1F at +{i*30}f"); break
g.core.clear_keys(K.KEY_LEFT)
g.frame(60)
print("1F:", g.describe())
g.shot("11_house_1f.png")
# probe behaviors near the front door area
for xy in [(5,8),(4,8),(3,9),(5,9),(4,9),(3,8),(6,8),(2,9)]:
    try:
        b, mt, blk = g.behavior_at(*xy)
        print(f"  1F tile {xy}: metatile={mt} behavior=0x{b:02x} block={blk:#06x}")
    except Exception as e:
        print(f"  1F tile {xy}: ERR {e}")

# walk to the south-arrow-warp door at (4,8)
st = g.state()
walk(g,'LEFT',target=(4, st['y']))     # to x=4 at y=2
st = g.state()
walk(g,'DOWN',target=(4, 7))           # to (4,7), in front of the door
print("in front of door:", g.describe())
# step onto the door tile (4,8)
g.core.set_keys(K.KEY_DOWN)
for i in range(40):
    g.frame(30)
    st = g.state()
    if st and (st['x'], st['y']) == (4,8):
        print(f"on door tile at +{i*30}f")
        break
# now hold DOWN to trigger the south arrow warp
for i in range(60):
    g.frame(30)
    st = g.state()
    if st and (st['group'], st['num']) == (75,0):
        print(f"EXITED to Pallet Town at +{i*30}f: {g.describe()}")
        break
g.core.clear_keys(K.KEY_DOWN)
g.frame(90)
print("outside:", g.describe())
g.shot("12_pallet_arrival.png")

# Walk north toward the Oak trigger at (12,1)/(13,1)
st = g.state()
walk(g,'RIGHT',target=(12, st['y']))   # x -> 12 at y=8
st = g.state()
print("at x=12:", g.describe())
walk(g,'UP',target=(12, 1))            # y -> 1 (trigger fires on the way)
print("after walking up:", g.describe())
g.frame(60)
print("after trigger wait:", g.describe())
# Oak cutscene: mash A with pauses while the map changes (player auto-walks to lab)
for i in range(400):
    g.frame(15)
    g.tap(K.KEY_A, hold=2, wait=4)
    st = g.state()
    if i % 100 == 0:
        print(f"  cutscene i={i}: {g.describe()}")
    if st is not None and (st['group'], st['num']) == (38,3):
        print(f"IN OAK LAB at i={i}: {g.describe()}")
        break
g.frame(120)
print("lab:", g.describe())
g.shot("13_oak_lab.png")
