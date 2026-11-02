#!/usr/bin/env python3
"""Open Dark Cave's lower Route 2-to-Route 46 passage.

The HNS donor places a Rock Smash object at (23, 19) and a two-tile
west-jump ledge at (38, 19..20) in the otherwise continuous lower corridor.
Plastic Ox makes this corridor bidirectional and HM-free, so replace the
ledge with the adjacent cave floor.  The object event is removed in map.json.
"""

from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / "data/layouts/DarkCave_SouthSide_hns/map.bin"
WIDTH = 78
HEIGHT = 50
FLOOR_METATILE = 641


def main():
    blocks = bytearray(MAP.read_bytes())
    assert len(blocks) == WIDTH * HEIGHT * 2

    for x, y in ((38, 19), (38, 20)):
        offset = 2 * (y * WIDTH + x)
        old = struct.unpack_from("<H", blocks, offset)[0]
        assert old & 0x03FF in (680, FLOOR_METATILE), (x, y, old & 0x03FF)
        # Use the same elevation-3 walkable floor as both sides of the ledge.
        struct.pack_into("<H", blocks, offset, 0x3000 | FLOOR_METATILE)

    MAP.write_bytes(blocks)


if __name__ == "__main__":
    main()
