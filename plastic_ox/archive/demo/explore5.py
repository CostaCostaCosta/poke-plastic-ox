
import os, hashlib, time
os.environ.setdefault('LD_LIBRARY_PATH', '/tmp/mgba-0.10.3/build:/usr/lib/x86_64-linux-gnu')
import mgba.core, mgba.image, mgba.gba, mgba.log
mgba.log.silence()

ROM = "/home/eddie/repos/poke-plastic-ox/pokeemerald.gba"
K = mgba.gba.GBA
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
        if 0x0E000000 <= addr < 0x0E010000: return m.sram, addr-0x0E000000
        return None, 0
    def u8(self, addr): seg, off = self._seg(addr); return seg.u8[off]
    def s8(self, addr): seg, off = self._seg(addr); return seg.s8[off]
    def u16(self, addr): seg, off = self._seg(addr); return seg.u16[off]
    def s32(self, addr): seg, off = self._seg(addr); return seg.s32[off]
    def s16(self, addr): seg, off = self._seg(addr); return seg.s16[off]
    def u32(self, addr): seg, off = self._seg(addr); return seg.u32[off]
    def mapgrid_info(self):
        # gBackupMapLayout @ 0x030024f8 (IWRAM); struct {s32 width; s32 height; u16* map;}
        base = 0x030024f8
        iw = self.core.memory.iwram
        off = base - 0x03000000
        width = iw.s32[off]
        height = iw.s32[off+4]
        map_ptr = self.u32(base+8)
        return dict(width=width, height=height, map_ptr=map_ptr)
    def metatile_at(self, mx, my):
        g = self.mapgrid_info()
        if g['map_ptr'] == 0: return None
        # map-local coords -> grid index with MAP_OFFSET=7
        idx = (mx + 7) + g['width']*(my + 7)
        block = self.u16(g['map_ptr'] + idx*2)
        metatile = block & 0x03FF
        return metatile, block
    def behavior_at(self, mx, my):
        g = self.mapgrid_info()
        mt, block = self.metatile_at(mx, my)
        mh = self.mapheader_info()
        layout = self.u32(0x02001664)
        prim = self.u32(layout+0x10)
        attrs = self.u32(prim+0x10)
        attr = self.u32(attrs + mt*4)
        behavior = attr & 0x1FF  # bits 0-8 for FRLG
        return behavior, mt, block, attr
    def mapheader_info(self):
        mh = 0x02001664
        w = self.core.memory.wram
        layout = w.u32[mh-0x02000000]
        events = w.u32[(mh-0x02000000)+4]
        if layout == 0 or events == 0: return None
        width = self.s32(layout)
        height = self.s32(layout+4)
        warp_count = self.u8(events+1)
        warps_ptr = self.u32(events+8)
        warps = []
        for i in range(warp_count):
            woff = warps_ptr + i*8
            warps.append((self.s16(woff), self.s16(woff+2), self.u8(woff+4), self.u8(woff+5), self.u8(woff+6), self.u8(woff+7)))
        return dict(w=width, h=height, warps=warps)
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

def walk(g, direction, target=None, timeout=4000):
    g.core.set_keys(direction)
    frames = 0
    while frames < timeout:
        g.frame(10)
        frames += 10
        st = g.state()
        if st is None: continue
        if target is not None and (st['x'], st['y']) == target:
            break
    g.core.clear_keys(direction)
    g.frame(8)

g = GBA()
boot_to_bedroom(g)
g.frame(90)
print("bedroom:", g.describe())
mh = g.mapheader_info()
print("mapheader:", mh)
g.core.set_keys(K.KEY_RIGHT)
for _ in range(200):
    g.frame(10)
    st = g.state()
    if st and (st['x'], st['y']) == (10, 6): break
g.core.clear_keys(K.KEY_RIGHT)
g.frame(8)
print("at x=10,y=6:", g.describe(), "mh:", g.mapheader_info())
g.core.set_keys(K.KEY_UP)
for _ in range(200):
    g.frame(10)
    st = g.state()
    if st and (st['x'], st['y']) == (10, 2): break
g.core.clear_keys(K.KEY_UP)
g.frame(8)
print("at stairs (10,2):", g.describe(), "mh:", g.mapheader_info())
# diagnostic: metatile behavior at the warp tile and surroundings
print("-- testing directional stair warp: press LEFT at (10,2) --")
g.frame(10)
g.core.set_keys(K.KEY_LEFT)
for i in range(60):
    g.frame(30)
    st = g.state()
    if st and (st['group'], st['num']) != (38, 1):
        print(f"WARPED via LEFT at +{i*30}f: {g.describe()}")
        break
else:
    print("no warp via LEFT on stairs yet")
g.core.clear_keys(K.KEY_LEFT)
g.frame(30)
print("after left-hold:", g.describe())
for (mx, my) in [(10,2),(9,2),(10,3),(9,3),(6,6),(10,6)]:
    try:
        b, mt, blk, attr = g.behavior_at(mx, my)
        print(f"  tile ({mx},{my}): metatile={mt} block={blk:#06x} behavior={b} (0x{b:03x}) attr={attr:#010x}")
    except Exception as e:
        print(f"  tile ({mx},{my}): ERR {e}")
print("mapgrid:", g.mapgrid_info())
# now hold still and wait up to 3000 frames, sampling every 30
for i in range(100):
    g.frame(30)
    if i % 4 == 0:
        st = g.state()
        print(f"  wait {i*30}f: {g.describe()}")
        if st and (st['group'], st['num']) != (38, 1):
            print("WARPED to:", g.describe())
            break
