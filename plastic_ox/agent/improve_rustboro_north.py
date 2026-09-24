#!/usr/bin/env python3
"""Reproduce the Rustboro / Route 24 road throat using each layout's own blocks.

Rustboro (19..22, 0) aligns with Route 24 (16..19, 21), offset +3.
Run before build_story.py; no imported metatile IDs cross tileset families.
"""
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]


def patch_layout(name, width, height, edits):
    path = ROOT / 'data/layouts' / name / 'map.bin'
    data = bytearray(path.read_bytes())
    assert len(data) == width * height * 2
    for (x, y), block in edits.items():
        assert 0 <= x < width and 0 <= y < height
        struct.pack_into('<H', data, 2 * (y * width + x), block)
    path.write_bytes(data)


def main():
    edits = {}
    # Continue the city's own stone road through the former grass cul-de-sac.
    for y in range(7):
        for x in range(19, 23):
            edits[x, y] = 0x32BB
    # Shift the east forest edge one block west: retain complete tree pairs
    # and finish the last row with the city's native tree bases.
    for y in range(5):
        pair = (0x05DC, 0x05DD) if y % 2 == 0 else (0x05D4, 0x05D5)
        for x in range(23, 40):
            edits[x, y] = pair[(x - 23) % 2]
    edits[23, 4], edits[24, 4] = 0x05E4, 0x05E5
    patch_layout('RustboroCity', 40, 60, edits)
    # The eastern riverside footpath is not another city entrance. Continue
    # its existing vertical fence across the southern end, using local rails.
    patch_layout('Route24_hns', 30, 22,
                 {(x, 21): 0x04F4 for x in range(24, 27)})


if __name__ == '__main__':
    main()
