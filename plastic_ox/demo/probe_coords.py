#!/usr/bin/env python3
"""Dump LIVE coord-event table of the current map via gMapHeader."""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import walk_demo as W
import walk_leg1 as L1
from walklib import GBA, K, boot_to_bedroom

g = GBA()
boot_to_bedroom(g)
L1.set_flag(g, 0x74)
navigate = L1.navigate

# fast path: house exit -> pallet -> lab door
g.walk("RIGHT", target=(10, 3)); g.walk("LEFT", target=(4, 3)); g.walk("DOWN", target=(4, 7))
g.hold(K.KEY_DOWN, 80); g.frame(90)
g.shot("pc_a.png")
g.walk("DOWN", target=(6, 10))
g.shot("pc_b.png")
g.shot("pc_c.png")
g.walk("RIGHT", target=(15, 10))
g.shot("pc_d.png")
g.shot("pc_e.png")
g.walk("DOWN", target=(16, 14))
g.shot("pc_f.png")
L1.enter_warp(g, (16, 13), "UP", (38, 3), "lab_in")
print("in:", g.describe())

mh = g.symbol_address("gMapHeader")
layout = g.u32(mh - 0x02000000)
events = g.u32(layout + 0x14) if False else None
# MapLayout: width/height/... ; MapHeader: layout@0, events@0x04 (per fieldmap.h comment)
ev = g.u32(mh - 0x02000000 + 0x04) if False else g.u32(g.u32(mh - 0x02000000) + 0)  # placeholder
# Use known offsets: MapHeader.layout ptr @ +0; MapEvents via header->events
hdr_base = mh - 0x02000000
layout_ptr = g.u32(hdr_base)
events_ptr = g.u32(hdr_base + 0x04)
print("layout", hex(layout_ptr), "events", hex(events_ptr))
obj = g.u32(events_ptr); obj_cnt = g.u8(events_ptr + 4)
warp = g.u32(events_ptr + 8); warp_cnt = g.u8(events_ptr + 12)
coord = g.u32(events_ptr + 16); coord_cnt = g.u8(events_ptr + 20)
bg = g.u32(events_ptr + 24); bg_cnt = g.u8(events_ptr + 28)
print("counts obj/warp/coord/bg:", obj_cnt, warp_cnt, coord_cnt, bg_cnt)
for i in range(coord_cnt):
    x = g.s16(coord + i * 12 + 0)
    y = g.s16(coord + i * 12 + 2)
    e = g.u8(coord + i * 12 + 4)
    trig = g.u16(coord + i * 12 + 6)
    idx = g.u16(coord + i * 12 + 8)
    sp = g.u32(coord + i * 12 + 12)
    print(f"coord{i}: ({x},{y}) e={e} trig={hex(trig)} idx={idx} script={hex(sp)}")
