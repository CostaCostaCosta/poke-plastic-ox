"""Restore FireRed Mt. Moon after region/story generation.

Canonical converted event sources are in mt_moon/. Geometry and matching FRLG
assets live in data/layouts and data/tilesets; see mt_moon/README.md.
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).with_suffix('')
FLOORS = ['MtMoon_1F_Frlg', 'MtMoon_B1F_Frlg', 'MtMoon_B2F_Frlg']


def install(read, put):
    def load(name):
        return json.loads(read(f'data/maps/{name}/map.json'))

    def save(name, data):
        put(f'data/maps/{name}/map.json', json.dumps(data, indent=2) + '\n')

    for floor, name in zip(['1F', 'B1F', 'B2F'], FLOORS):
        data = json.loads((BASE / f'{floor}.json').read_text())
        if floor == '1F':
            data['warp_events'][3].update(dest_map='MAP_ROUTE44_HNS', dest_warp_id='0')
        elif floor == 'B1F':
            data['warp_events'][7].update(dest_map='MAP_ROUTE33_HNS', dest_warp_id='0')
        save(name, data)
        put(f'data/maps/{name}/scripts.inc', (BASE / f'{floor}.inc').read_text())

    for name in ['Route44_hns', 'Route33_hns', 'MtMoon_Cave_hns']:
        data = load(name)
        for kind in ['coord_events', 'bg_events', 'object_events']:
            data[kind] = [e for e in data[kind] if not e.get('script', '').startswith(
                ('PoxRegion_route44_moon', 'PoxRegion_moon_route33', 'PoxMoon_EnterFromRoute44'))]
        if name == 'Route44_hns':
            data['warp_events'] = [dict(x=68, y=13, elevation=0,
                dest_map='MAP_MT_MOON_1F', dest_warp_id='3')]
            data['coord_events'].append(dict(type='trigger', x=68, y=13, elevation=0,
                var='VAR_POX_PORTAL_TRIGGER', var_value=0, script='PoxMoon_EnterFromRoute44'))
        elif name == 'Route33_hns':
            data['warp_events'] = [dict(x=27, y=17, elevation=0,
                dest_map='MAP_MT_MOON_B1F', dest_warp_id='7')]
        else:
            # Retired map remains registered for saves made in the old cave.
            data['object_events'] = []
            data['coord_events'] = []
            data['warp_events'] = []
            data['bg_events'] = []
            put(f'data/maps/{name}/scripts.inc', f'{name}_MapScripts::\n'
                '\tmap_script MAP_SCRIPT_ON_FRAME_TABLE, PoxMoon_LegacyTable\n\t.byte 0\n'
                'PoxMoon_LegacyTable::\n\tmap_script_2 VAR_POX_PORTAL_TRIGGER, 0, PoxMoon_EnterFromRoute44\n\t.2byte 0\n')
        save(name, data)
    path = 'data/maps/Route44_hns/scripts.inc'
    script = read(path)
    if 'PoxMoon_EnterFromRoute44::' not in script:
        script += '\nPoxMoon_EnterFromRoute44::\n\tlockall\n\twarp MAP_MT_MOON_1F, 18, 36\n\twaitstate\n\treleaseall\n\tend\n'
    put(path, script)

    trainers = json.loads((BASE / 'trainers.json').read_text())
    path = 'include/constants/opponents.h'
    text = re.sub(r'^#define TRAINER_PLASTIC_OX_MOON_.*\n', '', read(path), flags=re.M)
    defs = ''.join(f'#define {name} {number}\n' for name, number in trainers.items())
    text = text.replace('// End Plastic Ox story trainers.', defs + '// End Plastic Ox story trainers.')
    for constant in ['TRAINERS_COUNT_EMERALD', 'MAX_TRAINERS_COUNT_EMERALD']:
        text = re.sub(r'(#define ' + constant + r'\s+)(\d+)',
                      lambda match: match[1] + str(max(926, int(match[2]))), text)
    put(path, text)
    path = 'src/data/trainers.party'
    text = re.sub(r'=== TRAINER_PLASTIC_OX_MOON_\w+ ===\n.*?(?=\n=== |\Z)', '', read(path), flags=re.S)
    put(path, text.rstrip() + '\n\n' + (BASE / 'trainers.party').read_text().rstrip() + '\n')


if __name__ == '__main__':
    install(lambda p: Path(p).read_text(), lambda p, s: Path(p).write_text(s))
