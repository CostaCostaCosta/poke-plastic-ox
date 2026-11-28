#!/usr/bin/env python3
"""Saffron's north road: Saffron -> Route 34 -> Route 115 -> Meteor Falls -> Blackthorn.

Route 34 replaced the empty Route 5 (region_v7.py TRAILS saffron_route34 and
route34_route115). This walks the whole road with ordinary D-pad movement, plus
Surf on Route 115 as a player would. It also checks that the Saffron north gate
stays shut before the Space Center, and that Route 116's old door into Route 34
is gone.

Run:  plastic_ox/bin/pox-mgba-python plastic_ox/demo/test_route34_late_game.py
"""
import test_region_walk as W
from walklib import K


def port(g, key):
    p = W.PORTS[key]
    assert W.current(g) == p['source'], (W.current(g), key)
    W.navigate(g, lambda x, y: (x, y) == tuple(p['approach']))
    W.cross(g, p['direction'], p['destination'])
    print('PASS crossed', key, '->', W.current(g), flush=True)


def closed_gate():
    g = W.setup(('SaffronCity_hns', 29, 6))
    g.flag('FLAG_POX_STORY_SPACE_CENTER', False)
    g.warp('SaffronCity_hns', 29, 6)
    g.frame(60)
    for _ in range(3):
        g.tap(K.KEY_RIGHT, hold=24, wait=60)
        for _ in range(20):
            g.tap(K.KEY_A, hold=2, wait=10)
    g.frame(240)
    assert W.current(g) == 'SaffronCity_hns', ('north gate opened early', W.current(g))
    print('PASS north gate closed before the Space Center', flush=True)


def no_route116_door():
    d = W.MAPS['Route116']
    assert not any(c['map'] == 'MAP_ROUTE34_HNS' for c in d['connections'])
    assert not any(w['dest_map'] == 'MAP_ROUTE34_HNS' for w in d['warp_events'])
    print('PASS Route 116 has no door into Route 34', flush=True)


def walk():
    g = W.setup(('SaffronCity_hns', 16, 23))
    g.test_water = True
    g.warp('SaffronCity_hns', 16, 23)
    g.frame(60)
    port(g, 'saffron_route34_a')
    port(g, 'route34_route115_a')
    w = W.MAPS['Route115']['warp_events'][0]          # Meteor Falls mouth
    W.navigate(g, lambda x, y: abs(x - w['x']) + abs(y - w['y']) == 1)
    for key in (K.KEY_UP, K.KEY_RIGHT, K.KEY_LEFT, K.KEY_DOWN):
        if W.current(g) != 'Route115':
            break
        g.tap(key, hold=24, wait=200)
    assert W.current(g) == 'MeteorFalls_1F_1R', W.current(g)
    print('PASS entered Meteor Falls', flush=True)
    port(g, 'meteor_blackthorn_a')
    assert W.current(g) == 'BlackthornCity_hns'


if __name__ == '__main__':
    no_route116_door()
    closed_gate()
    walk()
    print('PASS Saffron -> Route 34 -> Route 115 -> Meteor Falls -> Blackthorn')
