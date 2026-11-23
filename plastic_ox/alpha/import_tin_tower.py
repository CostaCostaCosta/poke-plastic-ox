#!/usr/bin/env python3
"""Import Bellchime Trail and a two-storey Tin Tower (1F and the daytime roof).

Run once with `--donor`. It copies two HNS secondary tilesets
(`gTileset_BellchimeTrail_Hns`, and the tower's, which the donor calls
`gTileset_PowerPlant_GeneratorRoom_Hns` and this ROM `gTileset_TinTower_Hns`),
registers the three layouts and maps, and writes the converted maps to
`plastic_ox/alpha/tin_tower/`. `tin_tower.install` reapplies them, the sage
office door and the Moltres sage after story generation without the donor.

Route: Ecruteak sage office (north door) -> Bellchime Trail -> Tin Tower 1F ->
ladder -> roof. The donor's 2F-9F are not imported: the tower is kept short on
purpose (and the donor's 3F-6F could not be climbed anyway; every ladder there
sits in its own sealed pocket).

Donor story is dropped: wandering Pokémon, lamps, Morty and the item ball on
the trail; the trail's door coord trigger and its south seam into Ecruteak
(the trail is reached only through the office); the 1F sages and tower beam;
the Ho-Oh/Kimono roof scene; every statue sign.
"""
import argparse
import copy
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'plastic_ox/alpha/tin_tower'
DONOR_DEFAULT = Path(os.environ.get('POX_HNS_DONOR', ROOT.parent / 'pokehns-expansion'))
GROUP = 'gMapGroup_PlasticOxInteriors'

TRAIL = 'BellchimeTrail_hns'
FLOOR = 'TinTower_1F_hns'
ROOF = 'TinTower_RoofDay_hns'
MAPS = [TRAIL, FLOOR, ROOF]

# (donor symbol, donor folder, our symbol, our folder, our C stem)
TILESETS = [
    ('gTileset_BellchimeTrail_Hns', 'bellchime_trail_hns',
     'gTileset_BellchimeTrail_Hns', 'bellchime_trail_hns', 'BellchimeTrail_Hns'),
    ('gTileset_PowerPlant_GeneratorRoom_Hns', 'power_plant_generator_room_hns',
     'gTileset_TinTower_Hns', 'tin_tower_hns', 'TinTower_Hns'),
]

OFFICE = 'MAP_ECRUTEAK_CITY_SAGE_OFFICE2_HNS'
OFFICE_DOOR = '1'   # tin_tower.install appends the office's north door as warp 1
# Every converted warp, by map, in final order: (x, y, dest_map, dest_warp_id).
WARPS = {
    TRAIL: [(8, 36, OFFICE, OFFICE_DOOR), (8, 37, OFFICE, OFFICE_DOOR), (8, 38, OFFICE, OFFICE_DOOR),
            (35, 41, 'MAP_TIN_TOWER_1F_HNS', '0')],
    FLOOR: [(9, 17, 'MAP_BELLCHIME_TRAIL_HNS', '3'), (9, 4, 'MAP_TIN_TOWER_ROOF_DAY_HNS', '0')],
    ROOF: [(10, 14, 'MAP_TIN_TOWER_1F_HNS', '1')],
}
MUSIC = {TRAIL: 'MUS_MT_PYRE_EXTERIOR', FLOOR: 'MUS_MT_PYRE', ROOF: 'MUS_MT_PYRE_EXTERIOR'}
# The trail's tower door carries the solid bit (HNS opens it with a coord
# script); clear it so the door works as an ordinary step-in warp here.
CLEAR_COLLISION = {TRAIL: [(35, 41)]}


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n')


def insert_after(path, anchor_re, block, marker):
    text = path.read_text()
    if marker in text:
        return
    match = re.search(anchor_re, text, re.S)
    if not match:
        raise SystemExit(f'{path}: anchor {anchor_re!r} not found')
    path.write_text(text[:match.end()] + block + text[match.end():])


def register_tileset(donor, donor_folder, symbol, folder, stem):
    dst = ROOT / 'data/tilesets/secondary' / folder
    if not (dst / 'metatile_attributes.bin.orig').exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(donor / 'data/tilesets/secondary' / donor_folder, dst,
                        ignore=shutil.ignore_patterns('*.pla'))
        # Behaviour bytes use the hns enum; rewrite by name. The tool walks every
        # *_hns tileset and leaves a .orig on any without one; keep only ours.
        before = set(ROOT.glob('data/tilesets/*/*_hns/metatile_attributes.bin.orig'))
        subprocess.check_call([sys.executable, str(ROOT / 'plastic_ox/tools/remap_metatile_behaviors.py')],
                              cwd=ROOT, env=dict(os.environ, POX_HNS_DONOR=str(donor)),
                              stdout=subprocess.DEVNULL)
        for path in set(ROOT.glob('data/tilesets/*/*_hns/metatile_attributes.bin.orig')) - before:
            if path.parent != dst:
                path.unlink()
    pals = ''.join(f'    INCGFX_U16("data/tilesets/secondary/{folder}/palettes/{i:02}.pal", ".gbapal"),\n'
                   for i in range(13))
    insert_after(ROOT / 'src/data/tilesets/graphics.h',
                 r'const u16 gTilesetPalettes_EcruteakTheater_Hns\[\]\[16\] =\n\{.*?\n\};\n',
                 f'\nconst u32 gTilesetTiles_{stem}[] = INCGFX_U32("data/tilesets/secondary/{folder}/tiles.png", ".4bpp.fastSmol");\n'
                 f'\nconst u16 gTilesetPalettes_{stem}[][16] =\n{{\n{pals}}};\n',
                 f'gTilesetTiles_{stem}[]')
    insert_after(ROOT / 'src/data/tilesets/metatiles.h',
                 r'const u16 gMetatileAttributes_EcruteakTheater_Hns\[\] = [^\n]*\n',
                 f'\nconst u16 gMetatiles_{stem}[] = INCBIN_U16("data/tilesets/secondary/{folder}/metatiles.bin");\n'
                 f'const u16 gMetatileAttributes_{stem}[] = INCBIN_U16("data/tilesets/secondary/{folder}/metatile_attributes.bin");\n',
                 f'gMetatiles_{stem}[]')
    insert_after(ROOT / 'src/data/tilesets/headers.h',
                 r'const struct Tileset gTileset_EcruteakTheater_Hns =\n\{.*?\n\};\n',
                 f'\nconst struct Tileset {symbol} =\n{{\n'
                 f'    .isCompressed = TRUE,\n    .isSecondary = TRUE,\n'
                 f'    .tiles = gTilesetTiles_{stem},\n    .palettes = gTilesetPalettes_{stem},\n'
                 f'    .metatiles = gMetatiles_{stem},\n    .metatileAttributes = gMetatileAttributes_{stem},\n'
                 f'    .callback = NULL,\n}};\n',
                 f'struct Tileset {symbol} =')
    insert_after(ROOT / 'include/tilesets.h',
                 r'extern const struct Tileset gTileset_EcruteakTheater_Hns;\n',
                 f'extern const struct Tileset {symbol};\n', f'Tileset {symbol};')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--donor', type=Path, default=DONOR_DEFAULT)
    donor = ap.parse_args().donor.resolve()

    renamed = {}
    for donor_symbol, donor_folder, symbol, folder, stem in TILESETS:
        register_tileset(donor, donor_folder, symbol, folder, stem)
        renamed[donor_symbol] = symbol

    layouts_path = ROOT / 'data/layouts/layouts.json'
    layouts = json.loads(layouts_path.read_text())
    source_layouts = {l['id']: l for l in
                      json.loads((donor / 'data/layouts/layouts.json').read_text())['layouts'] if 'id' in l}
    groups_path = ROOT / 'data/maps/map_groups.json'
    groups = json.loads(groups_path.read_text())

    manifest = {
        'donor': str(donor),
        'revision': subprocess.check_output(['git', '-C', str(donor), 'rev-parse', 'HEAD'], text=True).strip(),
        'group': GROUP,
        'tilesets': [{'donor': t[0], 'here': t[2], 'path': f'data/tilesets/secondary/{t[3]}'} for t in TILESETS],
        'route': __doc__.split('\n\n')[2].replace('\n', ' '),
        'events': __doc__.split('\n\n')[3].replace('\n', ' '),
        'maps': {},
    }
    for name in MAPS:
        data = json.loads((donor / f'data/maps/{name}/map.json').read_text())
        layout = copy.deepcopy(source_layouts[data['layout']])
        layout.pop('game_version', None)
        layout.update(layout_version='hns', include_in_versions=['emerald'],
                      secondary_tileset=renamed.get(layout['secondary_tileset'], layout['secondary_tileset']))
        for key in ['border_filepath', 'blockdata_filepath']:
            target = ROOT / layout[key]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(donor / layout[key], target)
        blocks = bytearray((ROOT / layout['blockdata_filepath']).read_bytes())
        for x, y in CLEAR_COLLISION.get(name, []):
            i = 2 * (y * layout['width'] + x)
            blocks[i + 1] &= ~0x0C          # bits 10-11 of the block word
        (ROOT / layout['blockdata_filepath']).write_bytes(bytes(blocks))
        if not any(l.get('id') == layout['id'] for l in layouts['layouts']):
            layouts['layouts'].append(layout)

        data.pop('game_version', None)
        data.update(region='REGION_HOENN', region_map_section='MAPSEC_ECRUTEAK_CITY',
                    music=MUSIC[name], weather='WEATHER_NONE', connections=[], object_events=[],
                    warp_events=[dict(x=x, y=y, elevation=0, dest_map=m, dest_warp_id=i)
                                 for x, y, m, i in WARPS[name]],
                    coord_events=[], bg_events=[], allow_escaping=False, allow_running=True,
                    show_map_name=name == TRAIL)
        dump(BASE / f'{name}.json', data)
        (BASE / f'{name}.inc').write_text(f'{name}_MapScripts::\n\t.byte 0\n')
        manifest['maps'][name] = {'layout': layout['id']}
        if name not in groups[GROUP]:
            groups[GROUP].append(name)

    dump(layouts_path, layouts)
    dump(groups_path, groups)
    dump(BASE / 'source_manifest.json', manifest)
    print(json.dumps({k: v['layout'] for k, v in manifest['maps'].items()}, indent=1))


if __name__ == '__main__':
    main()
