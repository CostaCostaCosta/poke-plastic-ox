#!/usr/bin/env python3
"""Walk Hoenn Route 101, both connections, its ledge, and encounter grass."""

from test_story import StoryGame
from walk_demo import (
    MAP_OLDALE, MAP_PALLET, MAP_ROUTE101,
    cross_connection, exercise_route101_ledge, walk_to_edge,
)
from walklib import K


def check_round_trip():
    g = StoryGame()
    g.flag('FLAG_POX_STORY_STARTER', True)
    g.warp('Route101', 10, 19)
    assert g.metatile_at(6, 7)[0] == 0x08E
    assert g.behavior_at(6, 7)[0] == 0x3E
    g.shot('route101_hoenn_south.png')
    exercise_route101_ledge(g)
    walk_to_edge(g, 'north')
    cross_connection(g, 'UP', MAP_OLDALE, 'route101_to_oldale')
    g.shot('route101_hoenn_oldale.png')
    walk_to_edge(g, 'south')
    cross_connection(g, 'DOWN', MAP_ROUTE101, 'oldale_to_route101')
    walk_to_edge(g, 'south')
    cross_connection(g, 'DOWN', MAP_PALLET, 'route101_to_pallet')
    g.shot('route101_hoenn_pallet.png')
    print('ROUND TRIP AND LEDGE PASS', flush=True)


def check_grass_encounter():
    g = StoryGame()
    g.run('Pox_Squirtle')
    g.warp('Route101', 11, 10)
    assert g.behavior_at(11, 10)[0] == g.behavior_at(12, 10)[0] == 2
    g.write(g.syms['sWildEncountersDisabled'], 0)
    for step in range(300):
        g.tap(K.KEY_RIGHT if step % 2 == 0 else K.KEY_LEFT, hold=10, wait=20)
        if g.u32(g.syms['gBattleTypeFlags']):
            break
    else:
        raise AssertionError('no Route 101 grass encounter')

    g.frame(120)
    species = g.box_species(g.syms['gParties'] + g.sizes['gParties'] // 4)
    symbol = 'gPoxRoute101_LandMons'
    stride = g.sizes[symbol] // 7
    allowed = {g.u16(g.syms[symbol] + i * stride + 2) for i in range(7)}
    assert species in allowed, (species, allowed)
    g.shot('route101_hoenn_encounter.png')
    print(f'GRASS ENCOUNTER PASS after {step + 1} steps: species {species}', flush=True)


if __name__ == '__main__':
    check_round_trip()
    check_grass_encounter()
