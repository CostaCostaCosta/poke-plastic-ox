#!/usr/bin/env python3
"""Fly Key: picked up in the Route 119 Wingull house, then used from the field."""
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


if __name__ == '__main__':
    main()
