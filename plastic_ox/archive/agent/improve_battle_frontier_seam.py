#!/usr/bin/env python3
"""Repair the native Battle Frontier outside west/east camera seam.

The two layouts use different secondary tilesets, so only East-native blocks
are written.  The west edge has two land openings (rows 5..8 and 40..54);
East previously exposed an extra opening at rows 9..14 and put the first
opening at elevation 3, making the reciprocal camera seam asymmetric.
"""
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / 'data/layouts/BattleFrontier_OutsideEast/map.bin'
WIDTH, HEIGHT = 72, 72


def main():
    data = bytearray(PATH.read_bytes())
    assert len(data) == WIDTH * HEIGHT * 2

    def get(y):
        return struct.unpack_from('<H', data, 2 * (y * WIDTH))[0]

    def put(y, value):
        struct.pack_into('<H', data, 2 * (y * WIDTH), value)

    # Keep the existing East artwork/metatile IDs but clear the elevation
    # bits, matching West's rows 5..8.  The low 12 bits are local to East.
    for y in range(5, 9):
        put(y, get(y) & 0x0FFF)

    # Close East's rows 9..14 with the adjacent local boundary block.  This
    # preserves East's own secondary tileset and leaves the next opening at
    # row 40, where both maps already agree.
    boundary = get(15)
    for y in range(9, 15):
        put(y, boundary)

    PATH.write_bytes(data)


if __name__ == '__main__':
    main()
