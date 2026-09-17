#!/usr/bin/env python3
"""Restore Rustboro's authored map after the obsolete row-30 Route 44 cut."""
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "data/layouts/RustboroCity/map.bin"
WIDTH = 40

data = bytearray(PATH.read_bytes())
for x, metatile in enumerate((0x0719, 0x05E6, 0x05F2, 0x31CF), start=36):
    struct.pack_into("<H", data, 2 * (30 * WIDTH + x), metatile)
PATH.write_bytes(data)
