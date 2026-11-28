#!/usr/bin/env python3
"""Dark Cave: the South Side lake platform, the door to the North Side, and the
one-way North Side ledges, played in mGBA.

* Surf works off the platform's west side, (33,8) -> (32,8), and back again
  from the lake's west shore.
* The platform door (34,6) leads to DarkCave_NorthSide_hns (6,38) and back.
* The room behind that door is walled off by the west-facing ledges at
  (10,33-36): you can drop into it from the Blackthorn side but never climb
  out, so the early cave has no route to Blackthorn.
* Route 45's cave mouth (14,4) and the North Side's (45,9) are linked both ways.
* The North Side land tables are UU, Lv 33-37.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_warps_v1 import make_playtest
from test_region_walk import current
from test_sudowoodo_v1 import const
from walklib import K

ROOT = Path(__file__).resolve().parents[2]
SOUTH, NORTH, R45 = 'DarkCave_SouthSide_hns', 'DarkCave_NorthSide_hns', 'Route45_hns'


def pos(g):
    s = g.state()
    return s['x'], s['y']


def hold(g, key, frames=24):
    g.core.set_keys(key)
    g.frame(frames)
    g.core.clear_keys(key)
    g.frame(40)


def wait_map(g, name, frames=900):
    for _ in range(frames // 10):
        if current(g) == name:
            g.frame(90)
            return True
        g.frame(10)
    return False


def swim(g, key, frames=900):
    """Hold a direction until the engine puts the player back on land."""
    for _ in range(frames // 20):
        if not g.surfing():
            return True
        hold(g, key, 16)
    return not g.surfing()


def static_checks():
    sys.path.insert(0, str(ROOT / 'plastic_ox/tools'))
    import pox_progression as p
    tiers = p.load_tiers()
    enc = json.loads((ROOT / 'src/data/wild_encounters.json').read_text())['wild_encounter_groups'][0]['encounters']
    tables = [e for e in enc if e.get('map') == 'MAP_DARK_CAVE_NORTH_SIDE_HNS']
    assert len(tables) == 3, tables
    for t in tables:
        for kind in ('land_mons', 'water_mons', 'rock_smash_mons'):
            for m in t[kind]['mons']:
                assert tiers.get(m['species']) == 'UU', (t['base_label'], m)
                assert 33 <= m['min_level'] <= m['max_level'] <= 37, m
    print('  ok  North Side tables are UU, Lv 33-37', flush=True)


def test_platform_surf(g):
    g.warp(SOUTH, 33, 8)
    g.frame(60)
    ok, note = g.mount_surf('LEFT')
    assert ok and g.surfing(), ('no Surf off the platform west side', note, pos(g))
    assert swim(g, K.KEY_LEFT), ('never reached the west shore', pos(g))
    assert pos(g)[0] == 24, pos(g)
    print(f'  ok  surfed west off the platform to the shore at {pos(g)}', flush=True)
    ok, note = g.mount_surf('RIGHT')
    assert ok, ('no Surf from the west shore', note, pos(g))
    assert swim(g, K.KEY_RIGHT), ('never reached the platform', pos(g))
    assert pos(g)[0] == 33 and 7 <= pos(g)[1] <= 10, pos(g)
    print(f'  ok  surfed back east onto the platform at {pos(g)}', flush=True)
    # Up to the door.
    while pos(g)[1] > 7:
        hold(g, K.KEY_UP, 16)
    while pos(g)[0] < 34:
        hold(g, K.KEY_RIGHT, 16)
    hold(g, K.KEY_UP, 24)
    assert wait_map(g, NORTH), ('platform door did not warp', current(g), pos(g))
    print(f'  ok  platform door -> North Side at {pos(g)}', flush=True)


def test_one_way(g):
    # Below the ledges: holding right from the room never gets past x=9.
    g.warp(NORTH, 9, 35)
    g.frame(60)
    for _ in range(4):
        hold(g, K.KEY_RIGHT, 16)
    assert current(g) == NORTH and pos(g) == (9, 35), ('climbed the ledge', pos(g))
    # Above them: walking left jumps down two tiles.
    g.warp(NORTH, 11, 35)
    g.frame(60)
    hold(g, K.KEY_LEFT, 16)
    g.frame(60)
    assert pos(g) == (9, 35), ('ledge did not drop west', pos(g))
    print('  ok  (10,33-36) ledges: drop west only, no climb back toward Blackthorn', flush=True)
    # Back out through the south door to the platform.
    g.warp(NORTH, 6, 37)
    g.frame(60)
    for _ in range(3):
        if current(g) == SOUTH:
            break
        hold(g, K.KEY_DOWN, 24)
    assert wait_map(g, SOUTH), ('south door did not warp', current(g), pos(g))
    assert pos(g) in ((34, 6), (34, 7)), pos(g)
    print(f'  ok  North Side south door -> platform at {pos(g)}', flush=True)


def test_route45(g):
    g.warp(R45, 14, 5)
    g.frame(60)
    hold(g, K.KEY_UP, 24)
    assert wait_map(g, NORTH), ('Route 45 mouth did not warp', current(g), pos(g))
    assert pos(g) == (45, 9), pos(g)
    hold(g, K.KEY_DOWN, 24)
    assert wait_map(g, R45), ('North Side mouth did not warp', current(g), pos(g))
    assert pos(g) in ((14, 4), (14, 5)), pos(g)
    print(f'  ok  Route 45 (14,4) <-> North Side (45,9)', flush=True)


def main():
    static_checks()
    g = make_playtest()
    g.unlock()
    test_platform_surf(g)
    test_one_way(g)
    test_route45(g)
    print('PASS: Dark Cave', flush=True)


if __name__ == '__main__':
    main()
