#!/usr/bin/env python3
"""Import the Ruins of Alph: Route 36 gatehouse, the dig site and its chambers.

Run once with `--donor`. It copies two HNS secondary tilesets
(`gTileset_RuinsOfAlph_Outside_Hns`, `gTileset_RuinsOfAlphWriting_Hns`),
registers the three layouts and maps, and writes the converted maps to
`plastic_ox/alpha/ruins_of_alph/`. `ruins_of_alph.install` reapplies them, their
actors and the wild table after story generation without the donor.

Route: Route 36 south gate (55-57,25) -> gatehouse -> dig site -> four chamber
doors. Warps only: the donor's seams to Route 36 and Route 32 are not restored.

The donor reaches the west and south terraces only through Union Cave B1F,
which this build does not have. Here the pond between the main site and the
south terraces is crossed with Surf, two east-facing ledge tiles are repainted
as plain ground so the south terraces are two-way, and the two Union Cave
mouths lead to each other, which joins the west terrace to the rest.

Donor story is dropped: wandering Pokemon, Unown beams, lamps, both trainers,
the visitors and both hidden items outside; the gatehouse staff; the sliding
puzzles, holes to B1F, item balls, statue text and the reward-room doors to the
Words Rooms in the chambers. The lab, B1F, the Route 32 gatehouse and the Words
Rooms are not imported; their doors are made solid.
"""
import argparse
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from import_tin_tower import register_tileset, dump  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'plastic_ox/alpha/ruins_of_alph'
DONOR_DEFAULT = Path(os.environ.get('POX_HNS_DONOR', ROOT.parent / 'pokehns-expansion'))
GROUP = 'gMapGroup_PlasticOxInteriors'

GATE = 'Gate_RuinsOfAlph_Route36_hns'
OUTSIDE = 'RuinsOfAlph_Outside_hns'
CHAMBERS = 'RuinsOfAlph_PuzzleAndRewardChambers_hns'
MAPS = [GATE, OUTSIDE, CHAMBERS]
GATE_ID = 'MAP_GATE_RUINS_OF_ALPH_ROUTE36_HNS'
OUTSIDE_ID = 'MAP_RUINS_OF_ALPH_OUTSIDE_HNS'
CHAMBERS_ID = 'MAP_RUINS_OF_ALPH_PUZZLE_AND_REWARD_CHAMBERS_HNS'

# (donor symbol, donor folder, our symbol, our folder, our C stem)
TILESETS = [
    ('gTileset_RuinsOfAlph_Outside_Hns', 'ruins_of_alph_outside_hns',
     'gTileset_RuinsOfAlph_Outside_Hns', 'ruins_of_alph_outside_hns', 'RuinsOfAlph_Outside_Hns'),
    ('gTileset_RuinsOfAlphWriting_Hns', 'ruins_of_alph_writing_hns',
     'gTileset_RuinsOfAlphWriting_Hns', 'ruins_of_alph_writing_hns', 'RuinsOfAlphWriting_Hns'),
]

# Every converted warp, by map, in final order: (x, y, dest_map, dest_warp_id).
# Route 36 warp 2 is the middle lane (56,25); region_v7.py appends the three
# gate lanes after the National Park gate door.
WARPS = {
    GATE: [(7, 1, 'MAP_ROUTE36_HNS', '2'), (7, 9, OUTSIDE_ID, '0')],
    OUTSIDE: [
        (20, 6, GATE_ID, '1'),
        (28, 11, CHAMBERS_ID, '0'),     # north chamber (main site)
        (5, 23, CHAMBERS_ID, '1'),      # west chamber
        (7, 40, CHAMBERS_ID, '2'),      # south-west chamber
        (34, 42, CHAMBERS_ID, '3'),     # south-east chamber
        (13, 25, OUTSIDE_ID, '6'),      # crawlway, west mouth (donor: Union Cave B1F)
        (14, 36, OUTSIDE_ID, '5'),      # crawlway, south mouth (donor: Union Cave B1F)
    ],
    CHAMBERS: [
        (20, 9, OUTSIDE_ID, '1'), (4, 9, OUTSIDE_ID, '2'),
        (4, 26, OUTSIDE_ID, '3'), (20, 26, OUTSIDE_ID, '4'),
        (21, 1, CHAMBERS_ID, '5'), (20, 43, CHAMBERS_ID, '4'),      # north chamber <-> its back room
        (5, 18, CHAMBERS_ID, '7'), (4, 60, CHAMBERS_ID, '6'),       # south-west
        (21, 18, CHAMBERS_ID, '9'), (20, 60, CHAMBERS_ID, '8'),     # south-east
    ],
}
MUSIC = {GATE: 'MUS_RG_ROUTE24', OUTSIDE: 'MUS_RG_ROUTE24', CHAMBERS: 'MUS_SEALED_CHAMBER'}

SAND = 0x30D9          # plain ground at elevation 3, no collision
# Whole block words to write: the two ledge tiles that become plain ground.
REPAINT = {OUTSIDE: {(18, 38): SAND, (22, 40): SAND}}
# Tiles that only get the solid bit: doors and floor features with no warp here.
SOLID = {
    OUTSIDE: [(21, 21), (38, 27)],                      # B1F stair, Route 32 gatehouse
    CHAMBERS: [(x, y) for y in (5, 22) for x in (4, 5, 20, 21)]       # sliding panels
              + [(x, y) for y in (36, 53) for x in (4, 5, 20, 21)],   # Words Room doorways
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--donor', type=Path, default=DONOR_DEFAULT)
    donor = ap.parse_args().donor.resolve()

    for donor_symbol, donor_folder, symbol, folder, stem in TILESETS:
        assert donor_symbol == symbol
        register_tileset(donor, donor_folder, symbol, folder, stem)
        # The donor ships an unused flag animation with the outdoor set.
        shutil.rmtree(ROOT / 'data/tilesets/secondary' / folder / 'anim', ignore_errors=True)

    layouts_path = ROOT / 'data/layouts/layouts.json'
    layouts = json.loads(layouts_path.read_text())
    source_layouts = {l['id']: l for l in
                      json.loads((donor / 'data/layouts/layouts.json').read_text())['layouts'] if 'id' in l}
    groups_path = ROOT / 'data/maps/map_groups.json'
    groups = json.loads(groups_path.read_text())

    parts = __doc__.split('\n\n')
    manifest = {
        'donor': donor.name,
        'revision': subprocess.check_output(['git', '-C', str(donor), 'rev-parse', 'HEAD'], text=True).strip(),
        'group': GROUP,
        'tilesets': [{'donor': t[0], 'here': t[2], 'path': f'data/tilesets/secondary/{t[3]}'} for t in TILESETS],
        'route': parts[2].replace('\n', ' '),
        'access': parts[3].replace('\n', ' '),
        'events': parts[4].replace('\n', ' '),
        'repaint': {m: {f'{x},{y}': f'{v:#06x}' for (x, y), v in cells.items()} for m, cells in REPAINT.items()},
        'solid': {m: [list(c) for c in cells] for m, cells in SOLID.items()},
        'maps': {},
    }
    for name in MAPS:
        data = json.loads((donor / f'data/maps/{name}/map.json').read_text())
        layout = copy.deepcopy(source_layouts[data['layout']])
        layout.pop('game_version', None)
        layout.update(layout_version='hns', include_in_versions=['emerald'])
        for key in ['border_filepath', 'blockdata_filepath']:
            target = ROOT / layout[key]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(donor / layout[key], target)
        blocks = bytearray((ROOT / layout['blockdata_filepath']).read_bytes())
        for (x, y), word in REPAINT.get(name, {}).items():
            i = 2 * (y * layout['width'] + x)
            blocks[i:i + 2] = word.to_bytes(2, 'little')
        for x, y in SOLID.get(name, []):
            i = 2 * (y * layout['width'] + x)
            blocks[i + 1] |= 0x04           # collision bit 10 of the block word
        (ROOT / layout['blockdata_filepath']).write_bytes(bytes(blocks))
        if not any(l.get('id') == layout['id'] for l in layouts['layouts']):
            layouts['layouts'].append(layout)

        data.pop('game_version', None)
        data.update(region='REGION_HOENN', region_map_section='MAPSEC_ROUTE_36',
                    music=MUSIC[name], weather='WEATHER_NONE',
                    connections=[] if name == OUTSIDE else None, object_events=[],
                    warp_events=[dict(x=x, y=y, elevation=0, dest_map=m, dest_warp_id=i)
                                 for x, y, m, i in WARPS[name]],
                    coord_events=[], bg_events=[], allow_escaping=False, allow_running=True,
                    show_map_name=False)
        dump(BASE / f'{name}.json', data)
        manifest['maps'][name] = {'layout': layout['id']}
        if name not in groups[GROUP]:
            groups[GROUP].append(name)

    dump(layouts_path, layouts)
    dump(groups_path, groups)
    dump(BASE / 'source_manifest.json', manifest)
    print(json.dumps({k: v['layout'] for k, v in manifest['maps'].items()}, indent=1))


if __name__ == '__main__':
    main()
