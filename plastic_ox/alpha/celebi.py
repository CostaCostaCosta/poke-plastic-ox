"""Install Celebi at the Ilex Forest shrine (bible: Celebi — Ilex Forest).

* a sage and Celebi beside the shrine sign, shown only after the Burned Tower
  and until Celebi is caught (temp flag set by the Ilex arrival script);
* the sage battles only when the player holds ITEM_GS_BALL, the Trick House
  puzzle 5 prize; then the shared pox_legendary_sage reward runs;
* TRAINER_PLASTIC_OX_CELEBI_SAGE and its authored party.

The sage's homecoming in the Ecruteak sage office belongs to tin_tower.py.
Runs after region generation (it patches the Ilex arrival callback).
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).with_suffix('')
MAP = 'IlexForest_hns'
TRAINER_ID = 963
OURS = {'LOCALID_POX_CELEBI', 'LOCALID_POX_CELEBI_SAGE'}


def npc(local_id, gfx, x, y, movement):
    return dict(local_id=local_id, graphics_id=gfx, x=x, y=y, elevation=3,
                movement_type=movement, movement_range_x=0, movement_range_y=0,
                trainer_type='TRAINER_TYPE_NONE', trainer_sight_or_berry_tree_id='0',
                script='PoxCelebi_Sage', flag='FLAG_TEMP_1')


def install(read, put):
    path = f'data/maps/{MAP}/map.json'
    forest = json.loads(read(path))
    forest['object_events'] = [o for o in forest['object_events'] if o.get('local_id') not in OURS] + [
        npc('LOCALID_POX_CELEBI', 'OBJ_EVENT_GFX_CELEBI', 24, 26, 'MOVEMENT_TYPE_FACE_DOWN'),
        npc('LOCALID_POX_CELEBI_SAGE', 'OBJ_EVENT_GFX_SAGE_HNS', 24, 28, 'MOVEMENT_TYPE_FACE_DOWN'),
    ]
    put(path, json.dumps(forest, indent=2) + '\n')

    path = 'data/scripts/plastic_ox_region.inc'
    text = read(path)
    label = f'PoxRegion_Arrival_{MAP}::\n'
    if label not in text:
        raise SystemExit(f'{path}: no {label.strip()}')
    call = '\tcall PoxCelebi_IlexArrival\n'
    if label + call not in text:
        text = text.replace(label, label + call)
    put(path, text)

    put('data/scripts/plastic_ox_celebi.inc', (BASE / 'events.inc').read_text())
    text = read('data/event_scripts.s')
    line = '\t.include "data/scripts/plastic_ox_celebi.inc"\n'
    if line not in text:
        text += '\n' + line
    put('data/event_scripts.s', text)

    path = 'include/constants/opponents.h'
    text = read(path)
    define = f'#define TRAINER_PLASTIC_OX_CELEBI_SAGE {TRAINER_ID}\n'
    if define not in text:
        text = text.replace('// End Plastic Ox story trainers.', define + '// End Plastic Ox story trainers.')
    for constant in ['TRAINERS_COUNT_EMERALD', 'MAX_TRAINERS_COUNT_EMERALD']:
        text = re.sub(r'(#define ' + constant + r'\s+)(\d+)',
                      lambda m: m[1] + str(max(TRAINER_ID + 1, int(m[2]))), text)
    put(path, text)

    path = 'src/data/trainers.party'
    text = re.sub(r'=== TRAINER_PLASTIC_OX_CELEBI_SAGE ===\n.*?(?=\n=== |\Z)', '', read(path), flags=re.S)
    put(path, text.rstrip() + '\n\n' + (BASE / 'trainers.party').read_text())


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    install(lambda p: (root / p).read_text(),
            lambda p, s: ((root / p).parent.mkdir(parents=True, exist_ok=True),
                          (root / p).write_text(s)))
