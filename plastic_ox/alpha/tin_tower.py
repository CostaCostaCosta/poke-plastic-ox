"""Install the Tin Tower climb after region generation.

The converted tower maps live in tin_tower/ (written once by import_tin_tower.py).
This module owns three things on top of them:

* the Ecruteak sage office's north door (warp 1 of EcruteakCity_SageOffice2_hns)
  onto Bellchime Trail, held by a door keeper until five sages are home;
* one sage per caught legendary standing in that office (Entei, Articuno,
  Raikou, Regirock, Regice, Registeel);
* the Moltres sage and Moltres on the roof, via the shared pox_legendary_sage.

Runs after ecruteak.install, which copies the office's base map verbatim.
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).with_suffix('')
OFFICE = 'EcruteakCity_SageOffice2_hns'
ROOF = 'TinTower_RoofDay_hns'
TRAINER_ID = 959
TOWER_DOOR = dict(x=8, y=5, elevation=0, dest_map='MAP_BELLCHIME_TRAIL_HNS', dest_warp_id='1')

# (local id suffix, x, y, temp flag that hides them while away, script)
HOME_SAGES = [
    ('ENTEI', 2, 3, 'FLAG_TEMP_1'),
    ('ARTICUNO', 4, 3, 'FLAG_TEMP_2'),
    ('RAIKOU', 6, 3, 'FLAG_TEMP_3'),
    ('REGIROCK', 2, 12, 'FLAG_TEMP_4'),
    ('REGICE', 4, 12, 'FLAG_TEMP_5'),
    ('REGISTEEL', 6, 12, 'FLAG_TEMP_6'),
]


def npc(local_id, gfx, x, y, script, flag='0', movement='MOVEMENT_TYPE_FACE_DOWN', elevation=0):
    return dict(local_id=local_id, graphics_id=gfx, x=x, y=y, elevation=elevation,
                movement_type=movement, movement_range_x=0, movement_range_y=0,
                trainer_type='TRAINER_TYPE_NONE', trainer_sight_or_berry_tree_id='0',
                script=script, flag=flag)


def install(read, put):
    manifest = json.loads((BASE / 'source_manifest.json').read_text())
    for name in manifest['maps']:
        put(f'data/maps/{name}/map.json', (BASE / f'{name}.json').read_text())
        put(f'data/maps/{name}/scripts.inc', (BASE / f'{name}.inc').read_text())

    # Roof: Moltres with its sage one step in front of it.
    path = f'data/maps/{ROOF}/map.json'
    roof = json.loads(read(path))
    roof['object_events'] = [
        npc('LOCALID_POX_MOLTRES', 'OBJ_EVENT_GFX_MOLTRES', 10, 8, 'PoxTinTower_MoltresSage',
            'FLAG_POX_CAUGHT_MOLTRES', elevation=3),
        npc('LOCALID_POX_MOLTRES_SAGE', 'OBJ_EVENT_GFX_SAGE_HNS', 10, 10, 'PoxTinTower_MoltresSage',
            'FLAG_POX_CAUGHT_MOLTRES', elevation=3),
    ]
    put(path, json.dumps(roof, indent=2) + '\n')

    # Sage office: north door, door keeper, the sages who came home.
    path = f'data/maps/{OFFICE}/map.json'
    office = json.loads(read(path))
    warps = [w for w in office['warp_events'] if (w['x'], w['y']) != (TOWER_DOOR['x'], TOWER_DOOR['y'])]
    if len(warps) != 1:
        raise SystemExit(f'{OFFICE}: expected only the Office 1 stair before the tower door')
    office['warp_events'] = warps + [dict(TOWER_DOOR)]   # becomes warp 1 (the trail returns here)
    ours = {'LOCALID_POX_TIN_TOWER_KEEPER'} | {f'LOCALID_POX_HOME_{s[0]}_SAGE' for s in HOME_SAGES}
    office['object_events'] = [o for o in office['object_events'] if o.get('local_id') not in ours] + [
        npc('LOCALID_POX_TIN_TOWER_KEEPER', 'OBJ_EVENT_GFX_SAGE_HNS', 8, 5, 'PoxTinTower_Keeper',
            movement='MOVEMENT_TYPE_FACE_LEFT'),
    ] + [npc(f'LOCALID_POX_HOME_{who}_SAGE', 'OBJ_EVENT_GFX_SAGE_HNS', x, y,
             f'PoxTinTower_Sage{who.capitalize()}', flag) for who, x, y, flag in HOME_SAGES]
    put(path, json.dumps(office, indent=2) + '\n')

    path = f'data/maps/{OFFICE}/scripts.inc'
    header = f'{OFFICE}_MapScripts::\n\t.byte 0\n'
    text = read(path)
    if header in text:
        text = text.replace(header, f'{OFFICE}_MapScripts::\n'
                            '\tmap_script MAP_SCRIPT_ON_TRANSITION, PoxTinTower_Office_OnTransition\n'
                            '\t.byte 0\n')
    elif 'PoxTinTower_Office_OnTransition' not in text:
        raise SystemExit(f'{OFFICE}: unexpected map script header')
    put(path, text)

    put('data/scripts/plastic_ox_tin_tower.inc', (BASE / 'events.inc').read_text())
    text = read('data/event_scripts.s')
    for name in manifest['maps']:
        line = f'\t.include "data/maps/{name}/scripts.inc"\n'
        if line not in text:
            text += '\n' + line
    line = '\t.include "data/scripts/plastic_ox_tin_tower.inc"\n'
    if line not in text:
        text += '\n' + line
    put('data/event_scripts.s', text)

    path = 'include/constants/opponents.h'
    text = read(path)
    define = f'#define TRAINER_PLASTIC_OX_MOLTRES_SAGE {TRAINER_ID}\n'
    if define not in text:
        text = text.replace('// End Plastic Ox story trainers.', define + '// End Plastic Ox story trainers.')
    for constant in ['TRAINERS_COUNT_EMERALD', 'MAX_TRAINERS_COUNT_EMERALD']:
        text = re.sub(r'(#define ' + constant + r'\s+)(\d+)',
                      lambda m: m[1] + str(max(TRAINER_ID + 1, int(m[2]))), text)
    put(path, text)

    path = 'src/data/trainers.party'
    text = re.sub(r'=== TRAINER_PLASTIC_OX_MOLTRES_SAGE ===\n.*?(?=\n=== |\Z)', '', read(path), flags=re.S)
    put(path, text.rstrip() + '\n\n' + (BASE / 'trainers.party').read_text())


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    install(lambda p: (root / p).read_text(),
            lambda p, s: ((root / p).parent.mkdir(parents=True, exist_ok=True),
                          (root / p).write_text(s)))
