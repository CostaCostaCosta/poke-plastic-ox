#!/usr/bin/env python3
"""Route 2 trade house: walking into the room must not throw the player out.

The HNS interior once had a second warp on (4, 7), the floor tile just above
the exit mat, so the first step into the room sent the player back to Route 2.
This walks in through the Route 2 door, roams the room (including (4, 7)),
then leaves through the mat at (4, 8) and comes back in again.
"""
import json
import sys

from test_story import StoryGame, ROOT
from walklib import K
from walk_leg1 import navigate, enter_warp


def main():
    house = json.loads((ROOT / 'data/maps/Route2_House_Frlg/map.json').read_text())
    warps = [(w['x'], w['y'], w['dest_map']) for w in house['warp_events']]
    assert warps == [(4, 8, 'MAP_ROUTE2')], warps
    print('ok  static: one interior warp, on the exit mat')

    groups = json.loads((ROOT / 'data/maps/map_groups.json').read_text())
    ids = {n: (i, j) for i, key in enumerate(groups['group_order'])
           for j, n in enumerate(groups[key])}
    ROUTE, HOUSE = ids['Route2_Frlg'], ids['Route2_House_Frlg']

    def where(g):
        s = g.state()
        return (s['group'], s['num']), (s['x'], s['y'])

    g = StoryGame(spawn=('Route2_Frlg', 17, 24))
    for lap in range(2):
        enter_warp(g, (17, 23), 'UP', HOUSE, f'enter_house_{lap}')
        m, pos = where(g)
        assert m == HOUSE and pos == (4, 8), (m, pos)
        print(f'ok  lap {lap}: Route 2 door lands on the house mat')

        # Step onto (4, 7), then roam the room: we must stay inside.
        g.tap(K.KEY_UP, hold=8, wait=30)
        for _ in range(60):
            g.frame(1)
        m, pos = where(g)
        assert m == HOUSE and pos == (4, 7), f'first step forward left the house: {m} {pos}'
        for target in ((2, 7), (9, 7), (9, 3), (4, 7)):
            navigate(g, target)
            m, pos = where(g)
            assert m == HOUSE and pos == target, (target, m, pos)
        print(f'ok  lap {lap}: (4,7) and the room are ordinary floor')

        enter_warp(g, (4, 8), 'DOWN', ROUTE, f'exit_house_{lap}')
        for _ in range(90):
            g.frame(1)
        m, pos = where(g)
        assert m == ROUTE and pos in ((17, 22), (17, 23)), (m, pos)
        print(f'ok  lap {lap}: exit mat returns to Route 2 at {pos}')
        if pos == (17, 22):
            g.tap(K.KEY_DOWN, hold=8, wait=30)
        navigate(g, (17, 24))
    print('PASS: Route 2 house enter, roam, exit, re-enter')


if __name__ == '__main__':
    main()
