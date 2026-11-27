#!/usr/bin/env python3
"""Ruins of Alph: the Route 36 researcher, the gatehouse chain, the dig site's
terraces and the three Regi chambers that replaced the Route 127 caves.

    plastic_ox/bin/pox-mgba-python plastic_ox/demo/test_ruins_of_alph.py

Static checks (map JSON, a ledge/Surf-aware walk of the dig site, dialogue
duplicates) run first; they need no emulator. Emulator setup writes RAM only
(flags, bag, position); never ROM or save files.
"""
import json
import re
import struct
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'plastic_ox/tools'))

ROUTE36 = 'Route36_hns'
GATE = 'Gate_RuinsOfAlph_Route36_hns'
OUTSIDE = 'RuinsOfAlph_Outside_hns'
CHAMBERS = 'RuinsOfAlph_PuzzleAndRewardChambers_hns'
RESEARCHER = (56, 24)
LANES = (55, 56, 57)
# (species, tablet, badges needed, dig-site door, chamber door, back-wall door,
#  back-room door, sage)
REGIS = [
    ('Regirock', 'ITEM_ANCIENT_ROCK_TABLET', 5, (28, 11), (20, 9), (21, 1), (20, 43), (20, 39)),
    ('Registeel', 'ITEM_ANCIENT_STEEL_TABLET', 6, (7, 40), (4, 26), (5, 18), (4, 60), (4, 56)),
    ('Regice', 'ITEM_ANCIENT_ICE_TABLET', 6, (34, 42), (20, 26), (21, 18), (20, 60), (20, 56)),
]
# (cave, Route 127 mouth)
OLD_CAVES = [('DesertRuins', (28, 5)), ('IslandCave', (29, 33)), ('AncientTomb', (69, 12))]
ARRIVAL = (20, 7)       # first tile below the gatehouse door on the dig site
JUMP = {'MB_JUMP_SOUTH': (0, 1), 'MB_JUMP_NORTH': (0, -1), 'MB_JUMP_EAST': (1, 0), 'MB_JUMP_WEST': (-1, 0)}


# ---------------------------------------------------------------- static part
def load_map(name):
    return json.loads((ROOT / f'data/maps/{name}/map.json').read_text())


def layout_of(name):
    layouts = {l['id']: l for l in json.loads((ROOT / 'data/layouts/layouts.json').read_text())['layouts'] if 'id' in l}
    return layouts[load_map(name)['layout']]


class Grid:
    """Block words plus behaviour names for one layout."""

    def __init__(self, name):
        from render_solidity import tileset_attrs, BEHAVIORS
        self.lay = layout_of(name)
        raw = (ROOT / self.lay['blockdata_filepath']).read_bytes()
        self.blocks = struct.unpack('<' + 'H' * (len(raw) // 2), raw)
        self.w, self.h = self.lay['width'], self.lay['height']
        self.primary = tileset_attrs(self.lay['primary_tileset'])
        self.secondary = tileset_attrs(self.lay['secondary_tileset'])
        self.names = BEHAVIORS

    def word(self, x, y):
        return self.blocks[y * self.w + x]

    def solid(self, x, y):
        return bool((self.word(x, y) >> 10) & 3)

    def behavior(self, x, y):
        tile = self.word(x, y) & 0x3FF
        attrs, i = (self.primary, tile) if tile < 640 else (self.secondary, tile - 640)
        value = attrs[i] & 0xFF if i < len(attrs) else 0
        return self.names.get(value, value) if isinstance(self.names, dict) else self.names[value]

    def water(self, x, y):
        b = str(self.behavior(x, y))
        return 'WATER' in b or 'OCEAN' in b


def reach(grid, warps, start, surf):
    """Tiles the player can stand on from start, with ledges and (optionally) Surf."""
    seen, todo = {start}, deque([start])
    while todo:
        x, y = todo.popleft()
        if (x, y) in warps and warps[(x, y)] not in seen:
            seen.add(warps[(x, y)])
            todo.append(warps[(x, y)])
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < grid.w and 0 <= ny < grid.h):
                continue
            if JUMP.get(str(grid.behavior(nx, ny))) == (dx, dy):
                nx, ny = nx + dx, ny + dy           # hop over the ledge tile
                if not (0 <= nx < grid.w and 0 <= ny < grid.h):
                    continue
            if grid.solid(nx, ny) or (grid.water(nx, ny) and not surf):
                continue
            if (nx, ny) not in seen:
                seen.add((nx, ny))
                todo.append((nx, ny))
    return seen


def test_static():
    layouts = [layout_of(n) for n in (GATE, OUTSIDE, CHAMBERS)]
    for lay in layouts:
        assert lay['layout_version'] == 'hns' and lay['include_in_versions'] == ['emerald'], lay
    outside, route36, chambers = load_map(OUTSIDE), load_map(ROUTE36), load_map(CHAMBERS)
    assert not outside['connections'], outside['connections']
    ruins_ids = {load_map(n)['id'] for n in (GATE, OUTSIDE, CHAMBERS)}
    assert not [c for c in route36['connections'] if c['map'] in ruins_ids]
    lanes = sorted((w['x'], w['y']) for w in route36['warp_events'] if w['dest_map'] == load_map(GATE)['id'])
    assert lanes == [(x, 25) for x in LANES], lanes
    assert route36['warp_events'][2]['x'] == 56, 'the gatehouse returns to Route 36 warp 2'
    men = [o for o in route36['object_events'] if 'Ruins' in o['script']]
    assert len(men) == 1 and (men[0]['x'], men[0]['y']) == RESEARCHER, men
    assert men[0]['graphics_id'] == 'OBJ_EVENT_GFX_SCIENTIST_1' and men[0]['flag'] == 'FLAG_POX_HIDE_RUINS_RESEARCHER'
    print('PASS: HNS layouts kept; warps only; one researcher and three gate lanes on Route 36', flush=True)

    # Dig site: every door with a Regi behind it, there and back.
    grid = Grid(OUTSIDE)
    by_id = outside['warp_events']
    same_map = {(w['x'], w['y']): (by_id[int(w['dest_warp_id'])]['x'], by_id[int(w['dest_warp_id'])]['y'])
                for w in by_id if w['dest_map'] == outside['id']}
    doors = {species: door for species, _, _, door, *_ in REGIS}
    on_foot = reach(grid, same_map, ARRIVAL, surf=False)
    with_surf = reach(grid, same_map, ARRIVAL, surf=True)
    assert doors['Regirock'] in on_foot, 'north chamber must need no HM'
    for species, door in doors.items():
        assert door in with_surf, (species, door)
        assert ARRIVAL in reach(grid, same_map, (door[0], door[1] + 1), surf=True), ('no way back from', species)
    need_surf = sorted(s for s, d in doors.items() if d not in on_foot)
    assert need_surf == ['Regice', 'Registeel'], need_surf
    # The two repainted ledge tiles are what make the south terraces two-way.
    for tile in ((18, 38), (22, 40)):
        assert not grid.solid(*tile) and str(grid.behavior(*tile)) not in JUMP, (tile, grid.behavior(*tile))
    grass = [(x, y) for y in range(grid.h) for x in range(grid.w) if 'TALL_GRASS' in str(grid.behavior(x, y))]
    assert grass and all(t in with_surf for t in grass), 'some tall grass is unreachable'
    # No dead ends: from anywhere reachable, the gatehouse door can be reached again.
    stuck = [t for t in with_surf if not grid.water(*t) and ARRIVAL not in reach(grid, same_map, t, surf=True)]
    assert not stuck, stuck[:10]
    print('PASS: dig site walk: north chamber on foot; south-west and south-east with Surf only; '
          'all tall grass reachable; no one-way traps', flush=True)

    # Chambers: one Regi and one sage per back room, the fourth chamber empty.
    for species, _, _, _, door, wall, back, sage in REGIS:
        upper = species.upper()
        objs = {o.get('local_id'): o for o in chambers['object_events']}
        regi, keeper = objs[f'LOCALID_POX_{upper}'], objs[f'LOCALID_POX_{upper}_SAGE']
        assert regi['script'] == keeper['script'] == 'PoxTournament_' + species
        assert regi['flag'] == keeper['flag'] == 'FLAG_POX_CAUGHT_' + upper
        assert (keeper['x'], keeper['y']) == sage
    assert len(chambers['object_events']) == 6
    scripts = (ROOT / f'data/maps/{CHAMBERS}/scripts.inc').read_text()
    for word in ('DoSlidingPuzzle', 'warphole', 'FLAG_COMPLETED', 'UNOWN', 'VAR_RUINSOFALPH_STATE'):
        assert word not in scripts, word
    print('PASS: three Regis with their sages, tablet doors only; no puzzle or Unown callbacks', flush=True)

    # Old sites: nothing left that offers a Regi.
    for cave, _ in OLD_CAVES:
        data = load_map(cave)
        assert data['object_events'] == [], (cave, data['object_events'])
        text = (ROOT / f'data/maps/{cave}/scripts.inc').read_text()
        assert 'PoxTournament' not in text and 'TABLET' not in text and 'tablet' not in text, cave
    print('PASS: DesertRuins, IslandCave and AncientTomb hold no Regi, sage or tablet check', flush=True)

    # No two NPCs or signs here share a line.
    lines = {}
    files = [ROOT / f'data/maps/{n}/scripts.inc' for n in (ROUTE36, GATE, OUTSIDE, CHAMBERS, *[c for c, _ in OLD_CAVES])]
    for path in files:
        for label, body in re.findall(r'^(\w+):+\n((?:\t\.string "[^\n]*\n)+)', path.read_text(), flags=re.M):
            text = ''.join(re.findall(r'"(.*)"', body))
            lines.setdefault(text, []).append(f'{path.parent.name}:{label}')
    dupes = {t: where for t, where in lines.items() if len(where) > 1}
    assert not dupes, dupes
    print(f'PASS: {len(lines)} strings across Route 36, the Ruins maps and the old caves, no duplicates', flush=True)


# -------------------------------------------------------------- emulator part
def emulator():
    from pox_fixtures import game as new_game, at, shot as _shot
    from test_sudowoodo_v1 import K, talk, settle, give_item, bag, wait_for_battle, const, run_code, opcode
    from walk_leg1 import navigate

    def shot(g, name):
        _shot(g, 'ruins_' + name)

    def pos(g):
        s = g.state()
        return s['x'], s['y']

    def hold(g, key, frames=90):
        g.core.set_keys(key)
        g.frame(frames)
        g.core.clear_keys(key)
        g.frame(60)

    def wait_map(g, name, frames=600):
        for _ in range(frames // 10):
            if at(g, name):
                g.frame(90)
                return True
            g.frame(10)
        return False

    def walk_into(g, key, name, frames=400):
        """Hold key until the map changes to name, then let the arrival finish."""
        g.core.set_keys(key)
        try:
            for _ in range(frames):
                if at(g, name):
                    break
                g.frame(1)
        finally:
            g.core.clear_keys(key)
        g.frame(120)
        return at(g, name)

    def visible(g):
        stride = g.sizes['gObjectEvents'] // 16
        return {g.u8(g.syms['gObjectEvents'] + i * stride + 8)
                for i in range(16) if g.u8(g.syms['gObjectEvents'] + i * stride) & 1} - {0xFF}

    def said(r):
        return ' '.join(r['text']).replace('\n', ' ')

    def badges(g, count):
        for n in range(1, 9):
            g.flag(f'FLAG_BADGE{n:02}_GET', n <= count)

    def start(g, name, x, y):
        settle(g)
        g.warp(name, x, y)
        g.frame(90)
        assert at(g, name) and pos(g) == (x, y), g.describe()

    researcher_id = next(i + 1 for i, o in enumerate(load_map(ROUTE36)['object_events'])
                         if o.get('local_id') == 'LOCALID_POX_RUINS_RESEARCHER')

    # --- Flag unset: the researcher holds all three lanes.
    g = new_game()
    assert not g.flag('FLAG_POX_STORY_MANSION')
    for lane in LANES:
        start(g, ROUTE36, lane, 22)
        assert researcher_id in visible(g), visible(g)
        g.clear_text()
        hold(g, K.KEY_DOWN, 120)
        if lane == RESEARCHER[0]:
            assert pos(g) == (lane, 23), pos(g)            # walked into him
            text = said(talk(g, K.KEY_DOWN))
        else:
            text = g.text().replace('\n', ' ')              # the step trigger spoke
            settle(g)
            g.frame(60)
        assert 'closed' in text and 'CINNABAR' not in text, (lane, text)
        assert at(g, ROUTE36) and pos(g) == (lane, 23), (lane, pos(g), g.describe())
        hold(g, K.KEY_DOWN, 120)
        settle(g)
        g.frame(60)
        assert at(g, ROUTE36) and pos(g)[1] <= 24, (lane, g.describe())
        assert not g.flag('FLAG_POX_HIDE_RUINS_RESEARCHER')
    shot(g, 'route36_closed')
    print('PASS: flag unset: researcher turns the player back on lanes 55, 56 and 57; gate not reached', flush=True)

    # --- Flag set (also an old save that already has it): each lane opens.
    for lane in LANES:
        g = new_game()
        g.flag('FLAG_POX_STORY_MANSION', True)
        start(g, ROUTE36, lane, 22)
        assert researcher_id in visible(g)
        g.clear_text()
        hold(g, K.KEY_DOWN, 120)
        if lane == RESEARCHER[0]:
            text = said(talk(g, K.KEY_DOWN))
        else:
            text = g.text().replace('\n', ' ')
            settle(g)
        g.frame(120)
        assert 'CINNABAR' in text, (lane, text)
        assert g.flag('FLAG_POX_HIDE_RUINS_RESEARCHER') and researcher_id not in visible(g), (lane, visible(g))
        assert walk_into(g, K.KEY_DOWN, GATE), (lane, g.describe())
        assert pos(g) == (7, 2), pos(g)
        # Re-entering the route keeps him gone and the triggers quiet.
        assert walk_into(g, K.KEY_UP, ROUTE36), g.describe()
        assert pos(g) == (56, 25), pos(g)
        assert researcher_id not in visible(g)
    shot(g, 'route36_open')
    print('PASS: flag set: he names CINNABAR, walks into the gatehouse, hide flag set; lanes 55-57 reach the gate',
          flush=True)

    # --- Warp chain Route 36 -> gatehouse -> dig site and back, on the D-pad.
    navigate(g, (56, 23))
    assert walk_into(g, K.KEY_DOWN, GATE) and pos(g) == (7, 2), g.describe()
    shot(g, 'gatehouse')
    navigate(g, (5, 5))
    r = talk(g, K.KEY_LEFT)                   # the same researcher, across the desk
    assert 'CINNABAR' in said(r) and 'tablet' in said(r), r
    settle(g)
    navigate(g, (7, 8))
    assert walk_into(g, K.KEY_DOWN, OUTSIDE), g.describe()
    assert pos(g) == ARRIVAL, pos(g)
    shot(g, 'outside_arrival')
    assert walk_into(g, K.KEY_UP, GATE), g.describe()
    assert pos(g) == (7, 9), pos(g)
    navigate(g, (7, 2))
    assert walk_into(g, K.KEY_UP, ROUTE36) and pos(g) == (56, 25), g.describe()
    print('PASS: Route 36 (56,25) <-> gatehouse (7,1)/(7,9) <-> dig site (20,6), both directions', flush=True)

    # --- Dig site on foot: north chamber, then Surf, the two repainted ledges,
    # both southern chambers and the crawlway to the west terrace.
    def enter_chamber(species):
        _, _, _, door, inside, *_ = next(r for r in REGIS if r[0] == species)
        navigate(g, (door[0], door[1] + 1))
        assert walk_into(g, K.KEY_UP, CHAMBERS), (species, g.describe())
        assert pos(g) == inside, (species, pos(g))
        shot(g, 'chamber_' + species.lower())
        assert walk_into(g, K.KEY_DOWN, OUTSIDE), (species, g.describe())
        assert pos(g) == (door[0], door[1] + 1), (species, pos(g))

    start(g, OUTSIDE, *ARRIVAL)
    enter_chamber('Regirock')
    navigate(g, (28, 32))
    g.tap(K.KEY_DOWN, hold=2, wait=20)        # face the pond
    assert pos(g) == (28, 32), pos(g)
    fldeff = int(re.search(r'FLDEFF_USE_SURF\s+(\d+)', (ROOT / 'include/constants/field_effects.h').read_text())[1])
    run_code(g, opcode(g, 'lockall') + opcode(g, 'setfieldeffectargument') + struct.pack('<BH', 0, 0)
             + opcode(g, 'dofieldeffect') + struct.pack('<H', fldeff)
             + opcode(g, 'waitfieldeffect') + struct.pack('<H', fldeff) + opcode(g, 'releaseall'), frames=600)
    g.frame(60)
    assert pos(g) == (28, 33), ('Surf did not start', pos(g))
    shot(g, 'pond_surf')
    hold(g, K.KEY_DOWN, 240)
    assert pos(g)[1] >= 38, ('pond not crossed', pos(g))
    enter_chamber('Regice')
    navigate(g, (23, 40))
    hold(g, K.KEY_LEFT, 40)                   # through the repainted (22,40)
    assert pos(g)[0] <= 21, pos(g)
    navigate(g, (21, 40))
    hold(g, K.KEY_RIGHT, 40)
    assert pos(g)[0] >= 23, ('gap must be two-way', pos(g))
    shot(g, 'ledge_gap_east')
    navigate(g, (21, 40))
    enter_chamber('Registeel')
    navigate(g, (19, 38))
    hold(g, K.KEY_LEFT, 40)                   # through the repainted (18,38)
    assert pos(g)[0] <= 17 and pos(g)[1] == 38, pos(g)
    shot(g, 'ledge_gap_plateau')
    navigate(g, (14, 37))
    hold(g, K.KEY_UP, 30)
    g.frame(240)
    assert at(g, OUTSIDE) and pos(g) == (13, 26), ('crawlway south -> west', pos(g))
    shot(g, 'west_terrace')
    navigate(g, (5, 24))                      # the unused west chamber's door
    navigate(g, (13, 26))
    hold(g, K.KEY_UP, 30)
    g.frame(240)
    assert at(g, OUTSIDE) and pos(g) == (14, 37), ('crawlway west -> south', pos(g))
    navigate(g, (19, 38))                     # and back out through the plateau gap
    print('PASS: dig site walked: north chamber, Surf across the pond, south-east and south-west chambers, '
          'both ledge gaps two-way, crawlway to the west terrace and back', flush=True)

    # --- Each Regi: sealed without its tablet; sage refuses below its badge; battle with both.
    for species, tablet_name, need, _, inside, wall, back, sage in REGIS:
        tablet = const(tablet_name, 'items.h')
        g = new_game()
        badges(g, 8)
        below = (wall[0], wall[1] + 1)
        assert bag(g, tablet) == 0
        start(g, CHAMBERS, *below)
        r = talk(g, K.KEY_UP)
        assert 'tablet' in said(r) and not r['battle'], (species, r)
        settle(g)
        hold(g, K.KEY_UP)
        assert at(g, CHAMBERS) and pos(g) == below, (species, pos(g))
        shot(g, species.lower() + '_sealed')
        # Even standing in front of it, no tablet means no battle.
        start(g, CHAMBERS, sage[0], sage[1] + 1)
        r = talk(g, K.KEY_UP)
        assert not r['battle'] and 'sealed' in said(r), (species, r)
        settle(g)

        give_item(g, tablet)
        assert bag(g, tablet) == 1
        badges(g, need - 1)
        start(g, CHAMBERS, *below)                 # reload: the back wall is open now
        shot(g, species.lower() + '_open')
        hold(g, K.KEY_UP, 40)
        g.frame(240)
        assert at(g, CHAMBERS) and pos(g) == back, (species, pos(g))
        navigate(g, (sage[0], sage[1] + 1))
        shot(g, species.lower() + '_back_room')
        r = talk(g, K.KEY_UP)
        assert not r['battle'] and 'sealed' in said(r), (species, 'badge gate', r)
        settle(g)
        assert not g.flag('FLAG_POX_CAUGHT_' + species.upper())

        badges(g, need)
        r = talk(g, K.KEY_UP)
        assert r['battle'] and wait_for_battle(g), (species, r)
        shot(g, species.lower() + '_battle')
        print(f'PASS: {species}: sealed without {tablet_name}; sage refuses with {need - 1} badges; '
              f'battle starts with the tablet and {need}', flush=True)

    # --- Old Route 127 sites: caves still enterable, nothing to fight.
    g = new_game()
    badges(g, 8)
    for _, tablet_name, *_ in REGIS:
        give_item(g, const(tablet_name, 'items.h'))
    for cave, mouth in OLD_CAVES:
        start(g, 'Route127', mouth[0], mouth[1] + 1)
        hold(g, K.KEY_UP, 30)
        assert wait_map(g, cave), (cave, g.describe())
        assert pos(g) == (8, 29), pos(g)
        start(g, cave, 8, 21)
        assert not visible(g), (cave, visible(g))
        r = talk(g, K.KEY_UP)
        assert 'tablet' not in said(r).lower() and not r['battle'], (cave, r)
        settle(g)
        start(g, cave, 8, 8)
        assert not visible(g), (cave, visible(g))
        r = talk(g, K.KEY_UP)
        assert not r['battle'] and not r['text'], (cave, r)
        settle(g)
        shot(g, cave + '_empty')
    print('PASS: DesertRuins, IslandCave, AncientTomb: reachable from Route 127, empty, no battle '
          'even with all three tablets and eight badges', flush=True)


if __name__ == '__main__':
    test_static()
    if '--static' not in sys.argv:
        emulator()
    print('Ruins of Alph: PASS', flush=True)
