#!/usr/bin/env python3
"""Make Pallet Town's Route 21 connection reachable only through water."""

from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[2]
ATTRS_PATH = ROOT / "data/tilesets/primary/kanto_general_hns/metatile_attributes.bin"
OCEAN_WATER = 0x15


def main():
    # fix_door_behaviors.py once changed this shared ocean metatile because an
    # imported warp happened to use it. It is water throughout the Kanto maps.
    attrs = bytearray(ATTRS_PATH.read_bytes())
    attribute = struct.unpack_from("<H", attrs, 2 * 0x12B)[0]
    struct.pack_into("<H", attrs, 2 * 0x12B, (attribute & 0xFF00) | OCEAN_WATER)
    ATTRS_PATH.write_bytes(attrs)


if __name__ == "__main__":
    main()
