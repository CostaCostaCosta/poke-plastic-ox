#!/usr/bin/env python3
"""Routes 8, 7 and 21 roll their UU-capped gPoxUU tables in mGBA.

The Lavender -> Cinnabar leg (Route 8, Route 7, Route 21 North) sits at the
cinnabar checkpoint of plastic_ox/tools/pox_progression.py (tier UU, level
cap 42). For each live map this harness steps back and forth in tall grass
until a wild battle starts, then checks the wild POKeMON is one of the map's
gPoxUU land slots and that its level is inside that slot band. The field
warp only places the player; the encounter is the thing under test.
"""
from test_region_walk import current, navigate, KEYS, DELTAS, BEHAVIORS
from test_story import StoryGame

CASES = [
    # (map dir, spawn tile, table symbol)
    ('Route8_Frlg', (60, 20), 'gPoxUURoute8_LandMons'),
    # Route 7's grass is the patch at (11..18, 4..8); spawn inside it.
    ('Route7_hns', (13, 6), 'gPoxUURoute7Hns_LandMons'),
    ('Route21_North_Frlg', None, 'gPoxUURoute21North_LandMons'),
]


def first_walkable(g):
    for y in range(1, 60):
        for x in range(1, 40):
            if g.collision_at(x, y)[0] == 0 and BEHAVIORS[g.behavior_at(x, y)[0]] == 'MB_TALL_GRASS':
                return x, y
    raise AssertionError('no grass tile found')


def main():
    for name, spawn, symbol in CASES:
        g = StoryGame()
        g.flag('FLAG_POX_TRIGGERS_ENABLED', True)
        g.test_water = False
        if spawn is None:
            g.warp(name, 10, 10)
            g.frame(60)
            spawn = first_walkable(g)
        g.warp(name, *spawn)
        g.frame(90)
        assert current(g) == name, (name, current(g))

        def grass(x, y):
            return g.collision_at(x, y)[0] == 0 and BEHAVIORS[g.behavior_at(x, y)[0]] == 'MB_TALL_GRASS'

        def pair(x, y):
            return grass(x, y) and any(grass(x + dx, y + dy) for dx, dy in DELTAS.values())
        navigate(g, pair)
        s = g.state()
        start = s['x'], s['y']
        direction = next(k for k, (dx, dy) in DELTAS.items() if grass(start[0] + dx, start[1] + dy))
        reverse = dict(N='S', S='N', E='W', W='E')[direction]
        g.write(g.syms['sWildEncountersDisabled'], 0)
        for step in range(400):
            g.tap(KEYS[direction if step % 2 == 0 else reverse], hold=10, wait=20)
            if g.u32(g.syms['gBattleTypeFlags']):
                break
            assert current(g) == name
        else:
            raise AssertionError((name, 'no grass encounter'))
        g.frame(120)
        mon = g.syms['gParties'] + g.sizes['gParties'] // 4   # enemy party
        species = g.box_species(mon)
        level = g.u8(mon + 0x54)
        stride = g.sizes[symbol] // 12
        slots = [(g.u8(g.syms[symbol] + i * stride), g.u8(g.syms[symbol] + i * stride + 1),
                  g.u16(g.syms[symbol] + i * stride + 2)) for i in range(12)]
        assert any(sp == species and lo <= level <= hi for lo, hi, sp in slots), (name, species, level, slots)
        assert all(hi <= 42 for _lo, hi, _sp in slots), (name, slots)
        print(f'PASS {name}: encounter after {step + 1} steps, species {species} Lv{level} is a {symbol} slot',
              flush=True)


if __name__ == '__main__':
    main()
