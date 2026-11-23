#!/usr/bin/env python3
"""Route 110's building doors: New Mauville (warp 4) and the Trick House (warp 5).

    plastic_ox/bin/pox-mgba-python plastic_ox/demo/test_route110_doors.py
"""
from test_regi_caves import game, hold, wait_map, pos
from test_sudowoodo_v1 import K

DOORS = [
    # (door tile on Route 110, interior map, interior arrival)
    ((35, 24), 'NewMauville_Entrance', (4, 6)),
    ((11, 66), 'Route110_TrickHouseEntrance', None),
]


def main():
    g = game()
    for (x, y), inside, arrival in DOORS:
        g.warp('Route110', x, y + 1)
        g.frame(60)
        hold(g, K.KEY_UP, 30)
        assert wait_map(g, inside), (inside, g.describe())
        if arrival:
            assert pos(g) == arrival, (inside, pos(g))
        hold(g, K.KEY_DOWN, 30)
        assert wait_map(g, 'Route110'), (inside, g.describe())
        assert pos(g) == (x, y + 1), (inside, pos(g))
        print(f'PASS: Route 110 {(x, y)} <-> {inside}', flush=True)
    print('Route 110 doors: PASS', flush=True)


if __name__ == '__main__':
    main()
