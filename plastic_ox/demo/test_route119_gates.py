#!/usr/bin/env python3
"""Route 119's two ends, walked with the D-pad in a fresh ROM.

North: Route 119 <-> Fortree City is a native camera connection. Every lane
(y=6..10) crosses both ways keeping its row (an old portal landed everyone on
(0,9) after a fade), and before FLAG_POX_STORY_WEATHER the edge triggers refuse
and step the player back west without leaving the map.

South: the gatehouse door at (17,137) enters the Ecruteak east gate on its east
mat facing west; walking east from that mat exits through the door onto
(17,138) facing south; walking west through the gate reaches Ecruteak's east
door, and walking back east through the gate returns to Route 119.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_story import StoryGame
from test_burned_tower import at, shot
from test_sudowoodo_v1 import drain
from walklib import K

SOUTH, NORTH, WEST, EAST = 1, 2, 3, 4


def facing(g):
    oid = g.u8(g.syms['gPlayerAvatar'] + 5)
    return g.u8(g.syms['gObjectEvents'] + oid * 0x24 + 0x18) & 0xF


def pos(g):
    s = g.state()
    return s['x'], s['y']


def walk_until(g, key, name, limit=12):
    for _ in range(limit):
        g.hold(key, 16)
        if at(g, name):
            g.frame(120)
            return
    raise AssertionError(('never reached', name, g.describe()))


def main():
    g = StoryGame()
    for f in ('FLAG_POX_STORY_STARTER', 'FLAG_ADVENTURE_STARTED',
              'FLAG_POX_TRIGGERS_ENABLED', 'FLAG_BADGE03_GET'):
        g.flag(f, True)

    # Closed crossing: refusal and a step back, no transition.
    g.flag('FLAG_POX_STORY_WEATHER', False)
    for y in (6, 8, 10):
        g.warp('Route119', 37, y); g.frame(60)
        g.hold(K.KEY_RIGHT, 40)
        for _ in range(20):
            g.hold(K.KEY_B, 4); g.frame(20)
        drain(g); g.frame(60)
        assert at(g, 'Route119') and pos(g)[0] <= 38, (y, g.describe())
    print('ok  closed Fortree crossing refuses and steps back', flush=True)

    # Open crossing: seamless both ways on every lane, row preserved.
    g.flag('FLAG_POX_STORY_WEATHER', True)
    for y in range(6, 11):
        g.warp('Route119', 36, y); g.frame(60)
        walk_until(g, K.KEY_RIGHT, 'FortreeCity')
        assert pos(g)[1] == y and pos(g)[0] <= 2, (y, g.describe())
        if y == 8:
            shot(g, 'route119_fortree_seam.png')
        walk_until(g, K.KEY_LEFT, 'Route119')
        assert pos(g)[1] == y and pos(g)[0] >= 37, (y, g.describe())
    print('ok  Route 119 <-> Fortree seam, all five lanes, both ways', flush=True)

    # South gatehouse door -> Ecruteak east gate.
    # Setup warps carry s8 coordinates, so start inside the gate (y>127 on
    # Route 119 is unreachable by a debug warp) and walk out first.
    g.warp('Gate_EcruteakCity_Route42_hns', 10, 5); g.frame(60)
    walk_until(g, K.KEY_RIGHT, 'Route119')
    g.frame(240)
    shot(g, 'route119_door_arrival.png')
    print('arrival', g.describe(), 'facing', facing(g), 'behavior', g.behavior_at(17, 137), flush=True)
    assert pos(g) == (17, 138), g.describe()
    g.hold(K.KEY_RIGHT, 48); g.hold(K.KEY_UP, 64); g.frame(20)   # into the side lane
    assert pos(g) == (20, 134), g.describe()
    g.hold(K.KEY_DOWN, 64); g.hold(K.KEY_LEFT, 48); g.frame(20)
    assert pos(g) == (17, 138), g.describe()
    shot(g, 'route119_gatehouse.png')
    walk_until(g, K.KEY_UP, 'Gate_EcruteakCity_Route42_hns')
    assert pos(g) == (11, 5) and facing(g) == WEST, (g.describe(), facing(g))
    print('ok  gatehouse door enters the east gate on its mat facing west', flush=True)

    walk_until(g, K.KEY_RIGHT, 'Route119')
    g.frame(120)
    assert pos(g) == (17, 138) and facing(g) == SOUTH, (g.describe(), facing(g))
    print('ok  east gate exits through the Route 119 door, facing south', flush=True)

    walk_until(g, K.KEY_UP, 'Gate_EcruteakCity_Route42_hns')
    walk_until(g, K.KEY_LEFT, 'EcruteakCity_hns', limit=20)
    city = pos(g)
    assert city[1] == 42 and 53 <= city[0] <= 56, g.describe()
    print('ok  walking west through the gate reaches Ecruteak', city, flush=True)
    walk_until(g, K.KEY_RIGHT, 'Gate_EcruteakCity_Route42_hns')
    assert pos(g) == (1, 5) and facing(g) == EAST, (g.describe(), facing(g))
    walk_until(g, K.KEY_RIGHT, 'Route119', limit=20)
    g.frame(120)
    assert pos(g) == (17, 138), g.describe()
    print('ok  Ecruteak -> gate -> Route 119 round trip', flush=True)


if __name__ == '__main__':
    main()
