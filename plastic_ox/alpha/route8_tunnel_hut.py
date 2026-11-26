#!/usr/bin/env python3
"""Restore Route 8's Underground Path hut. Idempotent.

An earlier playtest fix cut a one-tile sand lane up the middle of the hut
(x=12, rows 14..18) and put a coordinate warp on it, so the player walked
through the building instead of into it. This puts the HNS hut back: cliff
foot, roof, wall and the animated door at (12,18), the same Kanto general
metatiles as Route 7's tunnel hut. region_v7.py points Route 8's warp 0 at
that door.

    python3 plastic_ox/alpha/route8_tunnel_hut.py
"""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Route 8 (Kanto_General_Hns + LavenderTown_Hns): metatile | collision << 10 | elevation << 12.
CELLS = {
    (12, 14): 0x047C,  # cliff foot, as (11,14)
    (12, 15): 0x073C,  # roof ridge, as (13,15)
    (12, 16): 0x044D,  # roof
    (12, 17): 0x0467,  # wall above the door
    (12, 18): 0x043D,  # animated door, as Route 7's (7,16)
}


def apply(layout_id, cells):
    layouts = json.loads((ROOT / 'data/layouts/layouts.json').read_text())['layouts']
    layout = next(l for l in layouts if l.get('id') == layout_id)
    path = ROOT / layout['blockdata_filepath']
    width = layout['width']
    blocks = list(struct.unpack(f'<{width * layout["height"]}H', path.read_bytes()))
    changed = 0
    for (x, y), value in cells.items():
        if blocks[y * width + x] != value:
            blocks[y * width + x] = value
            changed += 1
    path.write_bytes(struct.pack(f'<{len(blocks)}H', *blocks))
    print(f'{layout_id}: {changed} block(s) changed')


if __name__ == '__main__':
    apply('LAYOUT_ROUTE8_HNS', CELLS)
