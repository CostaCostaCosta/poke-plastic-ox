"""Reapply converted Ecruteak interiors and the city's doors after story generation."""
import json
from pathlib import Path

BASE = Path(__file__).with_suffix('')
CITY = 'EcruteakCity_hns'
ROUTE38 = 'Route38_hns'

CITY_WARPS = {
    0: dict(x=39, y=47, dest_map='MAP_ECRUTEAK_CITY_POKEMON_CENTER_HNS', dest_warp_id='0'),
    1: dict(x=48, y=40, dest_map='MAP_ECRUTEAK_CITY_MART_HNS', dest_warp_id='0'),
    2: dict(x=19, y=40, dest_map='MAP_ECRUTEAK_CITY_HOUSE1_HNS', dest_warp_id='0'),
}
CITY_DOORS = [
    dict(x=39, y=40, dest_map='MAP_ECRUTEAK_CITY_THEATER_HNS', dest_warp_id='0'),
    dict(x=20, y=48, dest_map='MAP_ECRUTEAK_CITY_GYM_HNS', dest_warp_id='0'),
    dict(x=28, y=47, dest_map='MAP_ECRUTEAK_CITY_HOUSE2_HNS', dest_warp_id='0'),
    dict(x=39, y=22, dest_map='MAP_ECRUTEAK_CITY_SAGE_OFFICE1_HNS', dest_warp_id='0'),
    dict(x=36, y=16, dest_map='MAP_ECRUTEAK_CITY_SAGE_OFFICE2_HNS', dest_warp_id='0'),
    dict(x=8, y=35, dest_map='MAP_GATE_ECRUTEAK_CITY_ROUTE38_HNS', dest_warp_id='0'),
]
# ROUTE 38 lost its ECRUTEAK "left" seam in wave 3; the gatehouse replaces it.
ROUTE38_WARP = dict(x=43, y=16, elevation=0,
                    dest_map='MAP_GATE_ECRUTEAK_CITY_ROUTE38_HNS', dest_warp_id='1')

# The donor's ECRUTEAK SAGE OFFICE 2 front door sits on (36,16), which in our
# copy of the city is a wall metatile completely enclosed by solid tiles (the
# four neighbours are solid too), so no standable tile exists next to it and the
# engine has no metatile behaviour there that can fire a warp. hns triggers
# warps on plain tiles; this ROM does not. The room stays reachable through the
# donor's own interior link from SAGE OFFICE 1, so the dead door is dropped
# rather than left as a warp nothing can set off.
CITY_WARP_DROPS = [(36, 16), (55, 42)]

# An object event blocks movement, so any NPC the donor parks on a door tile
# seals that door. SILVER stands on the theatre door (39,40) in the donor; step
# him one tile north, facing back into it.
NPC_SHIFTS = {
    (39, 40): (39, 39, 'MOVEMENT_TYPE_FACE_DOWN'),
}


def reserve_east(read, put):
    """Retire the eastern road; reserve its city entrances for the future League."""
    for name in (CITY, 'Route119'):
        path = f'data/maps/{name}/map.json'
        data = json.loads(read(path))
        for field in ('object_events', 'coord_events', 'bg_events'):
            data[field] = [e for e in data[field]
                           if not e.get('script', '').startswith('PoxRegion_ecruteak_route119')
                           and not (e.get('script') == 'EcruteakCity_EventScript_KimonoRoadblock'
                                    and (e['x'], e['y']) in ((52, 32), (53, 32), (55, 42)))]
        if name == CITY:
            data['warp_events'] = [w for w in data['warp_events']
                                   if (w['x'], w['y']) != (55, 42)]
            for x, y in ((53, 32), (55, 42)):
                data['object_events'].append(dict(
                    graphics_id='OBJ_EVENT_GFX_SIGN', x=x, y=y, elevation=0,
                    movement_type='MOVEMENT_TYPE_NONE', movement_range_x=0,
                    movement_range_y=0, trainer_type='TRAINER_TYPE_NONE',
                    trainer_sight_or_berry_tree_id='0',
                    script='EcruteakCity_EventScript_KimonoRoadblock', flag='0'))
            for obj in data['object_events']:
                if obj.get('script') == 'Pox_WeatherRoad':
                    obj['script'] = 'EcruteakCity_EventScript_KimonoRoadblock'
        put(path, json.dumps(data, indent=2) + '\n')
    path = f'data/maps/{CITY}/scripts.inc'
    text = read(path).replace(
        'Please help MORTY at the BURNED\\nTOWER, then earn his GYM BADGE.\\pAfter that, you may pass east.$',
        'EAST GATE CLOSED\\nFuture POKéMON LEAGUE site.$')
    put(path, text)


def install(read, put):
    def load(name):
        return json.loads(read(f'data/maps/{name}/map.json'))

    def save(name, data):
        put(f'data/maps/{name}/map.json', json.dumps(data, indent=2) + '\n')

    manifest = json.loads((BASE / 'source_manifest.json').read_text())

    city = load(CITY)
    warps = city['warp_events']
    # Preserve indices 0..2 (saved dynamic warps and story warps depend on them).
    for index, door in CITY_WARPS.items():
        warps[index] = dict(door, elevation=0)
    for door in CITY_DOORS:
        entry = dict(door, elevation=0)
        existing = next((i for i, w in enumerate(warps)
                         if (w['x'], w['y']) == (door['x'], door['y'])), None)
        if existing is None:
            warps.append(entry)
        else:
            warps[existing] = entry
    # Existing authored route connections, coordinate events and story NPCs stay intact.
    for obj in city['object_events']:
        shift = NPC_SHIFTS.get((obj['x'], obj['y']))
        if shift:
            obj['x'], obj['y'], obj['movement_type'] = shift
    city['warp_events'] = [w for w in city['warp_events']
                           if (w['x'], w['y']) not in CITY_WARP_DROPS]
    save(CITY, city)

    # The donor's warp ids index tables this port renumbers (the city door list
    # above, and interiors whose leading warp was dropped), so any warp that
    # still carries a donor id has to be retargeted onto the tile the donor
    # meant. Doing it by coordinate keeps it correct even though our order
    # differs from the donor's.
    city_door_at = {(w['x'], w['y']): i for i, w in enumerate(city['warp_events'])}
    city_id = city['id']
    interior_ids = {name: json.loads(read(f'data/maps/{name}/map.json'))['id']
                    for name in manifest['maps']}
    interior_renumber = {name: entry['donor_index_to_converted']
                         for name, entry in manifest['maps'].items()}

    for name in manifest['maps']:
        # The converted rooms already point at MAP_DYNAMIC or at a converted
        # destination, so they are copied across verbatim.
        put(f'data/maps/{name}/map.json', (BASE / f'{name}.json').read_text())
        put(f'data/maps/{name}/scripts.inc', (BASE / f'{name}.inc').read_text())

    def retarget(name):
        data = load(name)
        my_id = interior_ids[name]
        changed = 0
        for warp in data['warp_events']:
            dest = warp['dest_map']
            if dest == my_id or dest == 'MAP_DYNAMIC' or not str(warp['dest_warp_id']).isdigit():
                continue
            if dest == city_id:
                donor = manifest['donor_city_warps']
                tile = donor[int(warp['dest_warp_id'])] \
                    if int(warp['dest_warp_id']) < len(donor) else None
                index = city_door_at.get((tile['x'], tile['y'])) if tile else None
            elif dest in interior_ids.values():
                owner = next(n for n, v in interior_ids.items() if v == dest)
                index = interior_renumber[owner].get(str(warp['dest_warp_id']))
            else:
                continue
            if index is None:
                raise SystemExit(
                    f'{name}: warp ({warp["x"]},{warp["y"]}) -> {dest} '
                    f'#{warp["dest_warp_id"]} has no converted destination')
            warp['dest_warp_id'] = str(index)
            changed += 1
        if changed:
            save(name, data)
        return changed

    retargeted = sum(retarget(name) for name in manifest['maps'])

    # ROUTE 38 ↔ gatehouse. ROUTE 38 had no warps at all, so index 0 is free.
    route38 = load(ROUTE38)
    if not any(w['dest_map'] == 'MAP_GATE_ECRUTEAK_CITY_ROUTE38_HNS'
               for w in route38['warp_events']):
        route38['warp_events'].append(dict(ROUTE38_WARP))
    save(ROUTE38, route38)

    p = 'data/event_scripts.s'
    text = read(p)
    for name in manifest['maps']:
        line = f'\t.include "data/maps/{name}/scripts.inc"\n'
        if line not in text:
            text += '\n' + line
    put(p, text)
    reserve_east(read, put)
    return {'retargeted_warps': retargeted}


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    install(lambda p: (root / p).read_text(),
            lambda p, s: ((root / p).parent.mkdir(parents=True, exist_ok=True),
                          (root / p).write_text(s)))