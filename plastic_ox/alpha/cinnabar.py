"""Reapply Cinnabar progression and the reusable Entei Sage after generation."""
import json
import re
from pathlib import Path

BASE = Path(__file__).with_suffix('')


def install(read, put):
    def load(name):
        return json.loads(read(f'data/maps/{name}/map.json'))

    def save(name, data):
        put(f'data/maps/{name}/map.json', json.dumps(data, indent=2) + '\n')

    city = load('CinnabarIsland_Frlg')
    for obj in city['object_events']:
        obj['script'] = {'Pox_MansionGuide': 'PoxCinnabar_MansionGuide',
                         'Pox_BlaineGuide': 'PoxCinnabar_GymGuide'}.get(obj['script'], obj['script'])
    save('CinnabarIsland_Frlg', city)
    gym = load('CinnabarIsland_Gym_Frlg')
    for obj in gym['object_events']:
        if obj['script'] == 'CinnabarIsland_Gym_EventScript_Blaine':
            obj['script'] = 'Pox_Blaine'
            obj['trainer_type'] = 'TRAINER_TYPE_NONE'
            obj['trainer_sight_or_berry_tree_id'] = '0'
    save('CinnabarIsland_Gym_Frlg', gym)

    basement = load('PokemonMansion_B1F_Frlg')
    sage = basement['object_events'][5]
    sage.update(local_id='LOCALID_POX_ENTEI_SAGE', graphics_id='OBJ_EVENT_GFX_SAGE_HNS', x=5, y=7,
                movement_type='MOVEMENT_TYPE_FACE_DOWN', movement_range_x=0,
                movement_range_y=0, script='PoxCinnabar_EnteiSage', flag='FLAG_POX_ENTEI')
    entei = dict(sage, local_id='LOCALID_POX_ENTEI', graphics_id='OBJ_EVENT_GFX_ENTEI', x=6, y=7)
    if len(basement['object_events']) == 6:
        basement['object_events'].append(entei)
    else:
        basement['object_events'][6] = entei
    save('PokemonMansion_B1F_Frlg', basement)

    # The old placeholder cannot offer a second Entei or bypass the puzzle.
    legacy = load('PlasticOx_Mansion')
    legacy['object_events'] = [o for o in legacy['object_events'] if o['script'] != 'Pox_Entei']
    save('PlasticOx_Mansion', legacy)

    # Put the existing story archive sequence on the real Mansion's books.
    for name, old, new in [
        ('PokemonMansion_2F_Frlg', 'PokemonMansion_2F_EventScript_DiaryJuly5th', 'Pox_Archive1'),
        ('PokemonMansion_3F_Frlg', 'PokemonMansion_3F_EventScript_DiaryFeb6th', 'Pox_Archive2'),
        ('PokemonMansion_B1F_Frlg', 'PokemonMansion_B1F_EventScript_DiarySep1st', 'Pox_Archive3'),
    ]:
        data = load(name)
        for event in data['bg_events']:
            if event.get('script') == old:
                event['script'] = new
        save(name, data)

    path = 'data/scripts/plastic_ox_story.inc'
    text = read(path)
    text = re.sub(r'Pox_Entei::.*?(?=Pox_MansionExit::)',
                  'Pox_Entei::\n\tgoto PoxCinnabar_MansionGuide\n\n', text, flags=re.S)
    for old, new in [('Pox_MansionGuide', 'PoxCinnabar_MansionGuide'), ('Pox_BlaineGuide', 'PoxCinnabar_GymGuide')]:
        text = re.sub(old + r'::.*?(?=Pox_Text_' + old[4:] + r'::)',
                      old + '::\n\tgoto ' + new + '\n\n', text, flags=re.S)
    # Old saves can collect the key again if the original key flag was set but
    # the item is absent. The key flag follows the successful bag operation.
    text = text.replace('goto_if_set FLAG_POX_MANSION_KEY, Pox_Done\n\tgiveitem ITEM_SECRET_KEY',
                        'checkitem ITEM_SECRET_KEY\n\tgoto_if_eq VAR_RESULT, TRUE, Pox_Done\n\tgiveitem ITEM_SECRET_KEY')
    text = text.replace('checkitem ITEM_SECRET_KEY\n\tgoto_if_eq VAR_RESULT, TRUE, Pox_Done',
                        'checkitem ITEM_SECRET_KEY\n\tgoto_if_eq VAR_RESULT, TRUE, Pox_MansionKey_Owned')
    if 'Pox_MansionKey_Owned::' not in text:
        text = text.replace('\tsetflag FLAG_POX_MANSION_KEY',
                            'Pox_MansionKey_Owned::\n\tsetflag FLAG_POX_MANSION_KEY', 1)
    put(path, text)
    path = 'data/event_scripts.s'
    text = read(path)
    for source in ['data/scripts/plastic_ox_legendary_sages.inc', 'data/scripts/plastic_ox_cinnabar.inc']:
        line = f'\t.include "{source}"\n'
        if line not in text:
            text += '\n' + line
    put(path, text)
    put('data/scripts/plastic_ox_cinnabar.inc', (BASE / 'events.inc').read_text())

    path = 'include/constants/opponents.h'
    text = read(path)
    if '#define TRAINER_PLASTIC_OX_ENTEI_SAGE ' not in text:
        text = text.replace('// End Plastic Ox story trainers.',
                            '#define TRAINER_PLASTIC_OX_ENTEI_SAGE 938\n// End Plastic Ox story trainers.')
    for constant in ['TRAINERS_COUNT_EMERALD', 'MAX_TRAINERS_COUNT_EMERALD']:
        text = re.sub(r'(#define ' + constant + r'\s+)(\d+)',
                      lambda m: m[1] + str(max(939, int(m[2]))), text)
    put(path, text)
    path = 'src/data/trainers.party'
    text = re.sub(r'=== TRAINER_PLASTIC_OX_ENTEI_SAGE ===\n.*?(?=\n=== |\Z)', '', read(path), flags=re.S)
    put(path, text.rstrip() + '\n\n' + (BASE / 'trainers.party').read_text())

    # Imported visible pickups originally all used flag zero. Distinct virtual
    # flags preserve their persistence without consuming Hoenn quest flags.
    header = read('include/constants/plastic_ox_flags.h')
    aliases = read('include/constants/flags.h')
    names = sorted(set(re.findall(r'#define (FLAG_HIDE_POKEMON_MANSION_\w+)', aliases)))
    for index, name in enumerate(names, 8):
        new = name.replace('FLAG_HIDE_', 'FLAG_POX_HIDE_')
        line = f'#define {new} (POX_EVENT_FLAGS_START + {index})\n'
        if line not in header:
            header = header.replace('#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H',
                                    line + '#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H')
        aliases = re.sub(r'(#define ' + name + r'\s+)0\b', r'\g<1>' + new, aliases)
    put('include/constants/plastic_ox_flags.h', header)
    put('include/constants/flags.h', aliases)


if __name__ == '__main__':
    install(lambda p: Path(p).read_text(), lambda p, s: Path(p).write_text(s))
