#!/usr/bin/env python3
"""Fly Key: picked up in the Route 119 Wingull house, then used from the field."""
import json
import re

from test_story import StoryGame, ROOT
from walklib import K
from walk_demo import object_tiles

FLY_KEY = int(re.search(r'ITEM_FLY_KEY = (\d+)', (ROOT/'include/constants/items.h').read_text())[1])
BALL = (1, 2)


def finish(g):
    for _ in range(350):
        g.tap(K.KEY_A, hold=2, wait=10)
        if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            g.frame(60)
            return
    raise AssertionError('Dialogue did not release controls')


def key_items(g):
    pocket = g.syms['gBagPockets'] + 4 * (g.sizes['gBagPockets']//5)
    slots = g.u32(pocket)
    return [g.u16(slots+4*i) for i in range(g.u8(pocket+4))]


def callback2(g):
    return g.u32(g.syms['gMain'] + 4) & ~1  # drop the Thumb bit


def wait_callback(g, name, frames=600):
    for _ in range(frames // 10):
        g.frame(10)
        if callback2(g) == g.syms[name]:
            return
    raise AssertionError(f'never reached {name}: {g.describe()}')


def npc_count(g):
    base = g.symbol_address('gObjectEvents')
    return sum(1 for i in range(16)
               if g.u8(base + i*0x24) & 1 and not g.u8(base + i*0x24 + 2) & 1)


def register(g):
    g.write(int(g.state()['ptr'], 16)+0x496, FLY_KEY, 2)


def main():
    out = ROOT/'plastic_ox/demo/shots'
    g = StoryGame()
    g.run('Pox_Treecko')
    assert g.count() >= 1

    # Pick up the ball in the Wingull house.
    g.warp('Route119_House', BALL[0], BALL[1]+1)
    assert BALL in object_tiles(g), 'Fly Key ball missing'
    before = npc_count(g)
    g.tap(K.KEY_UP, hold=2, wait=20)
    g.tap(K.KEY_A, hold=2, wait=20)
    finish(g)
    assert FLY_KEY in key_items(g), key_items(g)
    assert g.flag('FLAG_POX_HIDE_ROUTE119_FLY_KEY')
    assert npc_count(g) == before - 1, 'Ball still present after pickup'
    g.shot('fly_key_pickup.png')
    g.warp('Route119_House', BALL[0], BALL[1]+1)
    assert npc_count(g) == before - 1, 'Ball respawned after reload'
    print('PASS: Fly Key picked up once in the Route 119 Wingull house', flush=True)

    # Indoors the key must refuse cleanly.
    register(g)
    g.tap(K.KEY_SELECT, hold=2, wait=60)
    assert callback2(g) != g.syms['CB2_FlyMap'], 'Fly map opened indoors'
    finish(g)
    print('PASS: Fly Key refuses indoors', flush=True)

    # Outdoors: open the map, cancel back to the field.
    g.flag('FLAG_VISITED_FORTREE_CITY', True)
    g.warp('FortreeCity', 10, 4)
    register(g)
    g.tap(K.KEY_SELECT, hold=2, wait=10)
    wait_callback(g, 'CB2_FlyMap')
    g.frame(60)
    g.shot('fly_key_map.png')
    g.tap(K.KEY_B, hold=2, wait=10)
    wait_callback(g, 'CB2_Overworld')
    g.frame(60)
    assert (g.state()['x'], g.state()['y']) == (10, 4), g.describe()
    print('PASS: cancelling the Fly Key map returns to the field', flush=True)

    # Open again and fly to Fortree's landing spot.
    g.tap(K.KEY_SELECT, hold=2, wait=10)
    wait_callback(g, 'CB2_FlyMap')
    g.frame(60)
    g.tap(K.KEY_A, hold=2, wait=10)
    wait_callback(g, 'CB2_Overworld', 1800)
    g.frame(400)
    st = g.state()
    assert (st['x'], st['y']) == (5, 7), ('did not land at the Fortree heal spot', g.describe())
    assert FLY_KEY in key_items(g), 'Fly Key consumed'
    g.shot('fly_key_landed.png')
    print('PASS: Fly Key flew to', g.describe(), flush=True)


def map_id(g, name):
    groups = json.loads((ROOT/'data/maps/map_groups.json').read_text())
    for i, group in enumerate(groups['group_order']):
        if name in groups[group]:
            return i, groups[group].index(name)
    raise KeyError(name)


def fly_by_cursor(g, moves, label):
    g.tap(K.KEY_SELECT, hold=2, wait=10)
    wait_callback(g, 'CB2_FlyMap')
    g.frame(60)
    for key, n in moves:
        for _ in range(n):
            g.tap(key, hold=2, wait=24)
    g.shot(f'fly_map_{label}.png')
    g.tap(K.KEY_A, hold=2, wait=10)
    wait_callback(g, 'CB2_Overworld', 1800)
    g.frame(400)


def region_map_tests():
    g = StoryGame()
    g.run('Pox_Treecko')
    g.warp('Route119_House', BALL[0], BALL[1]+1)
    g.tap(K.KEY_UP, hold=2, wait=20)
    g.tap(K.KEY_A, hold=2, wait=20)
    finish(g)
    assert FLY_KEY in key_items(g)
    # Visiting a Johto town sets its Plastic Ox visited flag automatically.
    for town, flag, spot in [('GoldenrodCity_hns', 'FLAG_POX_VISITED_GOLDENROD', (28, 37)),
                             ('EcruteakCity_hns', 'FLAG_POX_VISITED_ECRUTEAK', (39, 48)),
                             ('CherrygroveCity_hns', 'FLAG_POX_VISITED_CHERRYGROVE', (47, 8)),
                             ('BlackthornCity_hns', 'FLAG_POX_VISITED_BLACKTHORN', (27, 49))]:
        assert not g.flag(flag), flag
        g.warp(town, *spot)
        assert g.flag(flag), f'{flag} not set on entering {town}'
    print('PASS: entering Johto towns marks them as fly destinations', flush=True)
    for flag in ['FLAG_VISITED_FORTREE_CITY', 'FLAG_POX_VISITED_INDIGO']:
        g.flag(flag, True)

    # Fortree (19,4) -> Ecruteak (14,3): five left, one up.
    g.warp('FortreeCity', 10, 4)
    register(g)
    fly_by_cursor(g, [(K.KEY_LEFT, 5), (K.KEY_UP, 1)], 'ecruteak')
    st = g.state()
    assert (st['group'], st['num']) == map_id(g, 'EcruteakCity_hns') and (st['x'], st['y']) == (39, 48), g.describe()
    print('PASS: flew Fortree -> Ecruteak', flush=True)
    # Ecruteak (14,3) -> Indigo Plateau (9,3): five left.
    fly_by_cursor(g, [(K.KEY_LEFT, 5)], 'indigo')
    st = g.state()
    assert (st['group'], st['num']) == map_id(g, 'IndigoPlateau_hns') and (st['x'], st['y']) == (11, 7), g.describe()
    print('PASS: flew Ecruteak -> Indigo Plateau (League)', flush=True)
    # From a Kanto map (Lavender) the same Plastic Ox map is shown: Lavender
    # (21,7) -> Goldenrod (14,7) is seven cells left on that grid.
    g.warp('LavenderTown_hns', 9, 7)
    fly_by_cursor(g, [(K.KEY_LEFT, 7)], 'goldenrod_from_kanto')
    st = g.state()
    assert (st['group'], st['num']) == map_id(g, 'GoldenrodCity_hns') and (st['x'], st['y']) == (28, 37), g.describe()
    print('PASS: Kanto-side fly map uses the Plastic Ox grid (Lavender -> Goldenrod)', flush=True)
    # An unvisited town cannot be chosen: Saffron (25,7) from Lavender.
    g.warp('LavenderTown_hns', 9, 7)
    g.tap(K.KEY_SELECT, hold=2, wait=10)
    wait_callback(g, 'CB2_FlyMap')
    g.frame(60)
    for _ in range(4):
        g.tap(K.KEY_RIGHT, hold=2, wait=24)
    g.tap(K.KEY_A, hold=2, wait=60)
    assert callback2(g) == g.syms['CB2_FlyMap'], 'flew to an unvisited town'
    g.tap(K.KEY_B, hold=2, wait=10)
    wait_callback(g, 'CB2_Overworld')
    print('PASS: unvisited Saffron is not selectable', flush=True)

    # The PokeNav is gone from the start menu even with its flag set.
    g.flag('FLAG_SYS_POKENAV_GET', True)
    g.frame(30)
    g.tap(K.KEY_START, hold=2, wait=40)
    actions = [g.u8(g.syms['sCurrentStartMenuActions'] + i) for i in range(g.u8(g.syms['sNumStartMenuActions']))]
    g.shot('start_menu_no_pokenav.png')
    g.tap(K.KEY_B, hold=2, wait=30)
    assert 3 not in actions, actions  # MENU_ACTION_POKENAV
    print('PASS: start menu has no PokeNav', actions, flush=True)


if __name__ == '__main__':
    main()
    region_map_tests()
