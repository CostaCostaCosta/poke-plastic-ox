#!/usr/bin/env python3
"""Shape Rustboro's south road into the aligned Route 2 seam."""
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "data/layouts/RustboroCity/map.bin"
WIDTH = 40

data = bytearray(PATH.read_bytes())
road = (0x3110, 0x3111, 0x3112)
for y in range(57, 60):
    for x, block in zip(range(15, 18), road):
        struct.pack_into("<H", data, 2 * (y * WIDTH + x), block)

# Route 2's north edge only admits the three road tiles aligned with x=15..17.
# Close Rustboro's broad grass shoulders before the boundary so walking beside
# the road cannot cross into Route 2's trees.  The alternating blocks continue
# the city's existing two-row forest pattern.
trees = ((0x05D4, 0x05D5), (0x05DC, 0x05DD))
for y in range(58, 60):
    pair = trees[y & 1]
    for left in (12, 18):
        for x, block in zip(range(left, left + 2), pair):
            struct.pack_into("<H", data, 2 * (y * WIDTH + x), block)

# The native city layout also has an isolated grass block at the far-right
# edge.  With a south connection that block becomes an unintended crossing
# directly into Route 2 forest, so continue the adjacent boundary through it.
for y in (58, 59):
    struct.pack_into("<H", data, 2 * (y * WIDTH + 33), trees[y & 1][0])
PATH.write_bytes(data)
