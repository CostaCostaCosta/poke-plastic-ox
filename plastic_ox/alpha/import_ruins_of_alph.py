#!/usr/bin/env python3
"""Import the Ruins of Alph: Route 36 gatehouse, the dig site, its chambers,
the research centre, the four Words Rooms and the hall beneath them.

Run once with `--donor`. It copies three HNS secondary tilesets
(`gTileset_RuinsOfAlph_Outside_Hns`, `gTileset_RuinsOfAlphWriting_Hns`,
`gTileset_RuinsOfAlph_B1F_Hns`), registers the layouts and maps, and writes
the converted maps to
`plastic_ox/alpha/ruins_of_alph/`. `ruins_of_alph.install` reapplies them, their
actors and the wild table after story generation without the donor.

Route: Route 36 south gate (55-57,25) -> gatehouse -> dig site -> four chamber
doors and the research centre. Behind each chamber's back room a doorway leads
to a Words Room, whose floor hole drops into the hall (B1F); the hall's stair
comes back up in the middle of the dig site. Warps only: the donor's seams to
Route 36 and Route 32 are not restored.

The donor reaches the west and south terraces only through Union Cave B1F,
which this build does not have. Here the pond between the main site and the
south terraces is crossed with Surf, two east-facing ledge tiles are repainted
as plain ground so the south terraces are two-way, and the two Union Cave
mouths lead to each other, which joins the west terrace to the rest.

Donor story is dropped: wandering Pokemon, Unown beams, lamps, both trainers,
the visitors and both hidden items outside; the gatehouse staff; the sliding
puzzles, their holes to B1F, item balls and statue text in the chambers; the
fossil reviver in the research centre; the visitors, wandering Unown, fossils,
GS Ball and wall text in the hall. The Route 32 gatehouse is not imported
(Route 32 is not in this region); its door is made solid.
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
LAB = 'RuinsOfAlph_Lab_hns'
B1F = 'RuinsOfAlph_B1F_hns'
WORDS = {n: f'RuinsOfAlph_WordsRoom{n}_hns' for n in (1, 2, 3, 4)}
MAPS = [GATE, OUTSIDE, CHAMBERS, LAB, B1F, *WORDS.values()]
GATE_ID = 'MAP_GATE_RUINS_OF_ALPH_ROUTE36_HNS'
OUTSIDE_ID = 'MAP_RUINS_OF_ALPH_OUTSIDE_HNS'
CHAMBERS_ID = 'MAP_RUINS_OF_ALPH_PUZZLE_AND_REWARD_CHAMBERS_HNS'
LAB_ID = 'MAP_RUINS_OF_ALPH_LAB_HNS'
B1F_ID = 'MAP_RUINS_OF_ALPH_B1F_HNS'
WORDS_ID = {n: f'MAP_RUINS_OF_ALPH_WORDS_ROOM{n}_HNS' for n in WORDS}

# (donor symbol, donor folder, our symbol, our folder, our C stem)
TILESETS = [
    ('gTileset_RuinsOfAlph_Outside_Hns', 'ruins_of_alph_outside_hns',
     'gTileset_RuinsOfAlph_Outside_Hns', 'ruins_of_alph_outside_hns', 'RuinsOfAlph_Outside_Hns'),
    ('gTileset_RuinsOfAlphWriting_Hns', 'ruins_of_alph_writing_hns',
     'gTileset_RuinsOfAlphWriting_Hns', 'ruins_of_alph_writing_hns', 'RuinsOfAlphWriting_Hns'),
    ('gTileset_RuinsOfAlph_B1F_Hns', 'ruins_of_alph_b1_f_hns',
     'gTileset_RuinsOfAlph_B1F_Hns', 'ruins_of_alph_b1f_hns', 'RuinsOfAlph_B1F_Hns'),
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
        (36, 16, LAB_ID, '0'),          # research centre
        (21, 21, B1F_ID, '0'),          # stair down to the hall
    ],
    CHAMBERS: [
        (20, 9, OUTSIDE_ID, '1'), (4, 9, OUTSIDE_ID, '2'),
        (4, 26, OUTSIDE_ID, '3'), (20, 26, OUTSIDE_ID, '4'),
        (21, 1, CHAMBERS_ID, '5'), (20, 43, CHAMBERS_ID, '4'),      # north chamber <-> its back room
        (5, 18, CHAMBERS_ID, '7'), (4, 60, CHAMBERS_ID, '6'),       # south-west
        (21, 18, CHAMBERS_ID, '9'), (20, 60, CHAMBERS_ID, '8'),     # south-east
        (5, 1, CHAMBERS_ID, '11'), (4, 43, CHAMBERS_ID, '10'),      # west
        # Back-room doorways into the Words Rooms (one-way: each room's only
        # way on is its floor hole).
        (4, 36, WORDS_ID[1], '1'), (5, 36, WORDS_ID[1], '1'),       # west
        (20, 36, WORDS_ID[4], '1'), (21, 36, WORDS_ID[4], '1'),     # north
        (4, 53, WORDS_ID[3], '1'), (5, 53, WORDS_ID[3], '1'),       # south-west
        (20, 53, WORDS_ID[2], '1'), (21, 53, WORDS_ID[2], '1'),     # south-east
    ],
    LAB: [(2, 7, OUTSIDE_ID, '7')],
    # Warps 1-4 are where the Words Room holes land; nothing walks into them.
    B1F: [(15, 16, OUTSIDE_ID, '8'), (5, 6, OUTSIDE_ID, '8'), (21, 6, OUTSIDE_ID, '8'),
          (5, 23, OUTSIDE_ID, '8'), (21, 23, OUTSIDE_ID, '8')],
    # Warp 0 is the hole, warp 1 the spot the chamber doorway arrives on.
    WORDS[1]: [(17, 14, B1F_ID, '1'), (10, 6, CHAMBERS_ID, '12')],
    WORDS[2]: [(17, 10, B1F_ID, '4'), (9, 5, CHAMBERS_ID, '18')],
    WORDS[3]: [(17, 10, B1F_ID, '3'), (10, 6, CHAMBERS_ID, '16')],
    WORDS[4]: [(17, 10, B1F_ID, '2'), (5, 2, CHAMBERS_ID, '14')],
}
MUSIC = {GATE: 'MUS_RG_ROUTE24', OUTSIDE: 'MUS_RG_ROUTE24', LAB: 'MUS_RG_ROUTE24'}
# The gatehouse stays on Route 36's section so the name shows on the way in.
SECTION = {GATE: 'MAPSEC_ROUTE_36'}

SAND = 0x30D9          # plain ground at elevation 3, no collision
# Whole block words to write: the two ledge tiles that become plain ground.
# The west chamber has no Regi, so its back wall stands open (0x308, the
# writing tileset's doorway, as the other three get from their tablets).
REPAINT = {OUTSIDE: {(18, 38): SAND, (22, 40): SAND}, CHAMBERS: {(5, 1): 0x0308}}
# Tiles that only get the solid bit: doors and floor features with no warp here.
SOLID = {
    OUTSIDE: [(38, 27)],                                # Route 32 gatehouse
    CHAMBERS: [(x, y) for y in (5, 22) for x in (4, 5, 20, 21)]       # sliding panels
              # A Regi's doorway stays shut until it is caught (the map's
              # ON_LOAD opens it); the west room's is open.
              + [(20, 36), (21, 36), (4, 53), (5, 53), (20, 53), (21, 53)],
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
        data.update(region='REGION_HOENN', region_map_section=SECTION.get(name, 'MAPSEC_RUINS_OF_ALPH'),
                    music=MUSIC.get(name, 'MUS_SEALED_CHAMBER'), weather='WEATHER_NONE',
                    connections=[] if name == OUTSIDE else None, object_events=[],
                    warp_events=[dict(x=x, y=y, elevation=0, dest_map=m, dest_warp_id=i)
                                 for x, y, m, i in WARPS[name]],
                    coord_events=[], bg_events=[], allow_escaping=False, allow_running=True,
                    show_map_name=name == OUTSIDE)
        if name in WORDS.values():
            data['map_type'] = 'MAP_TYPE_INDOOR'    # a one-room drop, not a location of its own
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
