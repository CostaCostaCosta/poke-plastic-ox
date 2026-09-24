#!/usr/bin/env python3
"""Exercise every lane of the mixed-tileset Rustboro / Route 24 seam."""
import json
import sys

from test_story import StoryGame, ROOT
from test_camera_seam import check_view
from walk_demo import cross_connection
from walklib import K

sys.path.insert(0, str(ROOT / 'plastic_ox/alpha'))
from region_geometry import Geometry


def check_encounter(g, ids):
    from test_region_walk import navigate, cross

    # The grass bank is reached around the river through Route 25. Walk the
    # entire path after the new seam, so a setup warp cannot mask stale state.
    g.test_water = False
    g.warp('RustboroCity', 21, 0)
    cross_connection(g, 'UP', ids['Route24_hns'], 'rustboro_encounter_entry')
    navigate(g, lambda x, y: y == 0 and 16 <= x <= 19)
    cross(g, 'N', 'Route25_hns')
    navigate(g, lambda x, y: (x, y) == (8, 34))
    cross(g, 'S', 'Route24_hns')
    navigate(g, lambda x, y: (x, y) == (8, 2))
    assert g.behavior_at(8, 2)[0] == g.behavior_at(9, 2)[0] == 2
    g.write(g.syms['sWildEncountersDisabled'], 0)
    for step in range(300):
        g.tap(K.KEY_RIGHT if step % 2 == 0 else K.KEY_LEFT, hold=10, wait=20)
        if g.u32(g.syms['gBattleTypeFlags']):
            break
    else:
        raise AssertionError('No Route 24 grass encounter')
    g.frame(120)
    species = g.box_species(g.syms['gParties'] + g.sizes['gParties'] // 4)
    allowed = set()
    for time in ('Morning', 'Day', 'Night'):
        symbol = f'gPoxRoute24Hns_{time}_LandMons'
        stride = g.sizes[symbol] // 12
        allowed.update(g.u16(g.syms[symbol] + i * stride + 2) for i in range(12))
    assert species in allowed, (species, allowed)
    g.shot('rustboro_north_encounter.png')
    print(f'PASS: Route 24 encounter species {species} after continuous bridge/bank walk')


def main():
    groups = json.loads((ROOT / 'data/maps/map_groups.json').read_text())
    ids = {n: (i, j) for i, key in enumerate(groups['group_order'])
           for j, n in enumerate(groups[key])}
    city, route = Geometry('RustboroCity'), Geometry('Route24_hns')
    assert [x for x in range(city.w) if city.passable(x, 0)] == list(range(19, 23))
    assert [x for x in range(route.w) if route.passable(x, 21)] == list(range(16, 20))
    for x in range(19, 23):
        assert city.tile(x, 0)[1] == route.tile(x - 3, 21)[1] == 3
        assert (x, 0) in city.component((27, 20))
        assert (x - 3, 21) in route.component((18, 10))
    g = StoryGame()
    for x in range(19, 23):
        g.warp('RustboroCity', x, 1)
        g.walk('UP', target=(x, 0))
        cross_connection(g, 'UP', ids['Route24_hns'], f'rustboro_north_{x}')
        assert (g.state()['x'], g.state()['y']) == (x - 3, 21), g.state()
        assert g.collision_at(g.state()['x'], g.state()['y'])[0] == 0
        check_view(g, f'rustboro_north_route_lane_{x}')
        g.walk('DOWN', target=(x - 3, 21))
        cross_connection(g, 'DOWN', ids['RustboroCity'], f'rustboro_south_{x}')
        assert (g.state()['x'], g.state()['y']) == (x, 0), g.state()
        check_view(g, f'rustboro_north_city_lane_{x}')
    # The separate riverside path must not become a crossing into city trees.
    for x in range(24, 27):
        g.warp('Route24_hns', x, 20)
        g.tap(K.KEY_DOWN, hold=24, wait=30)
        state = g.state()
        assert (state['group'], state['num'], state['x'], state['y']) == (*ids['Route24_hns'], x, 20), state
    g.warp('RustboroCity', 21, 5)
    g.frame(180)
    g.shot('rustboro_north_city.png')
    g.warp('Route24_hns', 18, 19)
    g.frame(180)
    g.shot('rustboro_north_bridge.png')
    print('PASS: four lanes round trip, redraws, no white frames, blocked side path')
    check_encounter(g, ids)


if __name__ == '__main__':
    main()
