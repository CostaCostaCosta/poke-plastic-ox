#!/usr/bin/env python3
"""Prepare the three missing v7 HNS routes; emit text edits as apply_patch.

--assets copies only missing binary/image assets. Existing imported assets are
never overwritten. Text changes are always emitted for review/application.
"""
import argparse
import copy
import difflib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
ROUTES = ['Route33_hns', 'Route44_hns', 'Route45_hns']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets', action='store_true')
    parser.add_argument(
        '--donor',
        type=Path,
        default=os.environ.get('POX_DONOR'),
        help='path to the pokehns-expansion checkout (or set POX_DONOR)',
    )
    args = parser.parse_args()
    if args.donor is None:
        parser.error('provide --donor PATH or set POX_DONOR')
    donor = args.donor.expanduser().resolve()
    if not (donor/'data/layouts/layouts.json').is_file():
        parser.error(f'donor checkout is missing data/layouts/layouts.json: {donor}')
    changes = {}
    layouts = json.loads((ROOT/'data/layouts/layouts.json').read_text())
    donor_layouts = {l['id']: l for l in json.loads((donor/'data/layouts/layouts.json').read_text())['layouts']}
    groups = json.loads((ROOT/'data/maps/map_groups.json').read_text())
    group = 'gMapGroup_PlasticOxV7'
    if group not in groups['group_order']:
        groups['group_order'].append(group)
    groups.setdefault(group, [])
    for name in ROUTES:
        data = json.loads((donor/f'data/maps/{name}/map.json').read_text())
        layout = copy.deepcopy(donor_layouts[data['layout']])
        layout.pop('game_version', None)
        layout['include_in_versions'] = ['emerald']
        if not any(l['id'] == layout['id'] for l in layouts['layouts']):
            layouts['layouts'].append(layout)
        for key in ['border_filepath', 'blockdata_filepath']:
            path = ROOT/layout[key]
            if not path.exists() and args.assets:
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(donor/layout[key], path)
        if name not in groups[group]:
            groups[group].append(name)
        if not (ROOT/f'data/maps/{name}/map.json').exists():
            data.pop('game_version', None)
            data['region'] = 'REGION_HOENN'
            data['music'] = 'MUS_RG_ROUTE3'
            data['connections'] = []
            data['warp_events'] = []
            data['coord_events'] = []
            # Preserve ordinary people and signs, author their new-region text.
            # Donor berry/monster/tree systems are not imported.
            data['object_events'] = [o for o in data['object_events'] if not any(s in o['graphics_id'] for s in ['MON_', 'TREE', 'BALL', 'BERRY'])]
            for obj in data['object_events']:
                obj.update(graphics_id='OBJ_EVENT_GFX_HIKER', movement_type='MOVEMENT_TYPE_FACE_DOWN',
                           trainer_type='TRAINER_TYPE_NONE', trainer_sight_or_berry_tree_id='0',
                           script='PoxRegion_TrailHint', flag='0')
            data['bg_events'] = [b for b in data.get('bg_events', []) if b.get('type') == 'sign']
            for obj in data['bg_events']:
                obj['script'] = 'PoxRegion_TrailHint'
            changes[f'data/maps/{name}/map.json'] = json.dumps(data, indent=2)+'\n'
            changes[f'data/maps/{name}/scripts.inc'] = f'{name}_MapScripts::\n\t.byte 0\n'
    # The other four route tilesets are already imported. Azalea is the only
    # new tileset, and retains its own geometry/graphics/palettes as a unit.
    asset = 'data/tilesets/secondary/azalea_town_hns'
    if args.assets and not (ROOT/asset).exists():
        shutil.copytree(donor/asset, ROOT/asset)
        sys.path.insert(0, str(ROOT/'plastic_ox/agent'))
        from remap_metatile_behaviors import build_mapping
        mapping = build_mapping()[2]
        path = ROOT/asset/'metatile_attributes.bin'
        raw = path.read_bytes()
        words = struct.unpack('<'+'H'*(len(raw)//2), raw)
        path.write_bytes(struct.pack('<'+'H'*len(words), *[(v&0xFF00)|mapping[v&255][0] for v in words]))
    symbol = 'AzaleaTown_Hns'
    donor_mt = (donor/'src/data/tilesets/metatiles.h').read_text()
    for path, addition in [
        ('include/tilesets.h', f'extern const struct Tileset gTileset_{symbol};\n'),
        ('src/data/tilesets/headers.h', f'\nconst struct Tileset gTileset_{symbol} = {{ .isCompressed = TRUE, .isSecondary = TRUE, .tiles = gTilesetTiles_{symbol}, .palettes = gTilesetPalettes_{symbol}, .metatiles = gMetatiles_{symbol}, .metatileAttributes = gMetatileAttributes_{symbol}, .callback = NULL }};\n'),
        ('src/data/tilesets/metatiles.h', '\n'+'\n'.join(line for line in donor_mt.splitlines() if f'_{symbol}[]' in line)+'\n'),
        ('src/data/tilesets/graphics.h', f'\nconst u32 gTilesetTiles_{symbol}[] = INCGFX_U32("{asset}/tiles.png", ".4bpp.fastSmol");\nconst u16 gTilesetPalettes_{symbol}[][16] = {{\n'+''.join(f'    INCGFX_U16("{asset}/palettes/{i:02d}.pal", ".gbapal"),\n' for i in range(13))+'};\n'),
    ]:
        old = (ROOT/path).read_text()
        if symbol not in old:
            changes[path] = old.replace('#endif //GUARD_tilesets_H', addition+'\n#endif //GUARD_tilesets_H') if path == 'include/tilesets.h' else old+addition
    changes['data/layouts/layouts.json'] = json.dumps(layouts, indent=2)+'\n'
    original = json.loads((ROOT/'data/maps/Route20_Frlg/map.json').read_text())
    original_layout = next(l for l in layouts['layouts'] if l['id']==original['layout'])
    blocks = struct.unpack('<'+'H'*(120*20), (ROOT/original_layout['blockdata_filepath']).read_bytes())
    for suffix,start,width,warp_index in [('West',0,66,0),('East',66,54,1)]:
        name='PlasticOx_Route20'+suffix
        layout=copy.deepcopy(original_layout)
        layout.update(id='LAYOUT_PLASTIC_OX_ROUTE20_'+suffix.upper(), name=name+'_Layout', width=width,
                      border_filepath=f'data/layouts/{name}/border.bin', blockdata_filepath=f'data/layouts/{name}/map.bin')
        if not any(l['id']==layout['id'] for l in layouts['layouts']):
            layouts['layouts'].append(layout)
        if args.assets:
            dest=ROOT/f'data/layouts/{name}'
            dest.mkdir(parents=True,exist_ok=True)
            cropped=[blocks[y*120+x] for y in range(20) for x in range(start,start+width)]
            (dest/'map.bin').write_bytes(struct.pack('<'+'H'*len(cropped),*cropped))
            shutil.copyfile(ROOT/original_layout['border_filepath'],dest/'border.bin')
        if name not in groups[group]:
            groups[group].append(name)
        if not (ROOT/f'data/maps/{name}/map.json').exists():
            data=copy.deepcopy(original)
            data.update(id='MAP_PLASTIC_OX_ROUTE20_'+suffix.upper(),name=name,layout=layout['id'],region='REGION_HOENN',connections=[],coord_events=[],object_events=[],bg_events=[])
            data['warp_events']=[copy.deepcopy(original['warp_events'][warp_index])]
            data['warp_events'][0]['x']-=start
            changes[f'data/maps/{name}/map.json']=json.dumps(data,indent=2)+'\n'
            changes[f'data/maps/{name}/scripts.inc']=f'{name}_MapScripts::\n\t.byte 0\n'
    changes['data/layouts/layouts.json'] = json.dumps(layouts, indent=2)+'\n'
    changes['data/maps/map_groups.json'] = json.dumps(groups, indent=2)+'\n'
    path = 'data/event_scripts.s'
    text = (ROOT/path).read_text()
    for name in ROUTES:
        line = f'\t.include "data/maps/{name}/scripts.inc"\n'
        if line not in text:
            text += line
    changes[path] = text
    print('*** Begin Patch')
    for path, text in changes.items():
        dest = ROOT/path
        if dest.exists():
            old = dest.read_text()
            if text == old:
                continue
            print('*** Update File: '+path)
            for line in list(difflib.unified_diff(old.splitlines(), text.splitlines(), n=3))[2:]:
                print('@@' if line.startswith('@@') else line)
        else:
            print('*** Add File: '+path)
            print('\n'.join('+'+line for line in text.splitlines()))
    print('*** End Patch')


if __name__ == '__main__':
    main()
