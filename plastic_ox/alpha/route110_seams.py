#!/usr/bin/env python3
"""Layout edits behind Route 110's three walk-across seams. Idempotent.

  Fortree City east  <-> Route 110 north-west   (right/left, offset 5)
  Route 36 east      <-> Route 110 west spur    (right/left, offset -49)
  Route 110 south    <-> Lavender Town north    (down/up, offset 3)

Route 110's old north mouth (the Mauville exit) is closed with a tree line and
a four-lane forest corridor is cut west to the map edge so it lines up with
Fortree's east clearing (rows 7..10). The sand paths are trimmed or extended
so the block that the camera margin repeats at each seam is a plain one.
Connections, gates and ports live in region_v7.py (SEAM_TRAILS); the forest
drawn beyond the edges comes from src/plastic_ox_borders.c.

    python3 plastic_ox/alpha/route110_seams.py
"""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Route 110 (HoennOrasGeneral): metatile | collision << 10 | elevation << 12.
GRASS, TREE, TREE_BASE, TREE_TOP = 0x3001, 0x04C7, 0x0417, 0x300E
SHORE_N = 0x1189
SAND_SW, SAND_SE = 0x3128, 0x312A


def route110():
    cells = {}
    for x in range(19):
        cells[x, 0] = TREE
        cells[x, 1] = TREE_BASE
    for y in (2, 3, 4):
        for x in range(11):
            cells[x, y] = GRASS
    for x in range(9):
        cells[x, 5] = TREE_TOP
    cells[9, 5] = cells[10, 5] = GRASS
    # The west column was a strip of shore; forest now runs to the map edge.
    for y in range(6, 19):
        cells[0, y] = TREE
    cells[0, 19] = TREE_BASE
    cells[0, 20] = SHORE_N
    # End the sand one row short of the Lavender seam.
    cells[17, 98], cells[18, 98] = SAND_SW, SAND_SE
    cells[17, 99] = cells[18, 99] = GRASS
    return cells


def route36():
    # Carry the sand road through the last column instead of capping it.
    return {(65, 19): 0x30D4, (65, 20): 0x30DC, (65, 21): 0x30E4}


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
    apply('LAYOUT_ROUTE110', route110())
    apply('LAYOUT_ROUTE36_HNS', route36())
