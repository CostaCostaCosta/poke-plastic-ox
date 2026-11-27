#!/usr/bin/env python3
"""Houses on LAYOUT_HOUSE_GENERIC_A_HNS: enter from the street, walk in, leave.

The layout's exit is the south-arrow carpet at (4,8). A warp event at (4,9)
sits on plain floor and traps the player inside.
"""
import sys
from test_league import prepare, current, K

HOUSES = [
    ('CherrygroveCity_hns', (34, 14), 'CherrygroveCity_SoutheastHouse_hns'),
    ('CherrygroveCity_hns', (50, 18), 'House_GenericA_hns'),
]


def main():
    for town, door, house in HOUSES:
        g = prepare((town,) + door)
        g.tap(K.KEY_UP, hold=16, wait=240)
        assert current(g) == house, (house, 'enter', g.describe())
        for _ in range(2):
            g.tap(K.KEY_UP, hold=16, wait=30)
        assert g.state()['y'] < 8, (house, 'walk in', g.describe())
        for _ in range(4):
            g.tap(K.KEY_DOWN, hold=16, wait=200)
            if current(g) == town:
                break
        assert current(g) == town and (g.state()['x'], g.state()['y']) == door, (house, 'exit', g.describe())
        print(f'PASS: {house} enter, walk, exit to {town} {door[0]},{door[1]}', flush=True)


if __name__ == '__main__':
    sys.exit(main())
