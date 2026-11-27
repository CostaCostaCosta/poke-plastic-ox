#!/usr/bin/env python3
"""UU-band wild tables and the National Park Thursday extras, played in mGBA.

* Routes 8, 7 and 21 (cinnabar checkpoint: tier UU, cap 42) roll their gPoxUU
  land tables: step in tall grass until a wild battle starts, then check the
  POKeMON and its level against the map's slots.
* Route 20 West's open sea (same checkpoint) rolls its gPoxUU Surf table:
  Surf off the landing and swim until a wild battle starts.
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
import json
import random
import re
import struct
import sys
from pathlib import Path

from test_region_walk import current, navigate, KEYS, DELTAS, BEHAVIORS, water
from test_story import StoryGame
from test_national_park import call, set_weekday
from test_sudowoodo_v1 import CHARMAP, const
from walklib import K


def sp_id(name):
    return const('SPECIES_' + name, 'species.h')

CASES = [
    # (map dir, spawn tile, table symbol)
    ('Route8_Frlg', (60, 20), 'gPoxUURoute8_LandMons'),
    # Route 7's grass is the patch at (11..18, 4..8); spawn inside it.
    ('Route7_hns', (13, 6), 'gPoxUURoute7Hns_LandMons'),
    ('Route21_North_Frlg', None, 'gPoxUURoute21North_LandMons'),
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


def route44_surf_to_grass():
    """Walk Route 44 from the Rustboro seam, Surf from the shore for real (the
    YES/NO prompt with a Surf mon and the SURF KEY), cross the water and land
    on the grass, then roll its UU table (GIRAFARIG)."""
    from test_warps_v1 import make_playtest
    name, symbol = 'Route44_hns', 'gPoxRoute44Hns_LandMons'
    g = make_playtest()
    g.flag('FLAG_POX_TRIGGERS_ENABLED', True)
    g.test_water = False
    # Route 44's sight trainers would stop the swim; they are not under test.
    root = Path(__file__).resolve().parents[2]
    opponents = (root / 'include/constants/opponents.h').read_text()
    for trainer in set(re.findall(r'trainerbattle_\w+ (TRAINER_\w+)',
                                  (root / f'data/maps/{name}/scripts.inc').read_text())):
        tid = int(re.search(r'#define ' + trainer + r'\s+(\d+)', opponents)[1])
        # TRAINER_FLAG() in include/constants/flags.h: Plastic Ox ids 857..925
        # live in the 0x4A0 run; older ids use TRAINER_FLAGS_START (0x500).
        assert tid < 926, (trainer, tid)
        g.flag(0x4A0 + tid - 857 if tid >= 857 else 0x500 + tid, True)
    g.warp(name, 1, 15)
    g.frame(90)
    table = slots(g, symbol)
    banned = {sp_id(s) for s in FORBIDDEN}
    assert not banned & {sp for _lo, _hi, sp in table}, table
    assert all(36 <= lo <= hi <= 42 for lo, hi, _sp in table), table
    assert sp_id('GIRAFARIG') in {sp for _lo, _hi, sp in table}, table
    tiles = {}
    for x in range(80):
        for y in range(40):
            try:
                tiles[(x, y)] = (g.collision_at(x, y)[0], BEHAVIORS[g.behavior_at(x, y)[0]])
            except Exception:
                pass
    seen, todo = {(1, 15)}, [(1, 15)]
    while todo:
        x, y = todo.pop()
        for dx, dy in DELTAS.values():
            n = (x + dx, y + dy)
            if n not in seen and n in tiles and not tiles[n][0] and not water(tiles[n][1]):
                seen.add(n)
                todo.append(n)
    # Nearest the Rustboro seam first: the walk there stays on the open road.
    # Only water that actually touches the grass is worth launching into.
    open_water = {p for p, (c, b) in tiles.items() if not c and water(b)}
    lake, todo = set(), [p for p in open_water
                         if any(tiles.get((p[0] + dx, p[1] + dy), (1, ''))[1] == 'MB_TALL_GRASS'
                                for dx, dy in DELTAS.values())]
    lake.update(todo)
    while todo:
        x, y = todo.pop()
        for dx, dy in DELTAS.values():
            n = (x + dx, y + dy)
            if n in open_water and n not in lake:
                lake.add(n)
                todo.append(n)
    shores = sorted(((abs(x - 1) + abs(y - 15), (x, y), d) for (x, y) in seen
                     for d, (dx, dy) in DELTAS.items() if (x + dx, y + dy) in lake))
    assert shores, 'no shore on the walkable side of Route 44'
    ok, note = False, 'no shore tried'
    for _dist, shore, d in shores[:40]:
        g.release_scripts()
        g.warp(name, 1, 15)
        g.frame(60)
        try:
            navigate(g, lambda x, y, s=shore: (x, y) == s)
        except AssertionError as e:
            note = str(e)
            print('   shore', shore, 'unreachable:', note, flush=True)
            continue
        ok, note = g.mount_surf({'N': 'UP', 'S': 'DOWN', 'E': 'RIGHT', 'W': 'LEFT'}[d])
        if ok:
            break
        print('   shore', shore, d, 'no Surf:', note, g.state(), flush=True)
    else:
        raise AssertionError(('could not Surf from any shore', note))
    print(f'ok  Route44_hns: surfed from the shore at {shore} ({note})', flush=True)
    # Swim: a breadth-first path over open water to a tile beside the grass,
    # then one stroke onto the grass (the engine dismounts there).
    occupied = {(o['x'], o['y']) for o in json.loads((Path(__file__).resolve().parents[2]
                / f'data/maps/{name}/map.json').read_text())['object_events']}
    s = g.state()
    start, prev = (s['x'], s['y']), {(s['x'], s['y']): None}
    queue, end = [start], None
    while queue and end is None:
        cur = queue.pop(0)
        for dx, dy in DELTAS.values():
            n = (cur[0] + dx, cur[1] + dy)
            if n in prev or n not in tiles or tiles[n][0] or n in occupied:
                continue
            if tiles[n][1] == 'MB_TALL_GRASS':
                prev[n], end = cur, n
                break
            if water(tiles[n][1]):
                prev[n] = cur
                queue.append(n)
    assert end, ('no swim route to the grass', start)
    path = []
    while end is not None:
        path.append(end)
        end = prev[end]
    path.reverse()
    keys = {(1, 0): K.KEY_RIGHT, (-1, 0): K.KEY_LEFT, (0, 1): K.KEY_DOWN, (0, -1): K.KEY_UP}
    for _ in range(len(path) * 4):
        here = (g.state()['x'], g.state()['y'])
        if here == path[-1]:
            break
        assert here in path, ('swim left the route', here, path)
        i = path.index(here)
        nxt = path[i + 1]
        g.tap(keys[(nxt[0] - here[0], nxt[1] - here[1])], hold=1, wait=18)
    assert (g.state()['x'], g.state()['y']) == path[-1], ('swim stalled', g.state(), path)
    g.frame(60)
    landed = (g.state()['x'], g.state()['y'])
    assert not g.surfing() and BEHAVIORS[g.behavior_at(*landed)[0]] == 'MB_TALL_GRASS', g.state()
    print(f'ok  Route44_hns: swam {len(path) - 1} tiles and stepped onto the grass at {landed}', flush=True)
    steps = step_until_battle(g, name)
    species, level = enemy(g)
    assert any(sp == species and lo <= level <= hi for lo, hi, sp in table), (species, level, table)
    print(f'PASS Route44_hns: surfed to the grass, encounter after {steps} steps, species {species} '
          f'Lv{level} is a {symbol} slot', flush=True)


def route20_surf():
    """Route 20 West (the open sea between CINNABAR and SEAFOAM): walk the
    landing, Surf from its shore for real, swim back and forth until a wild
    battle starts, and check it against gPoxUURoute20West's five Surf slots."""
    from test_warps_v1 import make_playtest
    name, symbol, spawn = 'PlasticOx_Route20West', 'gPoxUURoute20West_WaterMons', (58, 10)
    g = make_playtest()
    g.flag('FLAG_POX_TRIGGERS_ENABLED', True)
    g.test_water = False
    g.warp(name, *spawn)
    g.frame(90)
    assert current(g) == name, current(g)
    stride = g.sizes[symbol] // 5
    table = [(g.u8(g.syms[symbol] + i * stride), g.u8(g.syms[symbol] + i * stride + 1),
              g.u16(g.syms[symbol] + i * stride + 2)) for i in range(5)]
    assert all(36 <= lo <= hi <= 42 for lo, hi, _sp in table), table
    assert not {sp_id(s) for s in FORBIDDEN} & {sp for _lo, _hi, sp in table}, table
    tiles = {}
    for x in range(spawn[0] - 20, spawn[0] + 20):
        for y in range(spawn[1] - 15, spawn[1] + 15):
            try:
                tiles[(x, y)] = (g.collision_at(x, y)[0], BEHAVIORS[g.behavior_at(x, y)[0]])
            except Exception:
                pass
    seen, todo = {spawn}, [spawn]
    while todo:
        x, y = todo.pop()
        for dx, dy in DELTAS.values():
            n = (x + dx, y + dy)
            if n not in seen and n in tiles and not tiles[n][0] and not water(tiles[n][1]):
                seen.add(n)
                todo.append(n)

    def open_water(p):
        return p in tiles and not tiles[p][0] and water(tiles[p][1])
    # A shore whose water tile has another open water tile beyond it, to swim on.
    shores = sorted((abs(x - spawn[0]) + abs(y - spawn[1]), (x, y), d) for (x, y) in seen
                    for d, (dx, dy) in DELTAS.items()
                    if open_water((x + dx, y + dy)) and open_water((x + 2 * dx, y + 2 * dy)))
    assert shores, 'no shore on the Route 20 West landing'
    for _dist, shore, d in shores[:20]:
        g.release_scripts()
        g.warp(name, *spawn)
        g.frame(60)
        try:
            navigate(g, lambda x, y, s=shore: (x, y) == s)
        except AssertionError:
            continue
        ok, note = g.mount_surf({'N': 'UP', 'S': 'DOWN', 'E': 'RIGHT', 'W': 'LEFT'}[d])
        if ok:
            break
    else:
        raise AssertionError('could not Surf from the Route 20 West landing')
    reverse = dict(N='S', S='N', E='W', W='E')[d]
    g.tap(KEYS[d], hold=1, wait=18)  # one stroke out, so both legs stay on water
    g.write(g.syms['sWildEncountersDisabled'], 0)
    for step in range(600):
        g.tap(KEYS[d if step % 2 == 0 else reverse], hold=1, wait=18)
        if g.u32(g.syms['gBattleTypeFlags']):
            g.frame(120)
            break
        assert g.surfing() and current(g) == name, g.state()
    else:
        raise AssertionError('no Surf encounter on Route 20 West')
    species, level = enemy(g)
    assert any(sp == species and lo <= level <= hi for lo, hi, sp in table), (species, level, table)
    print(f'PASS {name}: surfed from {shore}, encounter after {step + 1} strokes, species {species} '
          f'Lv{level} is a {symbol} slot', flush=True)


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


def script_texts(g, label, limit=600):
    """Run a field script to completion, pressing A; return its text boxes."""
    def text():
        out = []
        for i in range(400):
            b = g.u8(g.syms['gStringVar4'] + i)
            if b == 0xFF:
                break
            out.append(CHARMAP.get(b, '?'))
        return ''.join(out)
    g.write(g.syms['gStringVar4'], 0xFF)
    g.begin(label)
    seen = []
    for _ in range(limit):
        t = text()
        if t and (not seen or seen[-1] != t):
            seen.append(t)
        if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            return seen
        g.tap(K.KEY_A, hold=2, wait=10)
    raise AssertionError(('script never ended', label, seen))


def contest_claim_any_day():
    """A Thursday win claimed at the desk: the WARDEN speaks on Thursday, the
    desk attendant (with its own lines) any other day."""
    kangaskhan = sp_id('KANGASKHAN')
    for day, who, absent in ((4, 'beaming', 'lunches'), (1, 'lunches', 'beaming')):
        g = contest_game()
        g.flag('FLAG_BADGE04_GET', True)
        set_weekday(g, 4)
        g.write(g.syms['gSpecialVar_0x8004'], 0, 2)
        g.write(g.syms['gSpecialVar_0x8007'], 1, 2)
        assert call(g, 'PlasticOxContest_Start') == 0
        stride = g.sizes['gParties'] // 24
        for i in range(stride):
            g.write(g.syms['sCandidate'] + i, g.u8(g.syms['gParties'] + i))
        g.write(g.syms['sNewCatch'], 1)
        g.write(g.syms['gSpecialVar_0x8004'], 1, 2)
        call(g, 'PlasticOxContest_AcceptCatch')
        g.write(g.syms['sRivalScore'], 0, 2)
        assert call(g, 'PlasticOxContest_Judge') == 1
        assert g.flag('FLAG_POX_CONTEST_KANGASKHAN_PENDING')
        set_weekday(g, day)   # the claim happens on this day
        before = g.count()
        texts = ' '.join(script_texts(g, 'PlasticOxContest_EventScript_AttendantPrize'))
        assert who in texts and absent not in texts, (day, texts)
        assert g.count() == before + 1 and g.party_species(before) == kangaskhan, (day, g.party_species(before))
        assert not g.flag('FLAG_POX_CONTEST_KANGASKHAN_PENDING')
    print('PASS pending KANGASKHAN: the WARDEN hands it over on Thursday, the desk on Monday, '
          'each with its own lines', flush=True)


def main():
    which = sys.argv[1:] or ['routes', 'route44', 'route20', 'park', 'contest', 'claim']
    if 'routes' in which:
        route_tables()
    if 'route44' in which:
        route44_surf_only()
        route44_surf_to_grass()
    if 'route20' in which:
        route20_surf()
    if 'park' in which:
        park_thursday()
    if 'contest' in which:
        contest_kangaskhan()
    if 'claim' in which:
        contest_claim_any_day()


if __name__ == '__main__':
    main()
