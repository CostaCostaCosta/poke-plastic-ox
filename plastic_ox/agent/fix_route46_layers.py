#!/usr/bin/env python3
"""Keep Route 46's lower cliff/path graphics behind the player sprite."""

from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[2]
ATTRS = ROOT / "data/tilesets/primary/johto_north_east_hns/metatile_attributes.bin"
LAYER_MASK = 0xF000
COVERED = 0x1000

# These metatiles form the strip at (9, 34) and (0..9, 35) on Route 46.
ROUTE46_LOWER_CLIFF_METATILES = (0x14, 0x15, 0xD5, 0xDB)


def main():
    data = bytearray(ATTRS.read_bytes())
    for metatile_id in ROUTE46_LOWER_CLIFF_METATILES:
        offset = metatile_id * 2
        value = struct.unpack_from("<H", data, offset)[0]
        struct.pack_into("<H", data, offset, (value & ~LAYER_MASK) | COVERED)
    ATTRS.write_bytes(data)


if __name__ == "__main__":
    main()
