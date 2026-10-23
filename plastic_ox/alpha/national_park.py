"""Restore the source Johto gate warps and Cut seam after story generation."""
import json
from pathlib import Path

BASE = Path(__file__).with_suffix('')
GATE = 'Gate_NationalPark_hns'
OBSOLETE = ('PoxRegion_route35_park_', 'PoxRegion_park_route36_')


def install(read, put):
    def load(name):
        return json.loads(read(f'data/maps/{name}/map.json'))

    def save(name, data):
        put(f'data/maps/{name}/map.json', json.dumps(data, indent=2) + '\n')

    groups = json.loads(read('data/maps/map_groups.json'))
    if GATE not in groups['gMapGroup_PlasticOxInteriors']:
        groups['gMapGroup_PlasticOxInteriors'].append(GATE)
    put('data/maps/map_groups.json', json.dumps(groups, indent=2) + '\n')
    layouts = json.loads(read('data/layouts/layouts.json'))
    layout = json.loads((BASE / 'layout.json').read_text())
    if not any(l['id'] == layout['id'] for l in layouts['layouts']):
        layouts['layouts'].append(layout)
    put('data/layouts/layouts.json', json.dumps(layouts, indent=2) + '\n')
    save(GATE, json.loads((BASE / 'gate.json').read_text()))
    put(f'data/maps/{GATE}/scripts.inc', (BASE / 'gate.inc').read_text())

    entrances = {
        'Route35_hns': [(17, 5, 0), (18, 5, 0)],
        'Route36_hns': [(16, 20, 3)],
        'NationalPark_Normal_hns': [(12, 49, 1), (13, 49, 1), (40, 19, 2),
                                    (11, 49, 1), (14, 49, 1)],
    }
    for name, doors in entrances.items():
        data = load(name)
        for field in ('coord_events', 'object_events', 'bg_events'):
            data[field] = [e for e in data.get(field, [])
                           if not e.get('script', '').startswith(OBSOLETE)]
        if name == 'Route35_hns':
            data['coord_events'] = [e for e in data['coord_events']
                                    if e.get('script') != 'PoxRegion_goldenrod_route35_b']
        positions = {(x, y) for x, y, _ in doors}
        data['warp_events'] = [w for w in data.get('warp_events', [])
                               if (w['x'], w['y']) not in positions]
        data['warp_events'] += [dict(x=x, y=y, elevation=0,
                                   dest_map='MAP_GATE_NATIONAL_PARK_HNS', dest_warp_id=str(w))
                                for x, y, w in doors]
        if name != 'NationalPark_Normal_hns':
            other, direction, offset = (('MAP_ROUTE36_HNS', 'up', 16) if name == 'Route35_hns'
                                        else ('MAP_ROUTE35_HNS', 'down', -16))
            data['connections'] = [c for c in data.get('connections', []) if c['map'] != other]
            data['connections'].append(dict(map=other, direction=direction, offset=offset))
        else:
            for obj in data['object_events']:
                if obj['script'] == 'PlasticOxContest_EventScript_Attendant':
                    obj['script'] = 'NationalPark_Normal_EventScript_Npc3'
        save(name, data)

    path = 'data/event_scripts.s'
    text = read(path)
    line = f'\t.include "data/maps/{GATE}/scripts.inc"\n'
    if line not in text:
        text += '\n' + line
    put(path, text)


if __name__ == '__main__':
    install(lambda p: Path(p).read_text(),
            lambda p, s: (Path(p).parent.mkdir(parents=True, exist_ok=True), Path(p).write_text(s)))
