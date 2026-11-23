#!/usr/bin/env python3
"""Tin Tower: sages come home to the Ecruteak sage office, the stair opens at
five, and the Moltres sage waits on the roof.

    plastic_ox/bin/pox-mgba-python plastic_ox/demo/test_tin_tower.py

Setup writes emulator RAM only (flags, position); never ROM or save files.
"""
import json
import struct
from collections import deque
from pathlib import Path

from test_cinnabar import game, at, shot as _shot
from test_sudowoodo_v1 import K, talk, settle, wait_for_battle, battle_mon, const

ROOT = Path(__file__).resolve().parents[2]
OFFICE = 'EcruteakCity_SageOffice2_hns'
# In the order of the office's object events (local ids 3..8); 1 = caretaker, 2 = keeper.
SAGES = ['FLAG_POX_ENTEI', 'FLAG_POX_HIDE_ARTICUNO', 'FLAG_POX_CAUGHT_RAIKOU',
         'FLAG_POX_CAUGHT_REGIROCK', 'FLAG_POX_CAUGHT_REGICE', 'FLAG_POX_CAUGHT_REGISTEEL']
KEEPER = 2


def shot(g, name):
    _shot(g, 'tin_tower_' + name)


def pos(g):
    s = g.state()
    return s['x'], s['y']


def visible(g):
    stride = g.sizes['gObjectEvents'] // 16
    return {g.u8(g.syms['gObjectEvents'] + i * stride + 8)
            for i in range(16) if g.u8(g.syms['gObjectEvents'] + i * stride) & 1}


def hold(g, key, frames=90):
    g.core.set_keys(key)
    g.frame(frames)
    g.core.clear_keys(key)
    g.frame(60)


def wait_map(g, name, frames=600):
    for _ in range(frames // 10):
        if at(g, name):
            g.frame(90)
            return True
        g.frame(10)
    return False


def home(g, count):
    for i, flag in enumerate(SAGES):
        g.flag(flag, i < count)


def test_route_connected():
    """Static: trail and tower tiles plus warps reach the roof from the office door."""
    layouts = {l['id']: l for l in json.loads((ROOT / 'data/layouts/layouts.json').read_text())['layouts'] if 'id' in l}
    maps = {}
    for d in [*(ROOT / 'data/maps').glob('TinTower_*'), ROOT / 'data/maps/BellchimeTrail_hns']:
        data = json.loads((d / 'map.json').read_text())
        lay = layouts[data['layout']]
        raw = (ROOT / lay['blockdata_filepath']).read_bytes()
        blocks = struct.unpack('<' + 'H' * (len(raw) // 2), raw)
        maps[data['id']] = (data, lay, blocks)
    start = ('MAP_BELLCHIME_TRAIL_HNS', 9, 37)
    seen, todo = {start}, deque([start])
    while todo:
        m, x, y = todo.popleft()
        data, lay, blocks = maps[m]
        for w in data['warp_events']:
            if (w['x'], w['y']) == (x, y) and w['dest_map'] in maps:
                dest = maps[w['dest_map']][0]['warp_events'][int(w['dest_warp_id'])]
                nxt = (w['dest_map'], dest['x'], dest['y'])
                if nxt not in seen:
                    seen.add(nxt)
                    todo.append(nxt)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < lay['width'] and 0 <= ny < lay['height'] \
                    and not (blocks[ny * lay['width'] + nx] >> 10) & 3 and (m, nx, ny) not in seen:
                seen.add((m, nx, ny))
                todo.append((m, nx, ny))
    assert ('MAP_TIN_TOWER_ROOF_DAY_HNS', 10, 11) in seen
    print('PASS: office door -> Bellchime Trail -> Tin Tower 1F -> roof is walkable', flush=True)


def test_office_shut():
    g = game()
    home(g, 4)
    g.warp(OFFICE, 7, 5)
    g.frame(120)
    ids = visible(g)
    assert {1, KEEPER, 3, 4, 5, 6} <= ids and not ({7, 8} & ids), ids
    shot(g, 'office_four')
    hold(g, K.KEY_RIGHT)
    assert at(g, OFFICE) and pos(g) == (7, 5), (pos(g), g.describe())
    r = talk(g, K.KEY_RIGHT)
    text = ' '.join(r['text']).replace('\n', ' ')
    assert 'five' in text and '4' in text and not r['battle'], r
    print('PASS: four sages home: four visible, keeper holds the tower door and counts 4', flush=True)


def test_office_open():
    g = game()
    home(g, 5)
    g.warp(OFFICE, 7, 5)
    g.frame(120)
    ids = visible(g)
    assert {1, KEEPER, 3, 4, 5, 6, 7} <= ids and 8 not in ids, ids
    shot(g, 'office_five')
    hold(g, K.KEY_RIGHT, 120)
    assert wait_map(g, 'BellchimeTrail_hns'), g.describe()
    assert pos(g) == (8, 37), pos(g)
    shot(g, 'trail_arrival')
    hold(g, K.KEY_LEFT, 30)
    assert wait_map(g, OFFICE), g.describe()
    assert pos(g) == (8, 5), pos(g)
    # Trail door into the tower, and back out.
    g.warp('BellchimeTrail_hns', 35, 42)
    g.frame(120)
    shot(g, 'trail_door')
    hold(g, K.KEY_UP, 30)
    assert wait_map(g, 'TinTower_1F_hns'), g.describe()
    assert pos(g) == (9, 17), pos(g)
    shot(g, '1f')
    hold(g, K.KEY_DOWN, 30)
    assert wait_map(g, 'BellchimeTrail_hns'), g.describe()
    assert pos(g) == (35, 42), pos(g)   # door exit steps the player out
    print('PASS: five sages home: keeper steps aside; office <-> Bellchime Trail <-> Tin Tower 1F', flush=True)


def test_roof():
    g = game()
    home(g, 6)
    g.warp('TinTower_1F_hns', 9, 5)
    g.frame(120)
    hold(g, K.KEY_UP, 30)
    assert wait_map(g, 'TinTower_RoofDay_hns'), g.describe()
    assert pos(g) == (10, 14), pos(g)
    hold(g, K.KEY_UP, 60)
    settle(g)
    shot(g, 'roof')
    assert pos(g) == (10, 11), pos(g)
    r = talk(g, K.KEY_UP)
    assert r['battle'] and wait_for_battle(g), r
    lead = battle_mon(g, 1)
    assert lead['species'] == const('SPECIES_METAGROSS', 'species.h'), lead
    shot(g, 'moltres_sage_battle')
    print('PASS: 1F ladder reaches the roof; Moltres sage battle opens with Metagross', lead, flush=True)


if __name__ == '__main__':
    test_route_connected()
    test_office_shut()
    test_office_open()
    test_roof()
    print('Tin Tower: PASS', flush=True)
