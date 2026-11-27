#!/usr/bin/env python3
"""The old Regi caves on Route 127, south of Mossdeep, are empty side areas.
Regirock, Regice and Registeel moved to the Ruins of Alph chambers
(test_ruins_of_alph.py); the caves keep their mouths and open, bare inner rooms.

    plastic_ox/bin/pox-mgba-python plastic_ox/demo/test_regi_caves.py

Setup writes emulator RAM only (flags, bag, position); never ROM or save files.
"""
import struct

from pox_fixtures import Game, at, shot as _shot
from test_sudowoodo_v1 import (K, const, talk, give_item, bag, settle, wait_for_battle,
    run_code, opcode)

PLAYER_AVATAR_FLAG_SURFING = 1 << 3
# (cave map, Route 127 cave mouth, tablet, species)
CAVES = [
    ('DesertRuins', (28, 5), 'ITEM_ANCIENT_ROCK_TABLET', 'Regirock'),
    ('IslandCave', (29, 33), 'ITEM_ANCIENT_ICE_TABLET', 'Regice'),
    ('AncientTomb', (69, 12), 'ITEM_ANCIENT_STEEL_TABLET', 'Registeel'),
]


def game():
    g = Game()
    g.flag('FLAG_POX_TRIGGERS_ENABLED', True)
    run_code(g, opcode(g, 'callnative') + struct.pack('<I', g.syms['GivePlasticOxPlayerParty'] | 1)
             + opcode(g, 'releaseall'))
    return g


def shot(g, name):
    _shot(g, 'regi_' + name)


def pos(g):
    s = g.state()
    return s['x'], s['y']


def hold(g, key, frames=90):
    g.core.set_keys(key)
    g.frame(frames)
    g.core.clear_keys(key)
    g.frame(60)


def surf(g):
    a = g.syms['gPlayerAvatar']
    g.write(a, g.u8(a) | PLAYER_AVATAR_FLAG_SURFING)
    g.frame(10)


def wait_map(g, name, frames=600):
    for _ in range(frames // 10):
        if at(g, name):
            g.frame(90)
            return True
        g.frame(10)
    return False


def test_trail():
    g = game()
    g.warp('MossdeepCity', 33, 39)
    g.frame(60)
    surf(g)
    hold(g, K.KEY_RIGHT, 30)
    assert wait_map(g, 'Route127'), g.describe()
    assert pos(g) == (39, 1), pos(g)
    shot(g, 'route127_arrival')
    surf(g)
    hold(g, K.KEY_RIGHT, 30)
    assert wait_map(g, 'MossdeepCity'), g.describe()
    assert pos(g) == (33, 39), pos(g)
    print('PASS: Mossdeep south shore <-> Route 127 opens with no story flags', flush=True)


def visible(g):
    stride = g.sizes['gObjectEvents'] // 16
    return {g.u8(g.syms['gObjectEvents'] + i * stride + 8)
            for i in range(16) if g.u8(g.syms['gObjectEvents'] + i * stride) & 1} - {0xFF}


def test_cave(cave, mouth, tablet_name, species):
    tablet = const(tablet_name, 'items.h')
    g = game()
    for n in range(1, 9):
        g.flag(f'FLAG_BADGE{n:02}_GET', True)
    # Cave mouth on Route 127 and the cave's own exit.
    g.warp('Route127', mouth[0], mouth[1] + 1)
    g.frame(60)
    shot(g, cave + '_mouth')
    hold(g, K.KEY_UP, 30)
    assert wait_map(g, cave), (cave, g.describe())
    assert pos(g) == (8, 29), pos(g)
    hold(g, K.KEY_DOWN, 30)
    assert wait_map(g, 'Route127'), g.describe()
    assert pos(g) == (mouth[0], mouth[1] + 1), pos(g)

    # The inner room stands open with no tablet, and nothing is in it.
    assert bag(g, tablet) == 0
    g.warp(cave, 8, 21)
    g.frame(60)
    assert not visible(g), (cave, visible(g))
    r = talk(g, K.KEY_UP)
    text = ' '.join(r['text']).replace('\n', ' ')
    assert 'tablet' not in text.lower() and not r['battle'], r
    settle(g)
    hold(g, K.KEY_UP)
    g.frame(120)
    x, y = pos(g)
    assert at(g, cave) and y <= 11, (cave, x, y)
    shot(g, cave + '_inner')
    # Carrying the tablet changes nothing: no sage, no Regi, no battle.
    give_item(g, tablet)
    assert bag(g, tablet) == 1
    g.warp(cave, 8, 8)
    g.frame(60)
    assert not visible(g), (cave, visible(g))
    r = talk(g, K.KEY_UP)
    assert not r['battle'] and not r['text'], (species, r)
    print(f'PASS: {cave}: Route 127 mouth both ways, inner room open and empty, no {species} with or without '
          f'{tablet_name}', flush=True)



if __name__ == '__main__':
    test_trail()
    for args in CAVES:
        test_cave(*args)
    print('Route 127 caves: PASS', flush=True)
