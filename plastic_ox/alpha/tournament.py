"""Install the Underground tournament and reward hooks after region regeneration.

Authored scripts/parties live alongside this module. Existing routes, puzzles,
field requirements and normal encounter tables remain owned by their modules.
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).with_suffix('')
TRAINERS = ['TOURNAMENT_1', 'TOURNAMENT_2', 'TOURNAMENT_3', 'TOURNAMENT_4',
            'RAIKOU_SAGE', 'REGIROCK_SAGE', 'REGICE_SAGE', 'REGISTEEL_SAGE']


def install(read, put):
    def edit(path, fn):
        put(path, fn(read(path)))

    def actors(name, objects):
        path = f'data/maps/{name}/map.json'
        data = json.loads(read(path))
        ids = {o['local_id'] for o in objects}
        data['object_events'] = [o for o in data['object_events'] if o.get('local_id') not in ids] + objects
        put(path, json.dumps(data, indent=2) + '\n')

    def npc(id, gfx, x, y, script, flag='0', elevation=3):
        return dict(local_id='LOCALID_POX_' + id, graphics_id='OBJ_EVENT_GFX_' + gfx,
                    x=x, y=y, elevation=elevation, movement_type='MOVEMENT_TYPE_FACE_DOWN',
                    movement_range_x=0, movement_range_y=0, trainer_type='TRAINER_TYPE_NONE',
                    trainer_sight_or_berry_tree_id='0', script=script, flag=flag)

    actors('UndergroundPath_EastWestTunnel_Frlg', [
        npc('TOURNAMENT_HOST', 'OLD_MAN', 33, 2, 'PoxTournament_Host'),
        npc('TOURNAMENT_1', 'COOLTRAINER_F', 36, 2, 'PoxTournament_Round1'),
        npc('TOURNAMENT_2', 'GENTLEMAN', 39, 2, 'PoxTournament_Round2'),
        npc('TOURNAMENT_3', 'COOLTRAINER_M', 42, 2, 'PoxTournament_Round3')])
    actors('NewMauville_Inside', [
        npc('RAIKOU_SAGE', 'SAGE_HNS', 31, 6, 'PoxTournament_Raikou', 'FLAG_POX_CAUGHT_RAIKOU'),
        npc('RAIKOU', 'RAIKOU', 31, 7, 'PoxTournament_Raikou', 'FLAG_POX_CAUGHT_RAIKOU')])
    actors('RustboroCity_DevonCorp_3F', [
        npc('STONE', 'OLD_MAN', 8, 3, 'PoxTournament_Stone')])

    # Old saves with an open vanilla door must still own the tournament key.
    path = 'data/maps/NewMauville_Entrance/scripts.inc'
    s = read(path).replace('ITEM_BASEMENT_KEY', 'ITEM_NEW_MAUVILLE_KEY').replace('BASEMENT KEY', 'NEW MAUVILLE KEY')
    start = 'NewMauville_Entrance_OnLoad:\n'
    if 'PoxTournament_ResetMauvilleDoor' not in s:
        s = s.replace(start, start + '\tcheckitem ITEM_NEW_MAUVILLE_KEY\n\tgoto_if_eq VAR_RESULT, FALSE, PoxTournament_ResetMauvilleDoor\n\tgoto_if_unset FLAG_BADGE06_GET, PoxTournament_ResetMauvilleDoor\n')
        s += '\nPoxTournament_ResetMauvilleDoor::\n\tsetvar VAR_NEW_MAUVILLE_STATE, 0\n\tcall NewMauville_Entrance_EventScript_CloseDoor\n\tend\n'
        s = s.replace('\tcheckitem ITEM_NEW_MAUVILLE_KEY\n\tgoto_if_eq VAR_RESULT, FALSE, NewMauville_Entrance_EventScript_DontOpenDoor', '\tgoto_if_unset FLAG_BADGE06_GET, NewMauville_Entrance_EventScript_DontOpenDoor\n\tcheckitem ITEM_NEW_MAUVILLE_KEY\n\tgoto_if_eq VAR_RESULT, FALSE, NewMauville_Entrance_EventScript_DontOpenDoor')
    put(path, s)

    # The original Wailord/Relicanth ordering and all three local puzzles remain.
    path = 'data/maps/SealedChamber_InnerRoom/scripts.inc'
    s = read(path)
    if 'ITEM_ANCIENT_BRAILLE_TABLET' not in s:
        s = s.replace('SealedChamber_InnerRoom_EventScript_BrailleBackWall::\n\tlockall',
                      'SealedChamber_InnerRoom_EventScript_BrailleBackWall::\n\tlockall\n\tcheckitem ITEM_ANCIENT_BRAILLE_TABLET\n\tgoto_if_eq VAR_RESULT, FALSE, PoxTournament_LegendLocked\n\tgoto_if_unset FLAG_BADGE05_GET, PoxTournament_LegendLocked')
    put(path, s)
    for species, name in [('Regirock', 'DesertRuins'), ('Regice', 'IslandCave'), ('Registeel', 'AncientTomb')]:
        upper = species.upper()
        path = f'data/maps/{name}/map.json'
        d = json.loads(read(path))
        d['object_events'] = [o for o in d['object_events'] if o['graphics_id'] != 'OBJ_EVENT_GFX_' + upper]
        put(path, json.dumps(d, indent=2) + '\n')
        actors(name, [npc(upper, upper, 8, 7, 'PoxTournament_' + species, 'FLAG_POX_CAUGHT_' + upper),
                      npc(upper + '_SAGE', 'SAGE_HNS', 7, 7, 'PoxTournament_' + species, 'FLAG_POX_CAUGHT_' + upper)])
        path = f'data/maps/{name}/scripts.inc'
        s = read(path)
        # Replace the legacy direct-capture entry, including coordinate callers.
        s = re.sub(name + '_EventScript_' + species + r'::.*?(?=\n\w+::|\Z)',
                   name + '_EventScript_' + species + '::\n\tgoto PoxTournament_' + species + '\n', s, count=1, flags=re.S)
        put(path, s)

    put('data/scripts/plastic_ox_tournament.inc', (BASE / 'events.inc').read_text())
    line = '\t.include "data/scripts/plastic_ox_tournament.inc"\n'
    edit('data/event_scripts.s', lambda s: s if line in s else s + '\n' + line)
    path = 'include/constants/opponents.h'
    s = read(path)
    for i, trainer in enumerate(TRAINERS, 945):
        define = f'#define TRAINER_PLASTIC_OX_{trainer} {i}\n'
        if define not in s:
            s = s.replace('// End Plastic Ox story trainers.', define + '// End Plastic Ox story trainers.')
    for c in ['TRAINERS_COUNT_EMERALD', 'MAX_TRAINERS_COUNT_EMERALD']:
        s = re.sub(r'(#define ' + c + r'\s+)(\d+)', lambda m: m[1] + str(max(953, int(m[2]))), s)
    put(path, s)
    s = read('src/data/trainers.party')
    for trainer in TRAINERS:
        s = re.sub(r'=== TRAINER_PLASTIC_OX_' + trainer + r' ===\n.*?(?=\n=== |\Z)', '', s, flags=re.S)
    put('src/data/trainers.party', s.rstrip() + '\n\n' + (BASE / 'trainers.party').read_text())


if __name__ == '__main__':
    install(lambda p: Path(p).read_text(), lambda p, s: Path(p).write_text(s))
