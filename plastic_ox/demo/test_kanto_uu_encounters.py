#!/usr/bin/env python3
"""UU-band wild tables and the National Park Thursday extras, played in mGBA.

* Routes 8, 7 and 21 (cinnabar checkpoint: tier UU, cap 42) roll their gPoxUU
  land tables: step in tall grass until a wild battle starts, then check the
  POKeMON and its level against the map's slots.
* Route 44's grass is Surf-only: no walking path from the Rustboro seam
  reaches a grass tile (water is the only way in), and the grass rolls the UU
  table with GIRAFARIG.
* SCYTHER and PINSIR are contest-only: the Warden's Thursday Bug-Catching
  Contest round (after badge 4) can roll them; a Tuesday round, a Thursday
  round before badge 4 and the park's ordinary Thursday grass cannot.
* Every Warden's Thursday contest win (after badge 4) gives a KANGASKHAN
  (two in a row both do; a full party sends it to the PC); before badge 4
  the win pays the usual SUN STONE.

The field warp only places the player; the encounter or prize is the thing
under test.
"""
import random
import struct
import sys

from test_region_walk import current, navigate, KEYS, DELTAS, BEHAVIORS, water
from test_story import StoryGame
from test_national_park import call, set_weekday
from test_sudowoodo_v1 import const


def sp_id(name):
    return const('SPECIES_' + name, 'species.h')

CASES = [
    # (map dir, spawn tile, table symbol)
    ('Route8_Frlg', (60, 20), 'gPoxUURoute8_LandMons'),
    # Route 7's grass is the patch at (11..18, 4..8); spawn inside it.
    ('Route7_hns', (13, 6), 'gPoxUURoute7Hns_LandMons'),
    ('Route21_North_Frlg', None, 'gPoxUURoute21North_LandMons'),
    # Route 44's grass is Surf-only (checked by route44_surf_only); spawn on it.
    ('Route44_hns', (32, 14), 'gPoxRoute44Hns_LandMons'),
]
FORBIDDEN = {'KANGASKHAN', 'SCYTHER', 'PINSIR'}


def grass_fn(g):
    def grass(x, y):
        return g.collision_at(x, y)[0] == 0 and BEHAVIORS[g.behavior_at(x, y)[0]] == 'MB_TALL_GRASS'
    return grass


def first_grass(g):
    grass = grass_fn(g)
    for y in range(1, 60):
        for x in range(1, 40):
            if grass(x, y):
                return x, y
    raise AssertionError('no grass tile found')


def step_until_battle(g, name, limit=400):
    grass = grass_fn(g)

    def pair(x, y):
        return grass(x, y) and any(grass(x + dx, y + dy) for dx, dy in DELTAS.values())
    s = g.state()
    if not pair(s['x'], s['y']):
        navigate(g, pair)
        s = g.state()
    direction = next(k for k, (dx, dy) in DELTAS.items() if grass(s['x'] + dx, s['y'] + dy))
    reverse = dict(N='S', S='N', E='W', W='E')[direction]
    g.write(g.syms['sWildEncountersDisabled'], 0)
    for step in range(limit):
        g.tap(KEYS[direction if step % 2 == 0 else reverse], hold=10, wait=20)
        if g.u32(g.syms['gBattleTypeFlags']):
            g.frame(120)
            return step + 1
        assert current(g) == name
    raise AssertionError((name, 'no grass encounter'))


def enemy(g):
    mon = g.syms['gParties'] + g.sizes['gParties'] // 4
    return g.box_species(mon), g.u8(mon + 0x54)


def slots(g, symbol):
    stride = g.sizes[symbol] // 12
    return [(g.u8(g.syms[symbol] + i * stride), g.u8(g.syms[symbol] + i * stride + 1),
             g.u16(g.syms[symbol] + i * stride + 2)) for i in range(12)]


def route_tables():
    for name, spawn, symbol in CASES:
        g = StoryGame()
        g.flag('FLAG_POX_TRIGGERS_ENABLED', True)
        g.test_water = False
        if spawn is None:
            g.warp(name, 10, 10)
            g.frame(60)
            spawn = first_grass(g)
        g.warp(name, *spawn)
        g.frame(90)
        assert current(g) == name, (name, current(g))
        table = slots(g, symbol)
        banned = {sp_id(s) for s in FORBIDDEN}
        assert not banned & {sp for _lo, _hi, sp in table}, (name, table)
        assert all(36 <= lo <= hi <= 42 for lo, hi, _sp in table), (name, table)
        if name == 'Route44_hns':
            assert sp_id('GIRAFARIG') in {sp for _lo, _hi, sp in table}, table
        steps = step_until_battle(g, name)
        species, level = enemy(g)
        assert any(sp == species and lo <= level <= hi for lo, hi, sp in table), (name, species, level, table)
        print(f'PASS {name}: encounter after {steps} steps, species {species} Lv{level} is a {symbol} slot',
              flush=True)


def route44_surf_only():
    """Flood-fill Route 44 from the Rustboro seam on foot, then with Surf."""
    g = StoryGame()
    g.warp('Route44_hns', 1, 15)
    g.frame(90)
    tiles = {}
    for x in range(80):
        for y in range(40):
            try:
                tiles[(x, y)] = (g.collision_at(x, y)[0], BEHAVIORS[g.behavior_at(x, y)[0]])
            except Exception:
                pass
    grass = {p for p, (c, b) in tiles.items() if c == 0 and b == 'MB_TALL_GRASS'}

    def fill(surf):
        seen, todo = {(1, 15)}, [(1, 15)]
        while todo:
            x, y = todo.pop()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if n in seen or n not in tiles or tiles[n][0]:
                    continue
                b = tiles[n][1]
                if water(b) and not surf:
                    continue
                seen.add(n)
                todo.append(n)
        return seen
    on_foot, by_surf = fill(False) & grass, fill(True) & grass
    assert grass and not on_foot, ('Route 44 grass reachable on foot', sorted(on_foot)[:10])
    assert (32, 14) in by_surf, sorted(by_surf)[:10]
    print(f'PASS Route44_hns: {len(grass)} grass tiles, 0 reachable on foot, {len(by_surf)} via Surf', flush=True)


def contest_game():
    g = StoryGame(spawn=('Gate_NationalPark_hns', 38, 3))
    g.run('Pox_Cyndaquil')
    g.flag('FLAG_POX_TRIGGERS_ENABLED', True)
    g.flag('FLAG_SYS_CLOCK_SET', True)
    g.flag('FLAG_POX_WARDEN_GUEST', True)
    g.test_water = False
    return g


def park_thursday():
    """SCYTHER/PINSIR only inside the Warden's Thursday contest after badge 4."""
    extras = {sp_id('SCYTHER'), sp_id('PINSIR')}
    rng = random.Random(4)

    def sample(day, badge, contest, tries):
        g = contest_game()
        g.flag('FLAG_BADGE04_GET', badge)
        set_weekday(g, day)
        if contest:
            g.write(g.syms['gSpecialVar_0x8004'], 0, 2)
            g.write(g.syms['gSpecialVar_0x8007'], 1, 2)
            assert call(g, 'PlasticOxContest_Start') == 0, (day, badge)
        g.warp('NationalPark_Normal_hns', 26, 30)
        g.frame(90)
        if contest:
            assert g.u8(g.syms['sRunning']), 'contest session lost on entry'
        start = g.core.save_raw_state()
        seen = []
        for _ in range(tries):
            assert g.core.load_raw_state(start)
            g.write(g.syms['gRngValue'], rng.getrandbits(32), 4)
            step_until_battle(g, 'NationalPark_Normal_hns')
            seen.append(enemy(g))
            if seen[-1][0] in extras:
                break
        return seen
    thu = sample(4, True, True, 60)
    assert thu[-1][0] in extras, thu
    for day, badge, contest in ((2, True, True), (4, False, True), (4, True, False)):
        other = sample(day, badge, contest, 12)
        assert not extras & {sp for sp, _lv in other}, (day, badge, contest, other)
    print(f'PASS Thursday contest after badge 4 rolled species {thu[-1][0]} Lv{thu[-1][1]} after '
          f'{len(thu)} encounters; Tuesday contest, pre-badge-4 Thursday contest and Thursday '
          'park grass never did', flush=True)


def contest_kangaskhan():
    g = contest_game()
    kangaskhan = sp_id('KANGASKHAN')

    def win(day, badge):
        g.flag('FLAG_BADGE04_GET', badge)
        g.flag('FLAG_POX_DAILY_PARK_CONTEST', False)
        set_weekday(g, day)
        g.write(g.syms['gSpecialVar_0x8004'], 0, 2)
        g.write(g.syms['gSpecialVar_0x8007'], 1, 2)
        assert call(g, 'PlasticOxContest_Start') == 0, day
        stride = g.sizes['gParties'] // 24
        for i in range(stride):
            g.write(g.syms['sCandidate'] + i, g.u8(g.syms['gParties'] + i))
        g.write(g.syms['sNewCatch'], 1)
        g.write(g.syms['gSpecialVar_0x8004'], 1, 2)
        call(g, 'PlasticOxContest_AcceptCatch')
        g.write(g.syms['sRivalScore'], 0, 2)
        assert call(g, 'PlasticOxContest_Judge') == 1, 'not first place'
        before = g.count()
        return before, call(g, 'PlasticOxContest_ClaimPrize')

    stride = g.sizes['gParties'] // 24
    for n in (1, 2):
        before, result = win(4, True)
        assert result == 2, (n, result)   # POX_CONTEST_PRIZE_MON_PARTY
        assert not g.flag('FLAG_POX_CONTEST_KANGASKHAN_PENDING')
        assert g.count() == before + 1 and g.party_species(before) == kangaskhan, (n, g.party_species(before))
        assert g.u8(g.syms['gParties'] + before * stride + 0x54) == 36
    # Two consecutive Thursday wins both paid out. Fill the party; the next goes to the PC.
    while g.count() < 6:
        before, result = win(4, True)
        assert result in (2, 3), result
    before, result = win(4, True)
    assert result == 3 and g.count() == 6, (result, g.count())   # POX_CONTEST_PRIZE_MON_PC
    assert not g.flag('FLAG_POX_CONTEST_KANGASKHAN_PENDING')
    g = contest_game()
    before, result = win(4, False)
    assert result == 1 and g.count() == before, 'pre-badge-4 Thursday win must pay the SUN STONE'
    print('PASS Warden contest: two consecutive Thursday wins after badge 4 each give KANGASKHAN Lv36, '
          'a full party sends it to the PC, a pre-badge-4 Thursday win pays the SUN STONE', flush=True)


def main():
    which = sys.argv[1:] or ['routes', 'route44', 'park', 'contest']
    if 'routes' in which:
        route_tables()
    if 'route44' in which:
        route44_surf_only()
    if 'park' in which:
        park_thursday()
    if 'contest' in which:
        contest_kangaskhan()


if __name__ == '__main__':
    main()
