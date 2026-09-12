#!/usr/bin/env python3
"""Give Dark Cave exits dedicated warp metatiles without changing shared floors.

HNS uses 640 primary metatiles and Emerald u16 attributes. Clone the existing
art into the cave secondary tileset, preserving every attribute except behavior.
Re-running this repair leaves already repaired exits untouched.
"""
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[2]


def main():
    value = 0
    behaviors = {}
    for line in (ROOT/'include/constants/metatile_behaviors.h').read_text().splitlines():
        match = re.match(r'\s*(MB_\w+)\s*(?:=\s*(0x[0-9a-fA-F]+|\d+))?\s*,', line)
        if match:
            value = int(match[2], 0) if match[2] else value
            behaviors[match[1]] = value
            value += 1
    # A ladder-style warp lands in place; door arrivals force a south step
    # into the rock immediately below the Route 31 mouth.
    behavior = behaviors['MB_LADDER']
    layouts = {l['id']: l for l in json.loads((ROOT/'data/layouts/layouts.json').read_text())['layouts']}
    name = 'DarkCave_SouthSide_hns'
    data = json.loads((ROOT/'data/maps'/name/'map.json').read_text())
    layout = layouts[data['layout']]
    assert layout['layout_version'] == 'hns'
    primary = ROOT/'data/tilesets/primary/johto_general_hns'
    secondary = ROOT/'data/tilesets/secondary/cave_default_hns'
    blocks_path = ROOT/layout['blockdata_filepath']
    blocks = bytearray(blocks_path.read_bytes())
    tiles = bytearray((secondary/'metatiles.bin').read_bytes())
    attrs = bytearray((secondary/'metatile_attributes.bin').read_bytes())
    assert len(tiles) % 16 == 0 and len(attrs) % 2 == 0
    assert len(attrs)//2 >= len(tiles)//16
    for warp in data['warp_events']:
        offset = 2*(warp['y']*layout['width']+warp['x'])
        block = struct.unpack_from('<H', blocks, offset)[0]
        mt = block & 1023
        source = primary if mt < 640 else secondary
        index = mt if mt < 640 else mt-640
        attr = struct.unpack_from('<H', (source/'metatile_attributes.bin').read_bytes(), index*2)[0]
        if attr & 0xFF == behavior:
            continue
        new_id = 640+len(tiles)//16
        assert new_id < 1024, 'secondary tileset is full'
        tiles.extend((source/'metatiles.bin').read_bytes()[index*16:(index+1)*16])
        attribute_offset = 2*(new_id-640)
        if attribute_offset == len(attrs):
            attrs.extend(b'\0\0')
        struct.pack_into('<H', attrs, attribute_offset, (attr & ~0xFF) | behavior)
        struct.pack_into('<H', blocks, offset, (block & ~1023) | new_id)
        print(f'{name} ({warp["x"]}, {warp["y"]}): metatile {mt} -> {new_id}, behavior {attr & 0xFF:#x} -> {behavior:#x}')
    (secondary/'metatiles.bin').write_bytes(tiles)
    (secondary/'metatile_attributes.bin').write_bytes(attrs)
    blocks_path.write_bytes(blocks)


if __name__ == '__main__':
    main()
