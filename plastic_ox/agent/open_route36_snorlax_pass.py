#!/usr/bin/env python3
"""Restore Route 36's three-way junction and the east path through Snorlax.

The lower east lane let players walk around Sudowoodo. Restore the donor's
tree line at y=20 so Sudowoodo at (39, 19) blocks both north and east; reopen
the donor road at (43, 19) for Snorlax to guard the east branch.
Run from any working directory.
"""

from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / "data/layouts/Route36_hns/map.bin"
WIDTH = 66
EDITS = {
    (43, 18): (0x0405, 0x3001),
    (43, 19): (0x0405, 0x3009),
    (40, 20): (0x3000, 0x0405),
    (41, 20): (0x3001, 0x0405),
    (42, 20): (0x3000, 0x0405),
    (43, 20): (0x3001, 0x0405),
    (44, 20): (0x3000, 0x0405),
}


def main():
    data = bytearray(MAP.read_bytes())
    for (x, y), (old, new) in EDITS.items():
        offset = 2 * (y * WIDTH + x)
        actual = struct.unpack_from("<H", data, offset)[0]
        if actual not in (old, new):
            raise ValueError(f"unexpected Route 36 tile at {(x, y)}: {actual:#06x}")
        struct.pack_into("<H", data, offset, new)
    MAP.write_bytes(data)


if __name__ == "__main__":
    main()
