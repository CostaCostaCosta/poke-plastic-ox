#!/usr/bin/env python3
"""Repair Dark Cave's border, water behaviors, and malformed entrance tile.

The HNS donor blockmap references out-of-range metatiles for its two exits.
Plastic Ox reserves 946 and 947 as dedicated ladder warps; keep those unique
behaviors, but give both the ordinary cave-floor art used by their landings.

An old bulk door repair also changed two shared shoreline metatiles to normal
ground.  Restore their donor water behavior without touching their layers.
"""

from pathlib import Path
import re
import struct


ROOT = Path(__file__).resolve().parents[2]
SECONDARY = ROOT / "data/tilesets/secondary/cave_default_hns"
LAYOUT = ROOT / "data/layouts/DarkCave_SouthSide_hns"


def behavior_value(name):
    value = 0
    for line in (ROOT / "include/constants/metatile_behaviors.h").read_text().splitlines():
        match = re.match(r"\s*(MB_\w+)\s*(?:=\s*(0x[0-9a-fA-F]+|\d+))?\s*,", line)
        if not match:
            continue
        value = int(match[2], 0) if match[2] else value
        if match[1] == name:
            return value
        value += 1
    raise ValueError(f"unknown metatile behavior: {name}")


def main():
    metatiles_path = SECONDARY / "metatiles.bin"
    attributes_path = SECONDARY / "metatile_attributes.bin"
    metatiles = bytearray(metatiles_path.read_bytes())
    attributes = bytearray(attributes_path.read_bytes())

    # Secondary metatile 641 is the plain walkable floor beside both exits.
    floor_art = metatiles[16:32]
    assert len(floor_art) == 16
    for metatile_id in (946, 947):
        offset = 16 * (metatile_id - 640)
        assert offset + 16 <= len(metatiles)
        metatiles[offset:offset + 16] = floor_art

    water = behavior_value("MB_OCEAN_WATER")
    for metatile_id in (811, 820):
        offset = 2 * (metatile_id - 640)
        attribute = struct.unpack_from("<H", attributes, offset)[0]
        struct.pack_into("<H", attributes, offset, (attribute & ~0xFF) | water)

    # The imported pool lost its HNS elevation bits during an earlier blockmap
    # repair.  At elevation 0 it matches the surrounding cave floor, allowing
    # the player to walk onto the water.  Restore the donor's water elevation
    # for every water-behavior placement, not just the two shoreline shapes.
    # Keep those shoreline shapes explicitly impassable as an extra guard.
    map_path = LAYOUT / "map.bin"
    blocks = bytearray(map_path.read_bytes())
    assert len(blocks) == 78 * 50 * 2
    for offset in range(0, len(blocks), 2):
        block = struct.unpack_from("<H", blocks, offset)[0]
        metatile_id = block & 0x03FF
        if metatile_id < 640:
            continue
        attribute = struct.unpack_from("<H", attributes, 2 * (metatile_id - 640))[0]
        if attribute & 0xFF == water:
            block = (block & ~0xF000) | 0x1000
            if metatile_id in (811, 820):
                block |= 0x0C00
            struct.pack_into("<H", blocks, offset, block)

    # The donor's filler block (657) can expose entrance-like animation along
    # the camera margin.  Use the solid cave-wall block already surrounding the
    # playable rooms, while retaining the normal 2x2 HNS border dimensions.
    border = struct.pack("<4H", *(673,) * 4)

    metatiles_path.write_bytes(metatiles)
    attributes_path.write_bytes(attributes)
    map_path.write_bytes(blocks)
    (LAYOUT / "border.bin").write_bytes(border)


if __name__ == "__main__":
    main()
