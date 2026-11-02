#!/usr/bin/env python3
"""Import the remaining Ecruteak City HNS interiors and gatehouses.

The city map itself (`EcruteakCity_hns`) was already imported by
`plastic_ox/agent/import_wave3.py`; this importer adds the ten remaining donor
rooms and rewires the city's door warps onto them. Run once with `--donor`;
`ecruteak.install` reapplies the converted rooms after story generation
without needing the donor checkout.
"""
import argparse
import collections
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'plastic_ox/alpha/ecruteak'
DONOR_DEFAULT = Path('/home/eddie/repos/pokehns-expansion')
CITY = 'EcruteakCity_hns'

MAPS = [
    'EcruteakCity_Gym_hns',
    'EcruteakCity_House1_hns',
    'EcruteakCity_House2_hns',
    'EcruteakCity_Mart_hns',
    'EcruteakCity_PokemonCenter_hns',
    'EcruteakCity_SageOffice1_hns',
    'EcruteakCity_SageOffice2_hns',
    'EcruteakCity_Theater_hns',
    'Gate_EcruteakCity_Route38_hns',
    'Gate_EcruteakCity_Route42_hns',
]

# MUS_HG_* -> MUS_RG_*, per plastic_ox/alpha/IMPORT_GUIDE.md section 4.
MUSIC = {
    'EcruteakCity_Gym_hns': 'MUS_RG_GYM',
    'EcruteakCity_House1_hns': 'MUS_RG_CELADON',
    'EcruteakCity_House2_hns': 'MUS_RG_CELADON',
    'EcruteakCity_Mart_hns': 'MUS_RG_CELADON',
    'EcruteakCity_PokemonCenter_hns': 'MUS_RG_POKE_CENTER',
    'EcruteakCity_SageOffice1_hns': 'MUS_RG_LAVENDER',
    'EcruteakCity_SageOffice2_hns': 'MUS_RG_LAVENDER',
    'EcruteakCity_Theater_hns': 'MUS_RG_CELADON',
    'Gate_EcruteakCity_Route38_hns': 'MUS_RG_ROUTE24',
    'Gate_EcruteakCity_Route42_hns': 'MUS_RG_ROUTE24',
}

# Donor object-event sprites we do not import fall back to the nearest sprite
# this ROM already carries. `BILL_HNS` and every `MON_BASE+SPECIES_*` ghost are
# dropped outright (donor story / party graphics).
GFX_MAP = {
    'BALDING_MAN': 'MAN_3',
    'CHANNELER': 'LASS',
    'GENTLEMAN': 'GENTLEMAN',
    'GYM_GUY': 'GYM_GUY',
    'HIKER': 'HIKER',
    'LITTLE_BOY': 'BOY_1',
    'MART_EMPLOYEE': 'MART_EMPLOYEE',
    'MORTY': 'LASS',
    'NURSE': 'NURSE_FRLG',
    'NURSE_CHANSEY': 'CHANSEY',
    'OFFICER': 'POLICEMAN',
    'OLD_WOMAN': 'WOMAN_1',
    'ROCKET_M': 'MAN_1',
    'SAGE': 'OLD_MAN',
    'SUPER_NERD': 'MAN_5',
    'TWIN': 'LITTLE_GIRL',
    'WOMAN_2': 'WOMAN_2',
    'WORKER_M': 'MAN_1',
}
DROP_GFX = ('MON_BASE', 'BILL_HNS', 'POKE_BALL', 'ITEM_BALL', 'ROCKET')

# Warp conversion per map. `dynamic` maps a donor warp index onto the converted
# city-facing exit (MAP_DYNAMIC returns the player to the door they came in
# through). `drop` removes donor warps whose destination map is absent here.
WARP_PLAN = {
    'EcruteakCity_Gym_hns': {},                       # self-referential shadow teleports
    'EcruteakCity_House1_hns': {'dynamic': {0}},
    'EcruteakCity_House2_hns': {'dynamic': {0}},
    'EcruteakCity_Mart_hns': {'dynamic': {0}},
    'EcruteakCity_PokemonCenter_hns': {'dynamic': {0}},
    'EcruteakCity_SageOffice1_hns': {'dynamic': {0}},
    'EcruteakCity_SageOffice2_hns': {'drop': {0}},    # 0 led to BELLCHIME_TRAIL
    'EcruteakCity_Theater_hns': {'dynamic': {0}},
    'Gate_EcruteakCity_Route38_hns': {'dynamic': {0}},
    'Gate_EcruteakCity_Route42_hns': {'dynamic': {0}, 'drop': {1}},  # 1 led to ROUTE 42
}

# City doors, in donor warp order. The three already-indexed doors keep their
# index so saved dynamic warps and story warps stay valid; the rest are appended.
CITY_WARPS = {
    0: dict(x=39, y=47, dest_map='MAP_ECRUTEAK_CITY_POKEMON_CENTER_HNS', dest_warp_id='0'),
    1: dict(x=48, y=40, dest_map='MAP_ECRUTEAK_CITY_MART_HNS', dest_warp_id='0'),
    2: dict(x=19, y=40, dest_map='MAP_ECRUTEAK_CITY_HOUSE1_HNS', dest_warp_id='0'),
}
CITY_DOORS = [
    dict(x=39, y=40, dest_map='MAP_ECRUTEAK_CITY_THEATER_HNS', dest_warp_id='0'),
    dict(x=20, y=48, dest_map='MAP_ECRUTEAK_CITY_GYM_HNS', dest_warp_id='0'),
    dict(x=28, y=47, dest_map='MAP_ECRUTEAK_CITY_HOUSE2_HNS', dest_warp_id='0'),
    dict(x=39, y=22, dest_map='MAP_ECRUTEAK_CITY_SAGE_OFFICE1_HNS', dest_warp_id='0'),
    dict(x=36, y=16, dest_map='MAP_ECRUTEAK_CITY_SAGE_OFFICE2_HNS', dest_warp_id='0'),
    dict(x=8, y=35, dest_map='MAP_GATE_ECRUTEAK_CITY_ROUTE38_HNS', dest_warp_id='0'),
    dict(x=55, y=42, dest_map='MAP_GATE_ECRUTEAK_CITY_ROUTE42_HNS', dest_warp_id='0'),
]

# ROUTE 38 lost its ECRUTEAK seam in wave 3 (the donor uses a "left" connection
# there); the gatehouse replaces it with an explicit warp pair.
ROUTE38_WARP = dict(x=43, y=16, elevation=0,
                    dest_map='MAP_GATE_ECRUTEAK_CITY_ROUTE38_HNS', dest_warp_id='1')

# ROUTE 42 is not in this ROM yet (no map, no MAPSEC_ROUTE_42), so the ROUTE 42
# gatehouse is a dead end: its outer door is dropped and it charts under
# ECRUTEAK CITY. The ROUTE 38 gate keeps MAPSEC_ROUTE_38 because that route is
# here and the gate is its city end.
REGION_MAP_SECTION = {'Gate_EcruteakCity_Route42_hns': 'MAPSEC_ECRUTEAK_CITY'}

# Behaviors the player can actually stand on or step onto. Door and arrow-warp
# metatiles are not solid in the engine (`TryStartWarpEventScript` fires on
# them the moment the player steps on), so excluding them here makes every
# imported room look unreachable and silently deletes all of its NPCs.
WALKABLE = ('MB_NORMAL', 'MB_WALK_INPLACE_DOWN', 'MB_WALK_INPLACE_UP',
            'MB_WALK_INPLACE_LEFT', 'MB_WALK_INPLACE_RIGHT',
            'MB_ANIMATED_DOOR', 'MB_NON_ANIMATED_DOOR', 'MB_PETALBURG_GYM_DOOR',
            'MB_NORTH_ARROW_WARP', 'MB_SOUTH_ARROW_WARP',
            'MB_EAST_ARROW_WARP', 'MB_WEST_ARROW_WARP')

DIALOGUE = {
    'EcruteakCity_Gym_hns': [
        'GYM LEADER MORTY is away today.\nHis GHOSTs are still roaming.',
        'The shadows here move on their own.\nThat is a GHOST type thing.',
        'The ELITE FOUR train in this gym.\nTheir badges are in the west tower.',
        'This gym is quiet. Even the lights\nare only half lit.',
        'GYM LEADER MORTY watches from\nsomewhere you cannot see.',
    ],
    'EcruteakCity_House1_hns': [
        'The ECRUTEAK SAGE families have\nlived here for generations.',
        'Grandpa still reads the old\nJOHTO almanac every morning.',
    ],
    'EcruteakCity_House2_hns': [
        'You can never find the right book\nwhen you actually want it.',
        'Every book here is about ECRUTEAK\nor the tower that burned down.',
    ],
    'EcruteakCity_Mart_hns': [
        'The shelves are restocked, but the\ndelivery carts are still on ROUTE 37.',
        'ECRUTEAK is where people come to\ntrain GHOST types.',
    ],
    'EcruteakCity_PokemonCenter_hns': [
        'A book about JOHTO genealogy.\nEvery ECRUTEAK name is in it.',
        'These books are mostly about spirits\nand the people who study them.',
        'The bell in the tower rings by itself\nsome nights. Nobody knows why.',
        'People come to ECRUTEAK to talk to\nthe SAGES about their families.',
    ],
    'EcruteakCity_SageOffice1_hns': [
        'The three SAGES share this office.\nThey answer to the tower.',
        'One of the SAGES is away today.\nThe other two are studying.',
    ],
    'EcruteakCity_SageOffice2_hns': [
        'A carved statue of an ancestor.\nThe face has worn smooth.',
        'The SAGES leave offerings here\nevery morning.',
    ],
    'EcruteakCity_Theater_hns': [
        'The KIMONO troupe performs here.\nThe stage is open to anyone.',
        'The band tunes a song that will\nnever be finished.',
        'FANS hold a trance here every\nevening. It is impressive.',
        'The theatre is loud even when\nnobody is playing.',
    ],
    'Gate_EcruteakCity_Route38_hns': [
        'ECRUTEAK CITY lies east.\nROUTE 38 runs west to the farms.',
    ],
    'Gate_EcruteakCity_Route42_hns': [
        'ECRUTEAK CITY lies west.\nThe gate east is closed for now.',
    ],
}

SIGN_TEXT = {
    'EcruteakCity_Gym_hns': 'A stone plaque lists the\\nECRUTEAK GYM LEADERs.',
    'EcruteakCity_House2_hns': 'It is a book about ECRUTEAK\\nhistory, worn soft.',
    'EcruteakCity_SageOffice1_hns': 'ECRUTEAK SAGE OFFICES.\\nPlease keep your voice down.',
    'EcruteakCity_SageOffice2_hns': 'A carved statue of an\\nancestor of the SAGES.',
    'EcruteakCity_Theater_hns': 'ECRUTEAK DANCE THEATER.\\nThe KIMONO troupe performs here.',
}


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n')


def load_behaviors():
    sys.path.insert(0, str(ROOT / 'plastic_ox/agent'))
    from remap_metatile_behaviors import build_mapping
    return build_mapping()[0]


def load_attrs(symbol):
    """Return metatile -> raw metatile attribute word for one tileset."""
    headers = (ROOT / 'src/data/tilesets/headers.h').read_text()
    body = re.search(rf'const struct Tileset {re.escape(symbol)} =\n\{{(.*?)\n\}};',
                     headers, re.S).group(1)
    pointer = re.search(r'metatileAttributes = (\w+)', body).group(1)
    path = re.search(rf'{re.escape(pointer)}\[\] = INCBIN_U16\("([^"]+)"',
                     (ROOT / 'src/data/tilesets/metatiles.h').read_text()).group(1)
    raw = (ROOT / path).read_bytes()
    return struct.unpack('<' + 'H' * (len(raw) // 2), raw)


def read_blocks(layout):
    raw = (ROOT / layout['blockdata_filepath']).read_bytes()
    return struct.unpack('<' + 'H' * (len(raw) // 2), raw)


def walkable_grid(layout, blocks, behaviors, attrs):
    grid = []
    for y in range(layout['height']):
        row = []
        for x in range(layout['width']):
            metatile = blocks[y * layout['width'] + x] & 0x3FF
            row.append(behaviors[attrs(metatile) & 0xFF] in WALKABLE)
        grid.append(row)
    return grid


def convert_warps(name, donor_warps):
    """Convert donor warps, keeping self-referential ids correct after edits."""
    plan = WARP_PLAN.get(name, {})
    dropped = plan.get('drop', set())
    kept, index_of = [], {}
    seen = set()
    for index, warp in enumerate(donor_warps):
        if index in dropped:
            continue
        if (warp['x'], warp['y']) in seen:      # donor duplicates one tile
            continue
        seen.add((warp['x'], warp['y']))
        index_of[index] = len(kept)
        kept.append(dict(warp))
    for warp in kept:
        warp['dest_warp_id'] = str(index_of[int(warp['dest_warp_id'])]) \
            if warp['dest_map'] == name else warp['dest_warp_id']
        warp['elevation'] = 0                    # ELEVATION_TRANSITION: always matches
    for index in plan.get('dynamic', set()):
        target = index_of[index]
        kept[target].update(dest_map='MAP_DYNAMIC', dest_warp_id='WARP_ID_DYNAMIC')
    return kept, {str(k): v for k, v in index_of.items()}


# hns reuses MB_MT_PYRE_HOLE for the ECRUTEAK gym's shadow floor. In this ROM
# that behavior is hijacked by EventScript_FallDownHoleMtPyre, so every step in
# the gym would fire a FALLARBOR story beat instead of the maze warp. The
# donor's own shadow tiles only ever carry a warp event, and MB_NON_ANIMATED_DOOR
# is the engine's plain "step onto me and warp" tile with no door animation and
# no special script, so it reproduces the maze exactly.
GYM_TILESET = 'gTileset_EcruteakCity_Gym_Hns'
BEHAVIOR_PATCH = {GYM_TILESET: {'MB_MT_PYRE_HOLE': 'MB_NON_ANIMATED_DOOR'}}


def metatile_attribute_path(symbol):
    headers = (ROOT / 'src/data/tilesets/headers.h').read_text()
    body = re.search(rf'const struct Tileset {re.escape(symbol)} =\n\{{(.*?)\n\}};', headers, re.S)
    if body is None:
        return None
    pointer = re.search(r'metatileAttributes = (\w+)', body.group(1)).group(1)
    metatiles = (ROOT / 'src/data/tilesets/metatiles.h').read_text()
    match = re.search(rf'{re.escape(pointer)}\[\] = INCBIN_U16\("([^"]+)"', metatiles)
    return ROOT / match.group(1) if match else None


def behavior_names():
    body = (ROOT / 'include/constants/metatile_behaviors.h').read_text()
    return re.findall(r'^\s*(MB_\w+),', body, re.M)


def patch_tileset_behaviors():
    """Rewrite behaviour bytes in the copied *_hns metatile attribute blobs.

    Idempotent: a tileset already patched by an earlier run reports zero source
    entries, which is success as long as the replacements are present.
    """
    names = behavior_names()
    applied = []
    for symbol, changes in BEHAVIOR_PATCH.items():
        path = metatile_attribute_path(symbol)
        if path is None or not path.exists():
            raise SystemExit(f'cannot locate metatile attributes for {symbol}')
        raw = bytearray(path.read_bytes())
        patched = bytearray(raw)
        hits = collections.Counter()
        for i in range(len(raw) // 2):
            word = struct.unpack_from('<H', raw, 2 * i)[0]
            behaviour = names[word & 0xFF]
            if behaviour in changes:
                struct.pack_into('<H', patched, 2 * i,
                                 (word & ~0xFF) | names.index(changes[behaviour]))
                hits[behaviour] += 1
            elif behaviour in changes.values():
                source = next(s for s, t in changes.items() if t == behaviour)
                hits[source] += 1
        missing = [source for source in changes if not hits[source]]
        if missing:
            raise SystemExit(f'{symbol}: no {missing} entries to patch')
        path.write_bytes(bytes(patched))
        applied.append({'tileset': symbol, 'changes': dict(changes),
                        'metatiles': {k: v for k, v in hits.items() if k in changes}})
    return applied


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--donor', type=Path, default=DONOR_DEFAULT)
    args = ap.parse_args()
    donor = args.donor.resolve()

    layouts = json.loads((ROOT / 'data/layouts/layouts.json').read_text())
    source_layouts = {l['id']: l for l in
                      json.loads((donor / 'data/layouts/layouts.json').read_text())['layouts']}
    groups = json.loads((ROOT / 'data/maps/map_groups.json').read_text())
    gfx = (ROOT / 'include/constants/event_objects.h').read_text()
    behaviors = load_behaviors()

    manifest = {
        'donor': str(donor),
        'revision': subprocess.check_output(['git', '-C', str(donor), 'rev-parse', 'HEAD'],
                                            text=True).strip(),
        'group': 'gMapGroup_PlasticOxInteriors',
        'city': CITY,
        'maps': {},
        'assets': [],
        'tilesets': ('All primary/secondary tilesets these rooms use were already registered '
                     'by earlier waves; no new tileset assets were copied. The ECRUTEAK '
                     'gym tileset is the one exception to verbatim behaviour: see '
                     'behavior_patches.'),
        'encounters': ('None. ECRUTEAK keeps its city encounter table; every imported room '
                       'is indoor.'),
        'events': ('Donor story (BILL, the ELITE FOUR challenge, the ROCKET in the theatre) '
                   'is removed. Wardens, sages, clerk and nurse keep local service scripts; '
                   'every other NPC is pinned dialogue.'),
    }

    for name in MAPS:
        path = donor / f'data/maps/{name}/map.json'
        data = json.loads(path.read_text())
        source = copy.deepcopy(data)
        layout = copy.deepcopy(source_layouts[data['layout']])
        layout.pop('game_version', None)
        layout.update(layout_version='hns', include_in_versions=['emerald'])
        for key in ['border_filepath', 'blockdata_filepath']:
            target = ROOT / layout[key]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(donor / layout[key], target)
        if not any(l['id'] == layout['id'] for l in layouts['layouts']):
            layouts['layouts'].append(layout)

        data.pop('game_version', None)
        data.update(region='REGION_HOENN', music=MUSIC[name], connections=[],
                    coord_events=[], allow_running=True)
        data['region_map_section'] = REGION_MAP_SECTION.get(name, data['region_map_section'])

        script = [f'{name}_MapScripts::\n\t.byte 0\n']
        lines = collections.deque(DIALOGUE.get(name, ['ECRUTEAK CITY is full\nof stories.']))
        objects = []
        for obj in data['object_events']:
            g = obj['graphics_id']
            if any(s in g for s in DROP_GFX):
                continue
            if not re.search(r'\b' + re.escape(g) + r'\b', gfx):
                stem = g.removeprefix('OBJ_EVENT_GFX_').removesuffix('_HNS')
                g = 'OBJ_EVENT_GFX_' + GFX_MAP.get(stem, stem)
                if not re.search(r'\b' + re.escape(g) + r'\b', gfx):
                    g = 'OBJ_EVENT_GFX_MAN_1'
            obj.pop('local_id', None)
            obj.update(graphics_id=g, movement_type='MOVEMENT_TYPE_FACE_DOWN',
                       movement_range_x=0, movement_range_y=0,
                       trainer_type='TRAINER_TYPE_NONE',
                       trainer_sight_or_berry_tree_id='0', flag='0')
            # Reuse the shared heal/bookshelf scripts where one already exists.
            reuse = None
            if name == 'EcruteakCity_PokemonCenter_hns' and g == 'OBJ_EVENT_GFX_NURSE_FRLG':
                reuse = 'Pox_Heal'
            if reuse:
                obj['script'] = reuse
            else:
                label = f'PoxEcruteak_{name}_{len(objects)}'
                obj['script'] = label
                lines.rotate(-1)
                text = lines[0]
                script.append(f'{label}::\n\tmsgbox {label}_Text, MSGBOX_NPC\n\tend\n'
                              f'{label}_Text:\n\t.string "{text.replace(chr(10), chr(92) + "n")}$"\n')
            objects.append(obj)
        data['object_events'] = objects

        bg = []
        for index, event in enumerate(data['bg_events']):
            if event['type'] != 'sign':
                continue
            event.pop('label', None)
            event.pop('height', None)
            if (event.get('script') or '') == 'EventScript_BookShelf':
                bg.append(event)      # this ROM already carries the bookshelf script
                continue
            label = f'PoxEcruteak_{name}_Sign{index}'
            event['script'] = label
            script.append(f'{label}::\n\tmsgbox {label}_Text, MSGBOX_SIGN\n\tend\n'
                          f'{label}_Text:\n\t.string "{SIGN_TEXT.get(name, "ECRUTEAK CITY.")}$"\n')
            bg.append(event)
        data['bg_events'] = bg
        data['warp_events'], donor_index = convert_warps(name, source['warp_events'])

        # An NPC must never gate a room (IMPORT_GUIDE.md pitfall 2).
        primary = load_attrs(layout['primary_tileset'])
        secondary = load_attrs(layout['secondary_tileset'])
        attrs = lambda m: primary[m] if m < 640 else secondary[m - 640]  # noqa: E731
        grid = walkable_grid(layout, read_blocks(layout), behaviors, attrs)
        blocked = {(o['x'], o['y']) for o in objects}

        def reachable():
            # Every warp tile must be walkable-to, and every NPC needs at least
            # one standable tile the player can reach to talk to it. The talk
            # tile is any neighbour, not just the one below: a Pokemon Center
            # nurse and the gate officers both stand against a solid counter.
            def inside(tile):
                return 0 <= tile[0] < layout['width'] and 0 <= tile[1] < layout['height']

            warp_goals = {(w['x'], w['y']) for w in data['warp_events']
                          if (w['x'], w['y']) not in blocked}
            npc_options = []
            for ox, oy in blocked:
                options = [(ox + dx, oy + dy) for dx, dy in
                           ((0, -1), (0, 1), (-1, 0), (1, 0))]
                npc_options.append([g for g in options
                                    if inside(g) and g not in blocked and grid[g[1]][g[0]]])
            starts = [(w['x'], w['y']) for w in data['warp_events']
                      if w['dest_map'] != name and (w['x'], w['y']) not in blocked]
            if not starts:
                return True
            seen = set(starts)
            queue = collections.deque(starts)
            while queue:
                x, y = queue.popleft()
                for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < layout['width'] and 0 <= ny < layout['height']
                            and grid[ny][nx] and (nx, ny) not in blocked
                            and (nx, ny) not in seen):
                        seen.add((nx, ny))
                        queue.append((nx, ny))
            if not warp_goals <= seen:
                return False
            return all(options and seen.intersection(options) for options in npc_options)

        removed = []
        for obj in list(objects):
            blocked.add((obj['x'], obj['y']))
            if not reachable():
                blocked.discard((obj['x'], obj['y']))
                objects.remove(obj)
                removed.append(f"{obj['graphics_id']}@{obj['x']},{obj['y']}")
        data['object_events'] = objects

        dump(BASE / f'{name}.json', data)
        (BASE / f'{name}.inc').write_text('\n'.join(script))
        if name not in groups[manifest['group']]:
            groups[manifest['group']].append(name)
        manifest['maps'][name] = {
            'layout': layout,
            'source_warps': source['warp_events'],
            'converted_warps': data['warp_events'],
            # donor warp index -> index in converted_warps, so a *foreign* map
            # that points at a dropped/renumbered donor warp can be retargeted.
            'donor_index_to_converted': donor_index,
            'source_objects': source['object_events'],
            'converted_objects': data['object_events'],
            'dropped_blocking_objects': removed,
            'source_map_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'converted_layout_sha256': {
                key: hashlib.sha256((ROOT / layout[key]).read_bytes()).hexdigest()
                for key in ['border_filepath', 'blockdata_filepath']},
            'source_layout_sha256': {
                key: hashlib.sha256((donor / layout[key]).read_bytes()).hexdigest()
                for key in ['border_filepath', 'blockdata_filepath']},
        }

    # The donor city keeps its own warp ordering; ecruteak.install rewrites the
    # city door list, so record the donor geometry for cross-map retargeting.
    manifest['donor_city_warps'] = json.loads(
        (donor / f'data/maps/{CITY}/map.json').read_text())['warp_events']
    manifest['behavior_patches'] = patch_tileset_behaviors()

    dump(ROOT / 'data/maps/map_groups.json', groups)
    dump(ROOT / 'data/layouts/layouts.json', layouts)
    dump(BASE / 'source_manifest.json', manifest)
    from ecruteak import install
    install(lambda p: (ROOT / p).read_text(),
            lambda p, s: ((ROOT / p).parent.mkdir(parents=True, exist_ok=True),
                          (ROOT / p).write_text(s)))
    print(f'Imported {len(MAPS)} Ecruteak interiors and gatehouses into '
          f'{manifest["group"]}.')


if __name__ == '__main__':
    main()