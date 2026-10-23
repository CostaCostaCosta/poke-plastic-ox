#!/usr/bin/env python3
"""Verify Sudowoodo closes Route 36's three-way junction in the built ROM."""

import json
import sys

from test_story import ROOT, StoryGame
from walk_leg1 import navigate
from walklib import K

sys.path.insert(0, str(ROOT / 'plastic_ox/alpha'))
from region_geometry import Geometry


PARK = (16, 21)
SUDOWOODO = (39, 19)
SNORLAX = (43, 19)
EAST_PORT = (65, 18)


def map_id(name):
    groups = json.loads((ROOT / 'data/maps/map_groups.json').read_text())
    return next((i, groups[group].index(name))
                for i, group in enumerate(groups['group_order'])
                if name in groups[group])


def static_gate():
    geom = Geometry('Route36_hns')
    events = {o['script']: (o['x'], o['y']) for o in geom.data['object_events']}
    assert events['Pox_Sudowoodo'] == SUDOWOODO
    assert events['Route36_EventScript_Snorlax'] == SNORLAX
    assert all(geom.passable(*p) and geom.tile(*p)[1] == 3
               for p in [SUDOWOODO, (39, 18), (40, 19), (39, 20)])
    assert not geom.passable(38, 19)
    assert all(not geom.passable(x, 20) for x in range(40, 45))

    north = {(x, 0) for x in range(geom.w) if geom.passable(x, 0)}
    assert north
    for can_sudo, can_snorlax, north_open, east_open in [
        (False, False, False, False),
        (True, False, True, False),
        (True, True, True, True),
    ]:
        blocked = set()
        if not can_sudo:
            blocked.add(SUDOWOODO)
        if not can_snorlax:
            blocked.add(SNORLAX)
        for water in (False, True):
            reachable = geom.component(PARK, blocked=blocked, water=water)
            assert bool(reachable & north) == north_open, (blocked, 'north', water)
            assert (EAST_PORT in reachable) == east_open, (blocked, 'east', water)
            if not can_sudo:
                reverse = geom.component((35, 0), blocked=blocked, water=water)
                assert PARK not in reverse, (blocked, 'reverse bypass', water)
    print('three-way junction: no walking or Surf bypass; north opens after Sudowoodo; east after Snorlax PASS', flush=True)


def runtime_gate():
    cases = [
        ({}, (39, 20), K.KEY_UP, (39, 20), 'sudowoodo_south_blocked'),
        ({}, (39, 18), K.KEY_DOWN, (39, 18), 'sudowoodo_north_blocked'),
        ({'FLAG_POX_SUDOWOODO_CLEARED': True}, (39, 20), K.KEY_UP,
         (39, 19), 'sudowoodo_open'),
        ({'FLAG_POX_SUDOWOODO_CLEARED': True}, (42, 19), K.KEY_RIGHT,
         (42, 19), 'snorlax_blocked'),
        ({'FLAG_POX_SUDOWOODO_CLEARED': True,
          'FLAG_POX_ROUTE36_SNORLAX_CLEARED': True}, (42, 19), K.KEY_RIGHT,
         (43, 19), 'snorlax_open'),
    ]
    for flags, start, key, expected, shot in cases:
        game = StoryGame()
        for flag, value in flags.items():
            game.flag(flag, value)
        game.warp('Route36_hns', *start)
        game.frame(80)
        game.shot(f'route36_{shot}_before.png')
        game.tap(key, hold=18, wait=100)
        assert (game.state()['x'], game.state()['y']) == expected, (shot, game.state())
        game.shot(f'route36_{shot}_after.png')
        print(shot, 'PASS', flush=True)


def seam_round_trip():
    game = StoryGame()
    game.flag('FLAG_POX_SUDOWOODO_CLEARED', True)
    game.warp('Route36_hns', 39, 20)
    navigate(game, (35, 0))
    game.shot('route36_north_approach.png')
    game.hold(K.KEY_UP, 90)
    assert (game.state()['group'], game.state()['num']) == map_id('Route37_hns')
    game.shot('route36_route37_arrival.png')
    game.hold(K.KEY_DOWN, 150)
    assert (game.state()['group'], game.state()['num']) == map_id('Route36_hns')
    navigate(game, (39, 20))
    game.shot('route36_return_through_junction.png')
    print('Route 36 -> Route 37 -> Route 36 and south through cleared junction PASS', flush=True)


if __name__ == '__main__':
    static_gate()
    runtime_gate()
    seam_round_trip()
