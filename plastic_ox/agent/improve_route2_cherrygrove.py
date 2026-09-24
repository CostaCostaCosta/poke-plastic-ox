#!/usr/bin/env python3
"""Narrow Route 2's south edge to Cherrygrove's three-lane north gate.

Route 2 x=8..10 aligns with Cherrygrove x=33..35 at offset -25.  Only native
Route 2 tree blocks are used to close the two obsolete shoulder crossings.
"""
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "data/layouts/Route2_hns/map.bin"
WIDTH = 30
HEIGHT = 80


def main():
    data = bytearray(PATH.read_bytes())
    assert len(data) == WIDTH * HEIGHT * 2

    # Continue the existing two tree pairs into the former six-wide opening.
    # The retained road mouth is exactly x=8..10.
    for x, metatile in ((6, 0x0424), (7, 0x0423), (11, 0x0422)):
        struct.pack_into("<H", data, 2 * ((HEIGHT - 1) * WIDTH + x), metatile)

    PATH.write_bytes(data)


if __name__ == "__main__":
    main()
