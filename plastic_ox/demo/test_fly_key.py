#!/usr/bin/env python3
"""Fly Key: picked up in the Route 119 Wingull house, then used from the field."""
import json
import re
import sys

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


# --- region map -----------------------------------------------------------------
# The layout (cells, flags, landing tiles) comes from the generator, so these
# tests follow it when the map is rearranged.
sys.path.insert(0, str(ROOT/'plastic_ox/town_map'))
import build_fly_map as fly_map  # noqa: E402

TOWNS = {t[0]: t for t in fly_map.TOWNS}
GRID = fly_map.build()[3]
MAP_NAMES = {}
for _p in (ROOT/'data/maps').glob('*/map.json'):
    _j = json.loads(_p.read_text())
    MAP_NAMES[_j['id']] = _j['name']
TOWN_MAP = int(re.search(r'ITEM_TOWN_MAP = (\d+)', (ROOT/'include/constants/items.h').read_text())[1])


def cursor(g):
    """Region-map cursor as a grid cell (struct RegionMap.cursorPosX/Y)."""
    rm = g.u32(g.syms['sRegionMap'])
    return g.u16(rm + 0x54) - fly_map.CURSOR_X0, g.u16(rm + 0x56) - fly_map.CURSOR_Y0


def move_cursor(g, cell):
    for _ in range(80):
        x, y = cursor(g)
        if (x, y) == tuple(cell):
            return
        if x != cell[0]:
            g.tap(K.KEY_RIGHT if cell[0] > x else K.KEY_LEFT, hold=2, wait=24)
        else:
            g.tap(K.KEY_DOWN if cell[1] > y else K.KEY_UP, hold=2, wait=24)
    raise AssertionError(f'cursor never reached {cell}: at {cursor(g)}')


def script(g, code):
    """Run a few script bytes (same trick as StoryGame.warp)."""
    ptr = g.syms['gStringVar4']
    for i, b in enumerate(bytes(code) + bytes([2])):
        g.write(ptr + i, b)
    g.run(ptr)


def register(g, item=FLY_KEY):
    g.write(int(g.state()['ptr'], 16)+0x496, item, 2)


def open_map(g, callback='CB2_FlyMap'):
    g.tap(K.KEY_SELECT, hold=2, wait=10)
    if callback != 'CB2_FlyMap':
        # The Town Map opens through a script with one message box.
        for _ in range(60):
            if callback2(g) == g.syms[callback]:
                break
            g.tap(K.KEY_A, hold=2, wait=10)
    wait_callback(g, callback)
    g.frame(60)


def visit(g, mapsec):
    _, _, _, flag, mp, x, y, _ = TOWNS[mapsec]
    g.warp(MAP_NAMES[mp], x, y)
    assert g.flag(flag), f'{flag} not set on entering {mp}'


def assert_landed(g, mapsec):
    _, _, _, _, mp, x, y, _ = TOWNS[mapsec]
    st = g.state()
    assert (st['group'], st['num']) == map_id(g, MAP_NAMES[mp]) and (st['x'], st['y']) == (x, y), (mapsec, g.describe())


def fly_to(g, mapsec, label=None):
    open_map(g)
    move_cursor(g, TOWNS[mapsec][1])
    if label:
        g.shot(f'fly_map_{label}.png')
    g.tap(K.KEY_A, hold=2, wait=10)
    wait_callback(g, 'CB2_Overworld', 1800)
    g.frame(400)
    assert_landed(g, mapsec)


def pick_up_fly_key(g):
    g.warp('Route119_House', BALL[0], BALL[1]+1)
    g.tap(K.KEY_UP, hold=2, wait=20)
    g.tap(K.KEY_A, hold=2, wait=20)
    finish(g)
    assert FLY_KEY in key_items(g)


def clear_visited(g):
    for t in fly_map.TOWNS:
        g.flag(t[3], False)


def region_map_tests():
    g = StoryGame()
    g.run('Pox_Treecko')
    pick_up_fly_key(g)
    register(g)
    clear_visited(g)

    # Entering a town sets its visited flag; only those towns can be chosen.
    for mapsec in ['MAPSEC_GOLDENROD_CITY', 'MAPSEC_ECRUTEAK_CITY', 'MAPSEC_FORTREE_CITY']:
        assert not g.flag(TOWNS[mapsec][3]), mapsec
        visit(g, mapsec)
    print('PASS: entering towns marks them as fly destinations', flush=True)
    fly_to(g, 'MAPSEC_ECRUTEAK_CITY', 'ecruteak')
    print('PASS: flew Fortree -> Ecruteak by cursor', flush=True)
    open_map(g)
    move_cursor(g, TOWNS['MAPSEC_SAFFRON_CITY'][1])
    g.tap(K.KEY_A, hold=2, wait=60)
    assert callback2(g) == g.syms['CB2_FlyMap'], 'flew to an unvisited town'
    g.tap(K.KEY_B, hold=2, wait=10)
    wait_callback(g, 'CB2_Overworld')
    g.frame(60)
    print('PASS: unvisited Saffron is not selectable', flush=True)

    # Every destination: visit it once, then fly there from the previous one.
    for t in fly_map.TOWNS:
        visit(g, t[0])
    for i, t in enumerate(fly_map.TOWNS):
        fly_to(g, t[0], 'all' if i == 0 else None)
    print(f'PASS: flew to all {len(fly_map.TOWNS)} destinations', flush=True)

    # The map opens with the cursor on the player's own map section, also on
    # routes that bend (their bounding box holds other sections' cells).
    for name, mapsec in [('Route29_hns', 'MAPSEC_ROUTE_29'), ('Route33_hns', 'MAPSEC_ROUTE_33'),
                         ('Route36_hns', 'MAPSEC_ROUTE_36'), ('Route110', 'MAPSEC_ROUTE_110'),
                         ('Route101', 'MAPSEC_ROUTE_101')]:
        for x, y in [(3, 3), (20, 12)]:
            g.warp(name, x, y)
            open_map(g)
            cx, cy = cursor(g)
            assert GRID[cy][cx] == mapsec, (name, (x, y), (cx, cy), GRID[cy][cx])
            g.tap(K.KEY_B, hold=2, wait=10)
            wait_callback(g, 'CB2_Overworld')
            g.frame(60)
    print('PASS: fly map opens on the player\'s route', flush=True)

    # Town Map + Fly Key: A on a visited town flies there.
    script(g, bytes([0x44]) + TOWN_MAP.to_bytes(2, 'little') + (1).to_bytes(2, 'little'))
    assert TOWN_MAP in key_items(g), key_items(g)
    visit(g, 'MAPSEC_LAVENDER_TOWN')
    register(g, TOWN_MAP)
    open_map(g, 'MCB2_FieldUpdateRegionMap')
    g.shot('town_map_fly.png')
    move_cursor(g, TOWNS['MAPSEC_GOLDENROD_CITY'][1])
    g.tap(K.KEY_A, hold=2, wait=10)
    wait_callback(g, 'CB2_Overworld', 1800)
    g.frame(400)
    assert_landed(g, 'MAPSEC_GOLDENROD_CITY')
    before = (g.state()['x'], g.state()['y'])
    for key in (K.KEY_DOWN, K.KEY_LEFT, K.KEY_RIGHT, K.KEY_UP):
        g.tap(key, hold=20, wait=10)
        if (g.state()['x'], g.state()['y']) != before:
            break
    assert (g.state()['x'], g.state()['y']) != before, 'controls locked after Town Map flight'
    print('PASS: Town Map flies with the Fly Key and frees the player', flush=True)
    # On a route (not a destination) A still just closes the Town Map.
    visit(g, 'MAPSEC_LAVENDER_TOWN')
    open_map(g, 'MCB2_FieldUpdateRegionMap')
    move_cursor(g, (TOWNS['MAPSEC_LAVENDER_TOWN'][1][0], TOWNS['MAPSEC_LAVENDER_TOWN'][1][1] - 1))
    g.tap(K.KEY_A, hold=2, wait=10)
    wait_callback(g, 'CB2_Overworld')
    g.frame(120)
    finish(g)
    assert_landed(g, 'MAPSEC_LAVENDER_TOWN')
    print('PASS: Town Map closes with A off a destination', flush=True)

    # The PokeNav is gone from the start menu even with its flag set.
    g.flag('FLAG_SYS_POKENAV_GET', True)
    g.frame(30)
    g.tap(K.KEY_START, hold=2, wait=40)
    actions = [g.u8(g.syms['sCurrentStartMenuActions'] + i) for i in range(g.u8(g.syms['sNumStartMenuActions']))]
    g.shot('start_menu_no_pokenav.png')
    g.tap(K.KEY_B, hold=2, wait=30)
    assert 3 not in actions, actions  # MENU_ACTION_POKENAV
    print('PASS: start menu has no PokeNav', actions, flush=True)


def town_map_without_key_test():
    """Without the Fly Key the Town Map is only a map."""
    g = StoryGame()
    g.run('Pox_Treecko')
    assert FLY_KEY not in key_items(g)
    script(g, bytes([0x44]) + TOWN_MAP.to_bytes(2, 'little') + (1).to_bytes(2, 'little'))
    visit(g, 'MAPSEC_GOLDENROD_CITY')
    visit(g, 'MAPSEC_LAVENDER_TOWN')
    register(g, TOWN_MAP)
    open_map(g, 'MCB2_FieldUpdateRegionMap')
    move_cursor(g, TOWNS['MAPSEC_GOLDENROD_CITY'][1])
    g.tap(K.KEY_A, hold=2, wait=10)
    wait_callback(g, 'CB2_Overworld')
    g.frame(120)
    finish(g)
    assert_landed(g, 'MAPSEC_LAVENDER_TOWN')
    print('PASS: Town Map does not fly without the Fly Key', flush=True)


def old_save_test():
    """A save from before the fly map gets its visited towns back on Continue."""
    g = StoryGame()
    g.run('Pox_Treecko')
    g.warp('LavenderTown_hns', 9, 7)
    clear_visited(g)
    g.flag('FLAG_BADGE03_GET', True)                       # Morty: Ecruteak
    script(g, bytes([0x16]) + (0x40FC).to_bytes(2, 'little') + (1).to_bytes(2, 'little'))  # VAR_POX_SAVE_MIGRATION_VERSION = 1
    main_ = g.syms['gMain']
    g.write(main_ + 4, g.syms['CB2_ContinueSavedGame'] | 1, 4)
    g.write(main_ + 0x438, 0)
    g.frame(30)
    wait_callback(g, 'CB2_Overworld', 1800)
    g.frame(120)
    order = [t[0] for t in fly_map.TOWNS]
    reached = order.index('MAPSEC_LAVENDER_TOWN')          # standing in Lavender
    got = [m for m in order if g.flag(TOWNS[m][3])]
    assert got == order[:reached + 1], got
    print('PASS: old save backfills visited towns up to the furthest one reached:', len(got), flush=True)


if __name__ == '__main__':
    main()
    region_map_tests()
    town_map_without_key_test()
    old_save_test()
