#!/usr/bin/env python3
"""Rock-backed copies of the Lavender tower's crown metatiles. Idempotent.

LavenderTown_hns's layout starts at the tower's window rows, so the HNS dome,
spire and roof ledge (metatiles 0x2A5..0x2CF of gTileset_LavenderTown_Hns)
never appeared and the tower ended in a flat cut at the map's top edge.
src/plastic_ox_borders.c now draws the crown in the camera margin above the
tower (x 19..25, y -6..-1). The donor crown tiles stand on grass in their
bottom layer, which showed as green patches against the cliff that surrounds
the tower here, so the top three crown rows get copies whose grass quadrants
are replaced with the cliff-top rock of metatile 0x071. The copies are
appended after the tileset's last metatile; the originals stay untouched.

    python3 plastic_ox/alpha/lavender_tower_crown.py
"""
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECONDARY = ROOT / 'data/tilesets/secondary/lavender_town_hns'
PRIMARY = ROOT / 'data/tilesets/primary/kanto_general_hns'
PRIMARY_COUNT = 640
ROCK = 0x071                      # cliff top, primary
FIRST = 0x3CB                     # first free secondary slot (331 metatiles)
# Crown rows drawn over cliff: spire, dome top, dome middle, the dome
# base's outer corners.
SOURCES = [0x2A5, 0x2A6, 0x2A7,
           0x2A9, 0x2AA, 0x2AB, 0x2AC, 0x2AD, 0x2AE, 0x2AF,
           0x2B1, 0x2B2, 0x2B3, 0x2B4, 0x2B5, 0x2B6, 0x2B7,
           0x2B9, 0x2BF]
# Bottom-layer grass tiles of the donor crown.
GRASS = {0x001, 0x19D, 0x19E, 0x26C, 0x26D, 0x26E, 0x26F, 0x27C, 0x27D, 0x27E, 0x27F}
CROWN = {src: FIRST + i for i, src in enumerate(SOURCES)}


def entries(data, index):
    return list(struct.unpack_from('<8H', data, index * 16))


def main():
    rock = entries((PRIMARY / 'metatiles.bin').read_bytes(), ROCK)[4:]
    path = SECONDARY / 'metatiles.bin'
    data = bytearray(path.read_bytes())
    attr_path = SECONDARY / 'metatile_attributes.bin'
    attrs = bytearray(attr_path.read_bytes())
    for src, dst in CROWN.items():
        tiles = entries(data, src - PRIMARY_COUNT)
        for q in range(4):
            if tiles[q] & 0x3FF in GRASS:
                tiles[q] = rock[q]
        offset = (dst - PRIMARY_COUNT) * 16
        if len(data) < offset + 16:
            data.extend(bytes(offset + 16 - len(data)))
        struct.pack_into('<8H', data, offset, *tiles)
        a = (src - PRIMARY_COUNT) * 2
        b = (dst - PRIMARY_COUNT) * 2
        if len(attrs) < b + 2:
            attrs.extend(bytes(b + 2 - len(attrs)))
        attrs[b:b + 2] = attrs[a:a + 2]
    path.write_bytes(data)
    attr_path.write_bytes(attrs)
    print(f'{len(CROWN)} crown metatile(s) at 0x{FIRST:03X}..0x{FIRST + len(CROWN) - 1:03X}')


if __name__ == '__main__':
    main()
