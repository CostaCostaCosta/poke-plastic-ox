"""Install Jirachi and its sage in the Meteor Falls Bagon chamber.

Owns, on top of the vanilla MeteorFalls_B1F_2R map:

* JIRACHI asleep on the chamber's north shelf with its sage one step in front,
  via the shared pox_legendary_sage macro (beat the sage, any ball catches);
* TRAINER_PLASTIC_OX_JIRACHI_SAGE (ID 962, Sage trainer-flag range).

The Bagon wild table and the Dragon Claw item ball are left alone.
Runs after tin_tower.install, which counts this sage among those home.
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).with_suffix('')
CHAMBER = 'MeteorFalls_B1F_2R'
TRAINER_ID = 962


def npc(local_id, gfx, x, y, script, flag):
    return dict(local_id=local_id, graphics_id=gfx, x=x, y=y, elevation=3,
                movement_type='MOVEMENT_TYPE_FACE_DOWN', movement_range_x=0, movement_range_y=0,
                trainer_type='TRAINER_TYPE_NONE', trainer_sight_or_berry_tree_id='0',
                script=script, flag=flag)


def install(read, put):
    path = f'data/maps/{CHAMBER}/map.json'
    data = json.loads(read(path))
    ours = {'LOCALID_POX_JIRACHI', 'LOCALID_POX_JIRACHI_SAGE'}
    data['object_events'] = [o for o in data['object_events'] if o.get('local_id') not in ours] + [
        npc('LOCALID_POX_JIRACHI', 'OBJ_EVENT_GFX_SPECIES(JIRACHI)', 6, 3,
            'PoxMeteorFalls_JirachiSage', 'FLAG_POX_CAUGHT_JIRACHI'),
        npc('LOCALID_POX_JIRACHI_SAGE', 'OBJ_EVENT_GFX_SAGE_HNS', 6, 4,
            'PoxMeteorFalls_JirachiSage', 'FLAG_POX_CAUGHT_JIRACHI'),
    ]
    put(path, json.dumps(data, indent=2) + '\n')

    put('data/scripts/plastic_ox_meteor_falls.inc', (BASE / 'events.inc').read_text())
    text = read('data/event_scripts.s')
    line = '\t.include "data/scripts/plastic_ox_meteor_falls.inc"\n'
    if line not in text:
        text += '\n' + line
    put('data/event_scripts.s', text)

    path = 'include/constants/opponents.h'
    text = read(path)
    define = f'#define TRAINER_PLASTIC_OX_JIRACHI_SAGE {TRAINER_ID}\n'
    if define not in text:
        text = text.replace('// End Plastic Ox story trainers.', define + '// End Plastic Ox story trainers.')
    for constant in ['TRAINERS_COUNT_EMERALD', 'MAX_TRAINERS_COUNT_EMERALD']:
        text = re.sub(r'(#define ' + constant + r'\s+)(\d+)',
                      lambda m: m[1] + str(max(TRAINER_ID + 1, int(m[2]))), text)
    put(path, text)

    path = 'src/data/trainers.party'
    text = re.sub(r'=== TRAINER_PLASTIC_OX_JIRACHI_SAGE ===\n.*?(?=\n=== |\Z)', '', read(path), flags=re.S)
    put(path, text.rstrip() + '\n\n' + (BASE / 'trainers.party').read_text())


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    install(lambda p: (root / p).read_text(), lambda p, s: (root / p).write_text(s))
