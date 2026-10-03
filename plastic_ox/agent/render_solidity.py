#!/usr/bin/env python3
"""Print an ASCII solidity grid for a converted map.

Reads the layout blockmap plus each tileset's metatile_attributes.bin and uses
plastic_ox/agent/remap_metatile_behaviors.py to resolve the behavior byte to a
name. Used when reviewing imported interiors for chokepoints and for the Ecruteak
Gym's shadow-Pokémon teleport warp maze.

    python3 plastic_ox/agent/render_solidity.py EcruteakCity_Gym_hns
"""
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'plastic_ox/agent'))
from remap_metatile_behaviors import build_mapping  # noqa: E402

BEHAVIORS = build_mapping()[0]

# Tiles whose behavior lets the player stand on them.
WALKABLE = {
    'MB_NORMAL', 'MB_WALK_INPLACE_DOWN', 'MB_WALK_INPLACE_UP',
    'MB_WALK_INPLACE_LEFT', 'MB_WALK_INPLACE_RIGHT',
}
SYMBOL = {
    'MB_DOOR': 'D', 'MB_ANIMATED_DOOR': 'D', 'MB_STATIC_DOOR': 'D',
    'MB_SOUTH_ARROW_WARP': 'v', 'MB_NORTH_ARROW_WARP': '^',
    'MB_EAST_ARROW_WARP': '>', 'MB_WEST_ARROW_WARP': '<',
    'MB_LEDGE_DOWN': 'J', 'MB_LEDGE_UP': 'j',
}


def tileset_attrs(symbol):
    headers = (ROOT / 'src/data/tilesets/headers.h').read_text()
    body = re.search(rf'const struct Tileset {re.escape(symbol)} =\n\{{(.*?)\n\}};', headers, re.S)
    path = re.search(r'metatileAttributes = (\w+)', body.group(1)).group(1)
    incbin = re.search(rf'{re.escape(path)}\[\] = INCBIN_U16\("([^"]+)"',
                       (ROOT / 'src/data/tilesets/metatiles.h').read_text()).group(1)
    raw = (ROOT / incbin).read_bytes()
    return struct.unpack('<' + 'H' * (len(raw) // 2), raw)


def behavior(attrs, metatile):
    if metatile < len(attrs):
        return BEHAVIORS[attrs[metatile] & 0xFF]
    return 'MB_NORMAL'


def main():
    name = sys.argv[1]
    data = json.loads((ROOT / f'data/maps/{name}/map.json').read_text())
    layout = {l['id']: l for l in json.loads((ROOT / 'data/layouts/layouts.json').read_text())['layouts']}[data['layout']]
    raw = (ROOT / layout['blockdata_filepath']).read_bytes()
    blocks = struct.unpack('<' + 'H' * (len(raw) // 2), raw)
    prim = tileset_attrs(layout['primary_tileset'])
    sec = tileset_attrs(layout['secondary_tileset'])
    base = int(sys.argv[2], 0) if len(sys.argv) > 2 else 640
    warps = {(w['x'], w['y']): i for i, w in enumerate(data['warp_events'])}
    objs = {(o['x'], o['y']): o['graphics_id'] for o in data['object_events']}
    for y in range(layout['height']):
        row = ''
        for x in range(layout['width']):
            block = blocks[y * layout['width'] + x]
            metatile = block & 0x3FF
            attrs = prim if metatile < base else sec
            b = behavior(attrs, metatile - base if metatile >= base else metatile)
            if b in SYMBOL:
                row += SYMBOL[b]
            elif b in WALKABLE:
                row += '.'
            elif b.startswith('MB_WATER') or b == 'MB_ICE':
                row += '~'
            else:
                row += '#'
        print(f'{y:3d} {row}')
    print('    ' + ''.join(str(x % 10) for x in range(layout['width'])))
    print('warps:', sorted(warps.items()))
    print('objects:', sorted(objs.items()))


if __name__ == '__main__':

    main()