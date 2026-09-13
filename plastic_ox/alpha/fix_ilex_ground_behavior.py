#!/usr/bin/env python3
"""Correct Ilex secondary metatile 0x28E from cave to tall grass."""
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "data/tilesets/secondary/ilex_forest_hns/metatile_attributes.bin"
INDEX = 0x28E - 0x280
MAP = ROOT / "data/layouts/IlexForest_hns/map.bin"

values = list(struct.unpack("<" + "H" * (PATH.stat().st_size // 2), PATH.read_bytes()))
values[INDEX] = (values[INDEX] & 0xFF00) | 2  # MB_TALL_GRASS
PATH.write_bytes(struct.pack("<" + "H" * len(values), *values))

# The imported (32,24) block resets the Emerald runtime when approached from
# the west. Replace it with a known-safe elevation-3 path block from the same
# map; copying the adjacent primary 0x02B block still resets the runtime.
blocks = list(struct.unpack("<" + "H" * (MAP.stat().st_size // 2), MAP.read_bytes()))
offset = 24 * 82 + 32
blocks[offset] = blocks[26 * 82 + 29]  # 0x3004, MB_NORMAL
MAP.write_bytes(struct.pack("<" + "H" * len(blocks), *blocks))
