#!/usr/bin/env python3
"""Close Route 7's grass patch behind a Cut tree. Idempotent.

The patch at (11..18, 4..9) used to open onto the junction along five tiles of
row 10 (x 11..15). This continues the low fence that already runs along row 10
(x 2..5 and 8..10) across that gap, leaving one ground tile at (13,10) where
region_v7.py places a cuttable tree. Without Cut the grass is out of reach;
after Cut the gap is a normal path.

    python3 plastic_ox/alpha/route7_cut_hedge.py
"""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Route 7 (Kanto_General_Hns + CeladonCity_Hns): metatile | collision << 10 | elevation << 12.
CELLS = {
    (11, 10): 0x0487,  # fence, as (3,10)
    (12, 10): 0x04B1,  # fence end, as (5,10)
    # (13,10) stays ground (0x3001): the Cut tree stands here.
    (14, 10): 0x04B0,  # fence end, as (2,10)
    (15, 10): 0x0487,  # fence, against the wall at (16,10)
}
CUT_TREE = (13, 10)


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
    apply('LAYOUT_ROUTE7_HNS', CELLS)
