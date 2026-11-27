#!/usr/bin/env python3
"""Meteor Falls: JIRACHI and its sage in the Bagon chamber (B1F 2R), and the
sage's homecoming in the Ecruteak sage office.

    plastic_ox/bin/pox-mgba-python plastic_ox/demo/test_meteor_falls.py

Setup writes emulator RAM only (flags, position); never ROM or save files.
"""
import json
import struct
from collections import deque
from pathlib import Path

from pox_fixtures import game, at, shot as _shot
from test_sudowoodo_v1 import K, talk, settle, wait_for_battle, battle_mon, const
from test_tin_tower import visible, home, OFFICE

ROOT = Path(__file__).resolve().parents[2]
CHAMBER = 'MeteorFalls_B1F_2R'
JIRACHI, SAGE = 2, 3          # local ids after the Dragon Claw ball (1)
OFFICE_JIRACHI = 9            # appended after the six home sages (3..8)


def shot(g, name):
    _shot(g, 'meteor_falls_' + name)


def test_chamber_reachable():
    """Static: walk + Surf (collision-free tiles) from Route 115's door reaches the sage."""
    layouts = {l['id']: l for l in json.loads((ROOT / 'data/layouts/layouts.json').read_text())['layouts'] if 'id' in l}
    maps = {}
    for d in (ROOT / 'data/maps').glob('MeteorFalls_*'):
        data = json.loads((d / 'map.json').read_text())
        lay = layouts[data['layout']]
        raw = (ROOT / lay['blockdata_filepath']).read_bytes()
        maps[data['id']] = (data, lay, struct.unpack('<' + 'H' * (len(raw) // 2), raw))
    start = ('MAP_METEOR_FALLS_1F_1R', 6, 39)
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
    assert ('MAP_METEOR_FALLS_B1F_2R', 6, 5) in seen
    objs = json.loads((ROOT / f'data/maps/{CHAMBER}/map.json').read_text())['object_events']
    assert any(o['x'] == 5 and o['y'] == 3 and 'DRAGON_CLAW' in o['flag'] for o in objs), 'Dragon Claw ball kept'
    print('PASS: Route 115 -> Meteor Falls -> Bagon chamber sage tile reachable; Dragon Claw ball kept', flush=True)


def test_sage_battle():
    g = game()
    g.flag('FLAG_POX_CAUGHT_JIRACHI', False)
    g.warp(CHAMBER, 7, 4)
    g.frame(120)
    ids = visible(g)
    assert {JIRACHI, SAGE} <= ids, ids
    shot(g, 'chamber')
    r = talk(g, K.KEY_LEFT)
    text = ' '.join(r['text']).replace('\n', ' ')
    assert 'BAGON' in text and r['battle'] and wait_for_battle(g), r
    lead = battle_mon(g, 1)
    assert lead['species'] == const('SPECIES_MILOTIC', 'species.h'), lead
    shot(g, 'sage_battle')
    print('PASS: Bagon chamber shows JIRACHI and its sage; sage battle opens with Milotic', lead, flush=True)


def test_caught_hides_and_comes_home():
    g = game()
    g.flag('FLAG_POX_CAUGHT_JIRACHI', True)
    g.warp(CHAMBER, 7, 4)
    g.frame(120)
    ids = visible(g)
    assert not ({JIRACHI, SAGE} & ids), ids
    home(g, 0)
    g.warp(OFFICE, 7, 5)
    g.frame(120)
    ids = visible(g)
    assert OFFICE_JIRACHI in ids and not ({3, 4, 5, 6, 7, 8} & ids), ids
    shot(g, 'office_jirachi')
    r = talk(g, K.KEY_RIGHT)
    text = ' '.join(r['text']).replace('\n', ' ')
    assert '1' in text and not r['battle'], r
    print('PASS: caught JIRACHI hides the chamber pair; its sage is home and the keeper counts 1', flush=True)


if __name__ == '__main__':
    test_chamber_reachable()
    test_sage_battle()
    test_caught_hides_and_comes_home()
    print('Meteor Falls: PASS', flush=True)
