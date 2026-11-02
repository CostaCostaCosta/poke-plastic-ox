#!/usr/bin/env python3
"""Connect both National Park entrance landings to the park's walkable grounds."""

from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / "data/layouts/NationalPark_Normal_hns/map.bin"


def main():
    data = bytearray(MAP.read_bytes())
    offset = 2 * (27 * 48 + 38)
    old, new = 0x068E, 0x3011
    actual = struct.unpack_from("<H", data, offset)[0]
    if actual not in (old, new):
        raise ValueError(f"unexpected National Park gate tile: {actual:#06x}")
    struct.pack_into("<H", data, offset, new)
    MAP.write_bytes(data)


if __name__ == "__main__":
    main()
