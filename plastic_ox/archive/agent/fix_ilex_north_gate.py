#!/usr/bin/env python3
"""Turn Ilex Forest's north threshold into a real, visually identical warp."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAP_PATH = ROOT / "data/layouts/IlexForest_hns/map.bin"
METATILES_PATH = ROOT / "data/tilesets/secondary/ilex_forest_hns/metatiles.bin"
ATTRS_PATH = ROOT / "data/tilesets/secondary/ilex_forest_hns/metatile_attributes.bin"
EVENTS_PATH = ROOT / "data/maps/IlexForest_hns/map.json"

WIDTH = 82
DOOR_X, DOOR_Y = 20, 15
HNS_PRIMARY_METATILES = 640
SOURCE_LOCAL_METATILE = 0x1C
WARP_LOCAL_METATILE = 0x3B
MB_NORTH_ARROW_WARP = 0x64


def main():
    metatiles = bytearray(METATILES_PATH.read_bytes())
    source = metatiles[SOURCE_LOCAL_METATILE * 16:(SOURCE_LOCAL_METATILE + 1) * 16]
    if len(source) != 16:
        raise ValueError("Ilex source threshold metatile is missing")
    expected_size = WARP_LOCAL_METATILE * 16
    if len(metatiles) == expected_size:
        metatiles.extend(source)
    elif len(metatiles) == expected_size + 16:
        if metatiles[expected_size:] != source:
            raise ValueError("Ilex warp metatile slot is already occupied")
    else:
        raise ValueError(f"unexpected Ilex metatile size: {len(metatiles)}")
    METATILES_PATH.write_bytes(metatiles)

    attrs = bytearray(ATTRS_PATH.read_bytes())
    attr_offset = WARP_LOCAL_METATILE * 2
    attrs[attr_offset:attr_offset + 2] = MB_NORTH_ARROW_WARP.to_bytes(2, "little")
    ATTRS_PATH.write_bytes(attrs)

    blockmap = bytearray(MAP_PATH.read_bytes())
    offset = (DOOR_Y * WIDTH + DOOR_X) * 2
    old = int.from_bytes(blockmap[offset:offset + 2], "little")
    expected_old = 0x3000 | HNS_PRIMARY_METATILES | SOURCE_LOCAL_METATILE
    expected_new = 0x3000 | HNS_PRIMARY_METATILES | WARP_LOCAL_METATILE
    if old not in (expected_old, expected_new):
        raise ValueError(f"unexpected Ilex north threshold block: {old:#06x}")
    blockmap[offset:offset + 2] = expected_new.to_bytes(2, "little")
    MAP_PATH.write_bytes(blockmap)

    events = json.loads(EVENTS_PATH.read_text())
    events["coord_events"] = [
        event for event in events.get("coord_events", [])
        if event.get("script") != "PoxRegion_ilex_route2_north"
    ]
    events["object_events"] = [
        event for event in events.get("object_events", [])
        if event.get("script") != "PoxRegion_ilex_route2_north_Sign"
    ]
    events["bg_events"] = [
        event for event in events.get("bg_events", [])
        if event.get("script") != "PoxRegion_ilex_route2_north_Sign"
    ]
    EVENTS_PATH.write_text(json.dumps(events, indent=2) + "\n")


if __name__ == "__main__":
    main()
