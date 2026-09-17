#!/usr/bin/env python3
"""Replace the stray tall-grass strip immediately east of Route 29's gate."""

from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / "data/layouts/Route29_hns/map.bin"
WIDTH = 70


def main():
    blocks = list(struct.unpack("<2240H", MAP.read_bytes()))
    # Continue the neighboring tree pattern from the same-parity column.
    for y in range(15):
        blocks[y * WIDTH + 38] = blocks[y * WIDTH + 40]
    MAP.write_bytes(struct.pack("<2240H", *blocks))


if __name__ == "__main__":
    main()
