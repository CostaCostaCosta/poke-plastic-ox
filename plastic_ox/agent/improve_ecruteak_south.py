#!/usr/bin/env python3
"""Join Route 37 columns 16..19 to Ecruteak 32..35 with offset -16/+16.

Use the layouts' shared Ecruteak tileset: one city arch, a continuous stone
road, complete forest shoulders, and no old opening at city columns 0..3.
"""
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]


def main():
    path = ROOT / 'data/layouts/Route37_hns/map.bin'
    blocks = list(struct.unpack('<' + 'H' * (44 * 41), path.read_bytes()))
    for y in range(12):
        for x in range(16, 20):
            block = 0x32D4 if y < 3 else (0x31C0, 0x31C1, 0x31C1, 0x31C2)[x - 16]
            blocks[y * 44 + x] = block
    path.write_bytes(struct.pack('<' + 'H' * len(blocks), *blocks))

    path = ROOT / 'data/layouts/EcruteakCity_hns/map.bin'
    blocks = list(struct.unpack('<' + 'H' * (66 * 61), path.read_bytes()))
    # Retire the donor's invisible south-arrow warp at the arch's foot.
    for x in (33, 34):
        blocks[55 * 66 + x] = 0x32D4
    for y in range(56, 61):
        for x in range(32, 36):
            blocks[y * 66 + x] = 0x32D4
    # Close the earlier seam repair's opening on the far west edge.
    for y in range(59, 61):
        for x in range(4):
            blocks[y * 66 + x] = blocks[y * 66 + 26 + x % 2]
    path.write_bytes(struct.pack('<' + 'H' * len(blocks), *blocks))


if __name__ == '__main__':
    main()
