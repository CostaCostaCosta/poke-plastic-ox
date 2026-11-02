"""Reviewed Route 36/37 and National Park events, applied after region generation.

Trainer positions/roster follow pokehns-expansion 44f50eedefe58691b0444973e4138e9190d8fafc.
The twins share one trainer ID and victory flag, as in the Gen 2 games.
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).with_suffix('')


def install(read, put):
    for name in ('Route36_hns', 'Route37_hns', 'NationalPark_Normal_hns'):
        path = f'data/maps/{name}/map.json'
        data = json.loads(read(path))
        authored = json.loads((BASE / f'{name}.json').read_text())
        # Keep authored story actors, gatehouse warps, items, and other exits.
        for obj in data['object_events']:
            replacement = next((o for o in authored['objects']
                                if (o['x'], o['y']) == (obj['x'], obj['y'])), None)
            if replacement:
                obj.update(replacement)
        if name == 'Route37_hns':
            data['object_events'] = [o for o in data['object_events']
                                    if not o['script'].startswith('PoxRegion_route37_ecruteak')]
            for obj in authored['add_objects']:
                if not any(o['script'] == obj['script'] for o in data['object_events']):
                    data['object_events'].append(obj)
        if name == 'NationalPark_Normal_hns':
            for obj in data['object_events']:
                if obj['script'] == 'Pox_PU_PARK' and obj['x'] == 25 and obj['y'] == 30:
                    obj.update(next(o for o in authored['objects'] if o['y'] == 30))
        if name == 'Route37_hns':
            for field in ('coord_events', 'bg_events'):
                data[field] = [e for e in data[field]
                               if not e.get('script', '').startswith('PoxRegion_route37_ecruteak')
                               and e.get('script') != 'Route37_EventScript_CitySign']
            data['bg_events'].append(dict(type='sign', x=20, y=13, elevation=0,
                player_facing_dir='BG_EVENT_PLAYER_FACING_ANY', script='Route37_EventScript_CitySign'))
            next(c for c in data['connections'] if c['map'] == 'MAP_ECRUTEAK_CITY_HNS')['offset'] = -16
        put(path, json.dumps(data, indent=2) + '\n')
        put(f'data/maps/{name}/scripts.inc', (BASE / f'{name}.inc').read_text())

    path = 'data/maps/EcruteakCity_hns/map.json'
    data = json.loads(read(path))
    for field in ('coord_events', 'bg_events', 'object_events'):
        data[field] = [e for e in data[field]
                       if not e.get('script', '').startswith('PoxRegion_route37_ecruteak')]
    next(c for c in data['connections'] if c['map'] == 'MAP_ROUTE37_HNS')['offset'] = 16
    put(path, json.dumps(data, indent=2) + '\n')

    path = 'include/constants/opponents.h'
    text = re.sub(r'^#define TRAINER_PLASTIC_OX_JOHTO_.*\n', '', read(path), flags=re.M)
    trainers = json.loads((BASE / 'trainers.json').read_text())
    defs = ''.join(f'#define {name} {data["id"]}\n' for name, data in trainers.items())
    text = text.replace('// End Plastic Ox story trainers.', defs + '// End Plastic Ox story trainers.')
    for constant in ('TRAINERS_COUNT_EMERALD', 'MAX_TRAINERS_COUNT_EMERALD'):
        text = re.sub(r'(#define ' + constant + r'\s+)(\d+)',
                      lambda m: m[1] + str(max(938, int(m[2]))), text)
    put(path, text)
    path = 'src/data/trainers.party'
    text = read(path)
    # Retain existing teams; the canonical source supplies new/missing entries.
    blocks = re.split(r'(?=^=== TRAINER_)', (BASE / 'trainers.party').read_text(), flags=re.M)
    for block in blocks:
        if block.strip() and block.splitlines()[0] not in text:
            text = text.rstrip() + '\n\n' + block.strip() + '\n'
    put(path, text)


if __name__ == '__main__':
    install(lambda p: Path(p).read_text(), lambda p, s: Path(p).write_text(s))
