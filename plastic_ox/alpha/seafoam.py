"""Reapply the Seafoam Articuno Sage encounter after region generation."""
import json
import re
from pathlib import Path

BASE = Path(__file__).with_suffix('')


def install(read, put):
    path = 'data/maps/SeafoamIslands_B4F_Frlg/map.json'
    data = json.loads(read(path))
    bird = next(o for o in data['object_events'] if o['graphics_id'] == 'OBJ_EVENT_GFX_ARTICUNO')
    bird.update(local_id='LOCALID_POX_ARTICUNO', script='PoxSeafoam_ArticunoSage',
                movement_range_x=0, movement_range_y=0)
    sage = dict(bird, local_id='LOCALID_POX_ARTICUNO_SAGE',
                graphics_id='OBJ_EVENT_GFX_SAGE_HNS', x=10, y=2)
    data['object_events'] = [o for o in data['object_events']
                             if o.get('local_id') != 'LOCALID_POX_ARTICUNO_SAGE'] + [sage]
    put(path, json.dumps(data, indent=2) + '\n')

    # The shared reward script owns visibility and battle outcomes. Preserve
    # the original current/boulder puzzle, but never respawn a caught bird.
    path = 'data/maps/SeafoamIslands_B4F_Frlg/scripts.inc'
    text = read(path).replace('\tmap_script MAP_SCRIPT_ON_RESUME, SeafoamIslands_B4F_OnResume\n', '')
    text = re.sub(r'SeafoamIslands_B4F_OnResume::.*?(?=SeafoamIslands_B4F_OnTransition::)', '', text, flags=re.S)
    text = text.replace('\tcall_if_unset FLAG_POX_FOUGHT_ARTICUNO, SeafoamIslands_B4F_EventScript_ShowArticuno\n', '')
    text = re.sub(r'SeafoamIslands_B4F_EventScript_ShowArticuno::.*?(?=SeafoamIslands_B4F_OnLoad::)', '', text, flags=re.S)
    text = re.sub(r'SeafoamIslands_B4F_EventScript_Articuno::.*?(?=SeafoamIslands_B4F_EventScript_BoulderHintSign::)',
                  'SeafoamIslands_B4F_EventScript_Articuno::\n\tgoto PoxSeafoam_ArticunoSage\n\n', text, flags=re.S)
    put(path, text)

    put('data/scripts/plastic_ox_seafoam.inc', (BASE / 'events.inc').read_text())
    path = 'data/event_scripts.s'
    text = read(path)
    line = '\t.include "data/scripts/plastic_ox_seafoam.inc"\n'
    if line not in text:
        text += '\n' + line
    put(path, text)

    path = 'include/constants/opponents.h'
    text = read(path)
    if '#define TRAINER_PLASTIC_OX_ARTICUNO_SAGE ' not in text:
        text = text.replace('// End Plastic Ox story trainers.',
                            '#define TRAINER_PLASTIC_OX_ARTICUNO_SAGE 939\n// End Plastic Ox story trainers.')
    for constant in ['TRAINERS_COUNT_EMERALD', 'MAX_TRAINERS_COUNT_EMERALD']:
        text = re.sub(r'(#define ' + constant + r'\s+)(\d+)',
                      lambda m: m[1] + str(max(940, int(m[2]))), text)
    put(path, text)
    path = 'src/data/trainers.party'
    text = re.sub(r'=== TRAINER_PLASTIC_OX_ARTICUNO_SAGE ===\n.*?(?=\n=== |\Z)', '', read(path), flags=re.S)
    put(path, text.rstrip() + '\n\n' + (BASE / 'trainers.party').read_text())


if __name__ == '__main__':
    install(lambda p: Path(p).read_text(), lambda p, s: Path(p).write_text(s))
