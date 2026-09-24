#!/usr/bin/env python3
"""Exercise every lane and shoulder of the Route 2 / Cherrygrove seam."""
import json
import sys

from test_story import StoryGame, ROOT
from test_camera_seam import check_view
from walk_demo import cross_connection
from walklib import K

sys.path.insert(0, str(ROOT / 'plastic_ox/alpha'))
from region_geometry import Geometry


def main():
    groups = json.loads((ROOT / 'data/maps/map_groups.json').read_text())
    ids = {n: (i, j) for i, key in enumerate(groups['group_order'])
           for j, n in enumerate(groups[key])}
    route = Geometry('Route2_Frlg')
    city = Geometry('CherrygroveCity_hns')
    assert [x for x in range(route.w) if route.passable(x, route.h - 1)] == [8, 9, 10]
    assert [x for x in range(city.w) if city.passable(x, 0)] == [33, 34, 35]
    for x in range(8, 11):
        assert route.tile(x, 79)[1] == city.tile(x + 25, 0)[1]

    g = StoryGame()
    for x in range(8, 11):
        g.warp('Route2_Frlg', x, 78)
        g.walk('DOWN', target=(x, 79))
        cross_connection(g, 'DOWN', ids['CherrygroveCity_hns'], f'route2_south_{x}')
        assert (g.state()['x'], g.state()['y']) == (x + 25, 0), g.state()
        assert g.collision_at(x + 25, 0)[0] == 0
        check_view(g, f'cherrygrove_north_lane_{x + 25}')
        g.walk('UP', target=(x + 25, 0))
        cross_connection(g, 'UP', ids['Route2_Frlg'], f'cherrygrove_north_{x + 25}')
        assert (g.state()['x'], g.state()['y']) == (x, 79), g.state()
        check_view(g, f'route2_south_lane_{x}')

    # The old shoulder lanes must visibly stop before the boundary.
    for x in (7, 11):
        g.warp('Route2_Frlg', x, 78)
        g.tap(K.KEY_DOWN, hold=24, wait=30)
        state = g.state()
        assert (state['group'], state['num'], state['x'], state['y']) == \
               (*ids['Route2_Frlg'], x, 78), state
    print('PASS: three lanes round trip; old tree landings are blocked; redraws stable')


if __name__ == '__main__':
    main()
