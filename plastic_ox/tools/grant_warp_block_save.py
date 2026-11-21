#!/usr/bin/env python3
"""Grant ITEM_WARP_BLOCK to both valid slots of an Emerald battery save."""

import argparse
import shutil
import struct
from pathlib import Path


SECTOR_SIZE = 0x1000
SECTORS_PER_SLOT = 14
SECTOR_DATA_SIZE = 3968
FOOTER_ID = 0xFF4
FOOTER_CHECKSUM = 0xFF6
SAVE_SIGNATURE = 0x08012025
SAVEBLOCK2_ENCRYPTION_KEY = 0xAC
SAVEBLOCK1_KEY_ITEMS = 0x5D8
KEY_ITEM_CAPACITY = 30
ITEM_WARP_BLOCK = 883


def checksum(data: bytearray, sector_offset: int) -> int:
    total = sum(struct.unpack_from("<992I", data, sector_offset)) & 0xFFFFFFFF
    return ((total >> 16) + total) & 0xFFFF


def sector_offsets(data: bytearray, slot: int) -> dict[int, int]:
    result = {}
    for physical in range(SECTORS_PER_SLOT):
        offset = (slot * SECTORS_PER_SLOT + physical) * SECTOR_SIZE
        sector_id, _, signature = struct.unpack_from("<HHI", data, offset + FOOTER_ID)
        if signature == SAVE_SIGNATURE:
            result[sector_id] = offset
    return result


def grant(data: bytearray, slot: int) -> str:
    sectors = sector_offsets(data, slot)
    if 0 not in sectors or 1 not in sectors:
        return "invalid slot"
    key = struct.unpack_from("<I", data, sectors[0] + SAVEBLOCK2_ENCRYPTION_KEY)[0]
    pocket = sectors[1] + SAVEBLOCK1_KEY_ITEMS
    empty = None
    for index in range(KEY_ITEM_CAPACITY):
        item, encrypted_quantity = struct.unpack_from("<HH", data, pocket + 4 * index)
        if item == ITEM_WARP_BLOCK:
            return "already present"
        if item == 0 and empty is None:
            empty = index
    if empty is None:
        raise RuntimeError(f"slot {slot} has no empty Key Items slot")
    struct.pack_into("<HH", data, pocket + 4 * empty, ITEM_WARP_BLOCK, 1 ^ (key & 0xFFFF))
    struct.pack_into("<H", data, sectors[1] + FOOTER_CHECKSUM, checksum(data, sectors[1]))
    return f"added at Key Items slot {empty}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("save", type=Path)
    args = parser.parse_args()
    original = args.save.read_bytes()
    if len(original) < 28 * SECTOR_SIZE:
        raise RuntimeError("save is too small for two Emerald save slots")
    backup = args.save.with_suffix(args.save.suffix + ".before-warp-block")
    if not backup.exists():
        shutil.copy2(args.save, backup)
    data = bytearray(original)
    results = [grant(data, slot) for slot in range(2)]
    args.save.write_bytes(data)
    print(f"{args.save}: {', '.join(results)}; backup: {backup}")


if __name__ == "__main__":
    main()
