#!/usr/bin/env python3
"""Goldenrod-area polish: Pokemon Center, PCs, north gate roof, south road,
Pallet/Route 21 seam, Cinnabar sea road, and the park contest's Sport Balls.

Static checks run first; then each fix is exercised in the real ROM:
  * Goldenrod Pokemon Center uses the standard Johto PC room, the nurse runs
    the standard heal (Yes/No, machine, bow) and heals the party.
  * Using the PC in the Goldenrod Pokemon Center and in the National Park gate
    leaves the PC's metatile untouched (HNS PCs used to be overwritten with
    Emerald's PC on/off metatile ids).
  * Goldenrod's north gatehouse has a solid roof again, and its south avenue
    runs on past the map edge between trees instead of ending in water.
  * Route 21 North has no FRLG clone of Pallet's NPC standing in the margin.
  * Route 21 South no longer refuses the swim to Cinnabar.
  * In the contest, the quick-throw (R) button only throws the loaned Sport
    Balls and counts them down, even when the last ball thrown was the
    player's own.

    plastic_ox/bin/pox-mgba-python plastic_ox/demo/test_goldenrod_polish.py
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_story import ROOT, StoryGame
from walklib import K

ITEMS = (ROOT / 'include/constants/items.h').read_text()


def item_id(name):
    return int(re.search(rf'\b{name}\s*=\s*(\d+)', ITEMS)[1])


def load(name):
    return json.loads((ROOT / f'data/maps/{name}/map.json').read_text())


def static():
    pc = load('GoldenrodCity_PokemonCenter_hns')
    assert pc['layout'] == 'LAYOUT_POKEMON_CENTER_JOHTO_HNS'
    nurse = [o for o in pc['object_events'] if o.get('local_id') == 'LOCALID_GOLDENROD_NURSE']
    assert nurse and (nurse[0]['x'], nurse[0]['y']) == (7, 2)
    assert not any('LINK_RECEPTIONIST' in o['graphics_id'] for o in pc['object_events'])
    route = load('Route21_North_Frlg')
    assert not any(o.get('type') == 'clone' and o.get('target_map') == 'MAP_PALLET_TOWN'
                   for o in route['object_events'])
    south = load('Route21_South_Frlg')
    assert not any('CinnabarSeam' in e['script'] for e in south['coord_events'])
    table = (ROOT / 'src/data/plastic_ox_pu_encounters.h').read_text()
    body = re.search(r'sPoxParkContestPassDayMons\[\] = \{(.*?)\};', table, re.S)[1]
    mons = re.findall(r'\{ (\d+), (\d+), SPECIES_(\w+) \}', body)
    assert all((int(lo), int(hi)) == (34, 38) for lo, hi, _ in mons), mons
    assert {'SCYTHER', 'PINSIR'} <= {s for *_, s in mons}
    assert not {'CATERPIE', 'WEEDLE', 'METAPOD', 'KAKUNA'} & {s for *_, s in mons}
    print('ok  static: standard PC room, no Pallet clone, no Cinnabar current, Thursday table Lv34-38', flush=True)


def finish(g, limit=400, settle=0):
    idle = 0
    for _ in range(limit):
        g.tap(K.KEY_A, hold=2, wait=10)
        # The heal animation briefly idles the script; require a settled stop.
        idle = idle + 1 if g.u8(g.syms['sGlobalScriptContextStatus']) == 2 else 0
        if idle * 12 > settle:
            g.frame(60)
            return
    raise AssertionError(('dialogue stuck', g.describe()))


def use_pc(g, pc_xy, stand_xy, tag):
    before = g.metatile_at(*pc_xy)[0]
    g.warp(g.map_name, *stand_xy)
    g.frame(90)
    g.tap(K.KEY_UP, hold=8, wait=20)
    g.tap(K.KEY_A, hold=2, wait=90)
    assert g.u8(g.syms['sGlobalScriptContextStatus']) != 2, (tag, 'PC did not respond')
    for _ in range(12):
        g.tap(K.KEY_B, hold=2, wait=30)
        if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            break
    g.frame(90)
    after = g.metatile_at(*pc_xy)[0]
    g.shot(f'polish_pc_{tag}.png')
    assert after == before, (tag, hex(before), hex(after))


def pokemon_center():
    g = StoryGame(spawn=('GoldenrodCity_PokemonCenter_hns', 7, 4))
    g.map_name = 'GoldenrodCity_PokemonCenter_hns'
    g.run('Pox_Cyndaquil')
    g.flag('FLAG_POX_TRIGGERS_ENABLED', True)
    g.warp('GoldenrodCity_PokemonCenter_hns', 7, 4)
    g.frame(90)
    # struct Pokemon ends with hp, maxHP and five stats (seven u16).
    hp = g.syms['gParties'] + g.sizes['gParties'] // 24 - 14
    g.write(hp, 1, 2)
    g.frame(60)
    g.tap(K.KEY_UP, hold=8, wait=20)
    g.tap(K.KEY_A, hold=2, wait=30)
    assert g.u8(g.syms['sGlobalScriptContextStatus']) != 2, 'nurse did not respond'
    # Facing the nurse, A would talk to her again: press A until the heal
    # lands, then B through the goodbye.
    for _ in range(300):
        g.tap(K.KEY_A, hold=2, wait=10)
        if g.u16(hp) > 1:
            break
    assert g.u16(hp) > 1, 'nurse did not heal'
    for _ in range(100):
        g.tap(K.KEY_B, hold=2, wait=10)
        if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            break
    g.frame(120)
    assert g.u8(g.syms['sGlobalScriptContextStatus']) == 2, 'nurse script did not end'
    g.shot('polish_goldenrod_nurse.png')
    print('ok  Goldenrod Pokemon Center nurse heals with the standard script', flush=True)
    use_pc(g, (11, 1), (11, 2), 'goldenrod')
    print('ok  Goldenrod PC metatile unchanged after use', flush=True)
    g.map_name = 'Gate_NationalPark_hns'
    g.warp('Gate_NationalPark_hns', 4, 3)
    g.frame(90)
    use_pc(g, (4, 1), (4, 2), 'park_gate')
    print('ok  National Park gate PC metatile unchanged after use', flush=True)


def goldenrod_edges():
    g = StoryGame(spawn=('GoldenrodCity_hns', 33, 9))
    # The donor roof keeps one enclosed passable row (3); it can't be reached.
    for y in (0, 1, 2, 4, 5, 6):
        assert g.collision_at(33, y)[0] != 0, ('walkable gate roof', y)
    g.shot('polish_north_gate.png')
    g.warp('GoldenrodCity_hns', 33, 44)
    g.frame(90)
    # The margin is drawn at render time (src/plastic_ox_borders.c over the
    # layout border), so check those sources; the screenshot shows the result.
    border = (ROOT / 'data/layouts/GoldenrodCity_hns/border.bin').read_bytes()
    assert border == (ROOT / 'data/layouts/Route34_hns/border.bin').read_bytes(), 'border is not forest'
    zones = (ROOT / 'src/plastic_ox_borders.c').read_text()
    for x0, x1, mt in ((31, 31, '0x3D0'), (32, 33, '0x3D1'), (34, 34, '0x3D2')):
        assert re.search(rf'LAYOUT_GOLDENROD_CITY_HNS, {x0}, {x1}, 46, HI, ONE\({mt}\)', zones), (x0, mt)
    g.shot('polish_south_road.png')
    print('ok  Goldenrod north gate roof solid; south road continues into a forest border', flush=True)


def contest_quick_ball():
    from test_national_park import set_weekday, finish_dialogue, call
    from test_sudowoodo_v1 import SudoGame, in_battle, wait_for_battle, bag, give_item, POCKET_BALLS
    from walk_leg1 import navigate
    poke, sport = item_id('ITEM_POKE_BALL'), item_id('ITEM_SPORT_BALL')
    g = SudoGame()
    g.warp('Gate_NationalPark_hns', 3, 3)
    call(g, 'GivePlasticOxPlayerParty')
    give_item(g, poke, 5)
    g.flag('FLAG_SYS_CLOCK_SET', True)
    set_weekday(g, 2)
    g.begin('Gate_NationalPark_EventScript_SouthAttendant')
    finish_dialogue(g)
    assert g.u8(g.syms['sRunning']), 'contest did not start'
    navigate(g, (26, 30))
    g.write(g.syms['sWildEncountersDisabled'], 0)
    for i in range(100):
        g.tap(K.KEY_RIGHT if i % 2 else K.KEY_LEFT, hold=18, wait=8)
        if in_battle(g):
            break
    assert wait_for_battle(g), 'no contest encounter'
    g.write(g.syms['sWildEncountersDisabled'], 1)
    for _ in range(600):
        if g.controller('HandleInputChooseAction'):
            break
        g.frame(4)
    # Pretend the last ball thrown was the player's own Poke Ball.
    g.write(g.syms['gLastThrownBall'], poke, 2)
    g.write(g.syms['gBallToDisplay'], poke, 2)
    before = g.u8(g.syms['gNumSafariBalls'])
    g.tap(K.KEY_R, hold=2, wait=60)
    for _ in range(200):
        if g.u8(g.syms['gNumSafariBalls']) < before:
            break
        g.frame(4)
    assert g.u8(g.syms['gNumSafariBalls']) == before - 1, 'quick throw did not count down'
    assert bag(g, poke, POCKET_BALLS) == 5, 'quick throw used the player\'s own ball'
    assert bag(g, sport, POCKET_BALLS) == before - 1
    g.shot('polish_contest_quick_ball.png')
    print(f'ok  contest quick-throw used a Sport Ball ({before} -> {before - 1}); own Poke Balls untouched', flush=True)


def cinnabar_open_sea():
    from test_region_walk import cross, current, setup
    g = setup()
    g.flag('FLAG_POX_TRIGGERS_ENABLED', True)
    g.flag('FLAG_POX_STORY_MANSION', False)
    g.test_water = True
    # x=12 is open water on both sides of the seam (Cinnabar's x=11 is a wall).
    g.warp('Route21_South_Frlg', 12, 47)
    g.frame(60)
    cross(g, 'S', 'CinnabarIsland_Frlg')
    assert current(g) == 'CinnabarIsland_Frlg', g.describe()
    g.shot('polish_route21_to_cinnabar.png')
    print('ok  Route 21 swims straight into Cinnabar before the Mansion (no current)', flush=True)


if __name__ == '__main__':
    static()
    pokemon_center()
    goldenrod_edges()
    contest_quick_ball()
    cinnabar_open_sea()
    print('PASS test_goldenrod_polish', flush=True)
