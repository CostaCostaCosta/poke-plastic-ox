
"""Reusable headless mGBA Pokémon Emerald playthrough helpers (Plastic Ox demo)."""
import os, hashlib, re
from pathlib import Path
os.environ.setdefault('LD_LIBRARY_PATH', '/home/eddie/.venvs/mgba311/lib:/home/eddie/.venvs/mgba311/lib64')
import mgba.core, mgba.image, mgba.gba, mgba.log
mgba.log.silence()

ROM = "/home/eddie/repos/poke-plastic-ox/pokeemerald.gba"
LINKER_MAP = Path(ROM).with_suffix(".map")
K = mgba.gba.GBA
DIRKEY = {'UP': K.KEY_UP, 'DOWN': K.KEY_DOWN, 'LEFT': K.KEY_LEFT, 'RIGHT': K.KEY_RIGHT}
MAP_NAMES = {(38,1): "PALLET_2F", (38,0): "PALLET_1F", (75,0): "PALLET_TOWN",
             (38,3): "OAK_LAB", (0,16): "ROUTE101", (0,10): "OLDALE"}

class GBA:
    def __init__(self, rom=ROM):
        self._symbol_addresses = None
        self.core = mgba.core.load_path(rom)
        self.fb = mgba.image.Image(*self.core.desired_video_dimensions())
        self.core.set_video_buffer(self.fb)
        self.core.reset()
        self.fb = mgba.image.Image(*self.core.desired_video_dimensions())
        self.core.set_video_buffer(self.fb)
    # ---- basics ----
    def frame(self, n=1):
        for _ in range(n):
            self.core.run_frame()
    def tap(self, key, hold=2, wait=8):
        self.core.set_keys(key); self.frame(hold); self.core.clear_keys(key); self.frame(wait)
    def hold(self, key, n):
        self.core.set_keys(key); self.frame(n); self.core.clear_keys(key)
    def hash(self):
        return hashlib.md5(self.fb.to_pil().convert("RGB").tobytes()).hexdigest()
    # ---- game state ----
    def state(self):
        save_ptr_addr = self.symbol_address("gSaveBlock1Ptr")
        s1 = self.core.memory.iwram.u32[save_ptr_addr - 0x03000000]
        if not (0x02000000 <= s1 < 0x02040000):
            return None
        base = s1 - 0x02000000
        save2_ptr_addr = self.symbol_address("gSaveBlock2Ptr")
        s2 = self.core.memory.iwram.u32[save2_ptr_addr - 0x03000000]
        textspeed = None
        if 0x02000000 <= s2 < 0x02040000:
            textspeed = self.core.memory.wram.u16[s2 - 0x02000000 + 0x14] & 7
        return dict(ptr=hex(s1), group=self.core.memory.wram.s8[base+4],
                    num=self.core.memory.wram.s8[base+5],
                    x=self.core.memory.wram.s16[base+0],
                    y=self.core.memory.wram.s16[base+2],
                    textspeed=textspeed)
    def describe(self):
        st = self.state()
        if st is None: return "no-saveblock"
        mn = MAP_NAMES.get((st['group'], st['num']), f"({st['group']},{st['num']})")
        return f"{mn} ({st['group']},{st['num']}) at ({st['x']},{st['y']})"
    def party_species(self, idx=0):
        return self.u16(0x02031c08 + idx*0x64)   # gParties[B_TRAINER_PLAYER][idx].species
    def var(self, vid):
        """Read a VAR_* value from SaveBlock1 (vars array @ 0x139C)."""
        st = self.state()
        if st is None: return None
        base = int(st['ptr'], 16)
        idx = vid - 0x4000
        if not (0 <= idx < 1024): return None
        return self.core.memory.wram.u16[base - 0x02000000 + 0x139C + idx*2]
    def setvar(self, vid, val):
        st = self.state()
        if st is None: return False
        base = int(st['ptr'], 16)
        idx = vid - 0x4000
        if not (0 <= idx < 1024): return False
        self.core.memory.wram.u16[base - 0x02000000 + 0x139C + idx*2] = val
        return True
    def set_text_speed_fast(self):
        save_ptr_addr = self.symbol_address("gSaveBlock2Ptr")
        save_ptr = self.core.memory.iwram.u32[save_ptr_addr - 0x03000000]
        if not (0x02000000 <= save_ptr < 0x02040000): return False
        base = save_ptr - 0x02000000
        self.core.memory.wram.u16[base+0x14] = (self.core.memory.wram.u16[base+0x14] & ~7) | 2
        return True
    # ---- memory paging ----
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
    def symbol_address(self, name):
        """Resolve a linked symbol without hard-coding build-dependent RAM addresses."""
        if self._symbol_addresses is None:
            self._symbol_addresses = {}
            pattern = re.compile(r"^\s*(0x[0-9a-fA-F]+)\s+([A-Za-z_][A-Za-z0-9_]*)\s*$")
            with LINKER_MAP.open(encoding="utf-8", errors="replace") as linker_map:
                for line in linker_map:
                    match = pattern.match(line)
                    if match:
                        self._symbol_addresses[match.group(2)] = int(match.group(1), 16)
        if name in self._symbol_addresses:
            return self._symbol_addresses[name]
        raise KeyError(f"symbol not found in {LINKER_MAP}: {name}")
    # ---- map introspection ----
    def mapheader_info(self):
        mh = self.symbol_address("gMapHeader")
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
    def mapgrid_info(self):
        base = self.symbol_address("gBackupMapLayout")
        iw = self.core.memory.iwram
        off = base - 0x03000000
        width = iw.s32[off]; height = iw.s32[off+4]
        map_ptr = self.u32(base+8)
        return dict(width=width, height=height, map_ptr=map_ptr)
    def metatile_at(self, mx, my):
        g = self.mapgrid_info()
        if g['map_ptr'] == 0: return None
        idx = (mx + 7) + g['width']*(my + 7)
        block = self.u16(g['map_ptr'] + idx*2)
        return block & 0x03FF, block
    def behavior_at(self, mx, my):
        mt, block = self.metatile_at(mx, my)
        mh = self.symbol_address("gMapHeader")
        layout = self.core.memory.wram.u32[mh-0x02000000]
        is_frlg = self.u8(layout+0x18) != 0
        primary_count = 640 if is_frlg else 512
        if mt < primary_count:
            tileset = self.u32(layout+0x10)
            attr_index = mt
        else:
            tileset = self.u32(layout+0x14)
            attr_index = mt - primary_count
        attrs = self.u32(tileset+0x10)
        if is_frlg:
            behavior = self.u32(attrs + attr_index*4) & 0x1FF
        else:
            behavior = self.u16(attrs + attr_index*2) & 0xFF
        return behavior, mt, block
    def set_block_metatile(self, mx, my, metatile):
        """Rewrite the live map-grid block at map-local (mx,my) to a metatile id
        (preserving collision/elevation bits)."""
        g = self.mapgrid_info()
        if g['map_ptr'] == 0: return False
        idx = (mx + 7) + g['width']*(my + 7)
        block = self.u16(g['map_ptr'] + idx*2)
        newblock = (block & ~0x03FF) | (metatile & 0x03FF)
        self.core.memory.wram.u16[g['map_ptr'] - 0x02000000 + idx*2] = newblock
        return True
    def collision_at(self, mx, my):
        mt, block = self.metatile_at(mx, my)
        return (block & 0x0C00) >> 10, (block & 0xF000) >> 12
    # ---- movement ----
    def walk(self, direction, target=None, timeout=4000, expect_map=None, mash_text=True):
        """Hold a direction until the player crosses target (or map changes).

        Crossing detection (>= x for RIGHT, <= x for LEFT, >= y for DOWN,
        <= y for UP) prevents overshooting past the target tile.
        If mash_text is True and a dialog box is visible, taps A while walking.
        """
        key = DIRKEY[direction]
        self.core.set_keys(key)
        frames = 0
        tx, ty = (target if target is not None else (None, None))
        while frames < timeout:
            st = self.state()
            if st is not None:
                if expect_map is not None and (st['group'], st['num']) == expect_map:
                    break
                if target is not None:
                    x, y = st['x'], st['y']
                    if direction == 'RIGHT' and x >= tx: break
                    if direction == 'LEFT' and x <= tx: break
                    if direction == 'DOWN' and y >= ty: break
                    if direction == 'UP' and y <= ty: break
            self.frame(6)
            frames += 6
        self.core.clear_keys(key)
        self.frame(8)
        return self.describe()
    def bottom_whiteness(self):
        im = self.fb.to_pil().convert("RGB")
        w, h = im.size
        crop = im.crop((0, h-40, w, h))
        hist = crop.convert("L").histogram()
        return sum(hist[201:]) / (w * 40)
    def shot(self, name):
        if not os.path.splitext(name)[1]:
            name += ".png"
        path = os.path.join("/home/eddie/repos/poke-plastic-ox/plastic_ox/demo/shots", name)
        self.fb.to_pil().convert("RGB").save(path)
        return path
    # ---- generic ----
    def wait_for(self, pred, timeout_frames, step=30, label=""):
        for i in range(timeout_frames // step):
            self.frame(step)
            if pred():
                return i*step
        return None

def boot_to_bedroom(g):
    """Drive the boot/intro/new-game sequence to the 2F bedroom."""
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
        g.set_text_speed_fast()
        if i % 3 == 0:
            g.tap(K.KEY_A, hold=1, wait=2)
        st = g.state()
        if st is not None and st['group'] == 38 and st['num'] == 1:
            break
    else:
        raise RuntimeError("never reached bedroom")
    # the A-mash above can open the NES sign the player faces at spawn;
    # close any open dialog and verify movement before returning
    g.frame(60)
    for k in range(15):
        st0 = g.state()
        g.tap(K.KEY_A, hold=2, wait=25)
        g.tap(K.KEY_B, hold=2, wait=25)
        g.frame(30)
        g.tap(K.KEY_RIGHT, hold=10, wait=30)
        st1 = g.state()
        if st0 and st1 and st1['x'] != st0['x']:
            g.tap(K.KEY_LEFT, hold=10, wait=30)   # step back to spawn column
            return
    raise RuntimeError("bedroom reached but player is stuck in a dialog")
