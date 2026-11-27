"""Install the Clear Bell chain: ZAPDOS at the Radio Tower, MORTY and SUICUNE
under the Burned Tower.

Owns, on top of the maps other modules generate:

* GoldenrodCity_RadioTower_5F_hns: ZAPDOS and its sage in the east studio,
  shown once the New Mauville generator is off (VAR_NEW_MAUVILLE_STATE == 2)
  and the OU region is open (FLAG_POX_STORY_SPACE_CENTER); a tower engineer
  who hands over the CLEAR BELL once ZAPDOS is caught;
* PlasticOx_BurnedTowerB1F: MORTY waiting where SUICUNE looked back (after
  badge 3) and SUICUNE, who answers the bell; MORTY is SUICUNE's sage;
* PlasticOx_MortyGym: the gym MORTY is away while he waits in the tower;
* TRAINER_PLASTIC_OX_ZAPDOS_SAGE (964) and TRAINER_PLASTIC_OX_SUICUNE_SAGE
  (965, MORTY's own team), both in the Sage trainer-flag range.

Both encounters use the shared pox_legendary_sage macro. The ZAPDOS sage goes
home to the Ecruteak sage office (tin_tower.py); MORTY goes back to his gym.
Runs after build_story's tower and gym rooms and after tin_tower.install.
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).with_suffix('')
RADIO = 'GoldenrodCity_RadioTower_5F_hns'
TOWER = 'PlasticOx_BurnedTowerB1F'
GYM = 'PlasticOx_MortyGym'
TRAINERS = {'ZAPDOS_SAGE': 964, 'SUICUNE_SAGE': 965}


def npc(local_id, gfx, x, y, script, flag, movement='MOVEMENT_TYPE_FACE_DOWN'):
    return dict(local_id=local_id, graphics_id=gfx, x=x, y=y, elevation=0,
                movement_type=movement, movement_range_x=0, movement_range_y=0,
                trainer_type='TRAINER_TYPE_NONE', trainer_sight_or_berry_tree_id='0',
                script=script, flag=flag)


def install(read, put):
    def actors(name, objects):
        path = f'data/maps/{name}/map.json'
        data = json.loads(read(path))
        ids = {o['local_id'] for o in objects}
        data['object_events'] = [o for o in data['object_events'] if o.get('local_id') not in ids] + objects
        put(path, json.dumps(data, indent=2) + '\n')

    def header(name, old, new):
        path = f'data/maps/{name}/scripts.inc'
        text = read(path)
        if new in text:
            return
        if old not in text:
            raise SystemExit(f'{name}: unexpected map script header')
        put(path, text.replace(old, new, 1))

    actors(RADIO, [
        npc('LOCALID_POX_ZAPDOS', 'OBJ_EVENT_GFX_ZAPDOS', 27, 7, 'PoxRadioTower_ZapdosSage', 'FLAG_TEMP_1'),
        npc('LOCALID_POX_ZAPDOS_SAGE', 'OBJ_EVENT_GFX_SAGE_HNS', 27, 8, 'PoxRadioTower_ZapdosSage', 'FLAG_TEMP_1'),
        npc('LOCALID_POX_RADIO_ENGINEER', 'OBJ_EVENT_GFX_MAN_5', 30, 13, 'PoxRadioTower_Engineer', '0',
            movement='MOVEMENT_TYPE_FACE_LEFT'),
    ])
    header(RADIO, f'{RADIO}_MapScripts::\n\t.byte 0\n',
           f'{RADIO}_MapScripts::\n\tmap_script MAP_SCRIPT_ON_TRANSITION, PoxRadioTower_OnTransition\n\t.byte 0\n')

    actors(TOWER, [
        npc('LOCALID_POX_SUICUNE_MORTY', 'OBJ_EVENT_GFX_MAN_3', 16, 12, 'PoxClearBell_Morty', 'FLAG_TEMP_1'),
        npc('LOCALID_POX_SUICUNE', 'OBJ_EVENT_GFX_SUICUNE', 16, 11, 'PoxClearBell_SuicuneSage', 'FLAG_TEMP_2'),
    ])
    header(TOWER, 'map_script MAP_SCRIPT_ON_TRANSITION, PoxTower_InitGraphics\n',
           'map_script MAP_SCRIPT_ON_TRANSITION, PoxClearBell_TowerOnTransition\n')

    # The gym MORTY keeps the story-NPC hide flag, re-applied on transition,
    # and is away while he waits in the tower.
    path = f'data/maps/{GYM}/map.json'
    gym = json.loads(read(path))
    morty = [o for o in gym['object_events'] if o['script'] == 'Pox_Morty']
    if len(morty) != 1:
        raise SystemExit(f'{GYM}: expected one Pox_Morty object')
    morty[0]['flag'] = 'FLAG_TEMP_1'
    put(path, json.dumps(gym, indent=2) + '\n')
    header(GYM, f'{GYM}_MapScripts::\n\t.byte 0\n',
           f'{GYM}_MapScripts::\n\tmap_script MAP_SCRIPT_ON_TRANSITION, PoxClearBell_GymOnTransition\n\t.byte 0\n')

    put('data/scripts/plastic_ox_clear_bell.inc', (BASE / 'events.inc').read_text())
    text = read('data/event_scripts.s')
    line = '\t.include "data/scripts/plastic_ox_clear_bell.inc"\n'
    if line not in text:
        text += '\n' + line
    put('data/event_scripts.s', text)

    path = 'include/constants/opponents.h'
    text = read(path)
    for name, tid in TRAINERS.items():
        define = f'#define TRAINER_PLASTIC_OX_{name} {tid}\n'
        if define not in text:
            text = text.replace('// End Plastic Ox story trainers.', define + '// End Plastic Ox story trainers.')
    top = max(TRAINERS.values()) + 1
    for constant in ['TRAINERS_COUNT_EMERALD', 'MAX_TRAINERS_COUNT_EMERALD']:
        text = re.sub(r'(#define ' + constant + r'\s+)(\d+)', lambda m: m[1] + str(max(top, int(m[2]))), text)
    put(path, text)

    path = 'src/data/trainers.party'
    text = read(path)
    for name in TRAINERS:
        text = re.sub(rf'=== TRAINER_PLASTIC_OX_{name} ===\n.*?(?=\n=== |\Z)', '', text, flags=re.S)
    put(path, text.rstrip() + '\n\n' + (BASE / 'trainers.party').read_text())


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    install(lambda p: (root / p).read_text(), lambda p, s: (root / p).write_text(s))
