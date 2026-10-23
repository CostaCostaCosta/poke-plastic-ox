#!/usr/bin/env python3
"""Exercise the real Johto doors, Cut seam, and weekly contest in mGBA."""
import json
import re
import struct
import sys

from test_story import ROOT, StoryGame
from walk_leg1 import enter_warp, find_path_elev, navigate
from walklib import K

sys.path.insert(0, str(ROOT / 'plastic_ox/alpha'))
from region_geometry import Geometry

R35, R36, PARK, GATE = 'Route35_hns', 'Route36_hns', 'NationalPark_Normal_hns', 'Gate_NationalPark_hns'
groups = json.loads((ROOT / 'data/maps/map_groups.json').read_text())
IDS = {name: (i, j) for i, group in enumerate(groups['group_order'])
       for j, name in enumerate(groups[group])}


def call(g, name):
    """Invoke actual native engine code through the field script interpreter."""
    ptr = g.syms['gStringVar4']
    code = bytes([0x23]) + struct.pack('<I', g.syms[name] | 1) + bytes([0x6C, 2])
    for i, b in enumerate(code):
        g.write(ptr + i, b)
    g.run(ptr)
    return g.u16(g.syms['gSpecialVar_Result'])


def finish_dialogue(g):
    for _ in range(500):
        g.tap(K.KEY_A, hold=2, wait=10)
        if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            g.frame(90)
            return
    raise AssertionError(('dialogue stuck', g.describe()))


def load_ok(g, name, tag):
    assert (g.state()['group'], g.state()['num']) == IDS[name], (tag, g.describe())
    g.wait_warp_complete(IDS[name])
    assert g.collision_at(g.state()['x'], g.state()['y'])[0] == 0, (tag, 'solid landing')
    g.frame(120)
    g.shot('national_park_' + tag + '.png')


def gates():
    g = StoryGame(spawn=(R35, 17, 8))
    # This leg isolates doors and paths; battle coverage lives in test_johto_outdoors.
    from test_qol import opcode
    from test_training_kit import run_code
    for trainer in ('TRAINER_PLASTIC_OX_PU_PARK', 'TRAINER_PLASTIC_OX_JOHTO_BEVERLY',
                    'TRAINER_PLASTIC_OX_JOHTO_JACK', 'TRAINER_PLASTIC_OX_JOHTO_KRISE'):
        run_code(g, opcode(g, 'settrainerflag') + struct.pack('<H', g.const(trainer)))
    # Both visible outdoor door tiles must enter the south gate.
    for lane in (17, 18):
        g.warp(R35, lane, 6)
        enter_warp(g, (lane, 6), 'UP', IDS[GATE], 'Route 35 gate')
        load_ok(g, GATE, f'south_gate_lane_{lane}')
        assert (g.state()['x'], g.state()['y']) == (7, 13)
        enter_warp(g, (7, 2), 'UP', IDS[PARK], 'south gate to park')
        load_ok(g, PARK, 'south_park_arrival')
        navigate(g, (26, 30))
        load_ok(g, PARK, 'park_grounds')
        enter_warp(g, (39, 19), 'RIGHT', IDS[GATE], 'park east exit')
        load_ok(g, GATE, 'east_gate_arrival')
        enter_warp(g, (47, 7), 'RIGHT', IDS[R36], 'east gate to Route 36')
        load_ok(g, R36, 'route36_arrival')
        enter_warp(g, (17, 20), 'LEFT', IDS[GATE], 'Route 36 gate')
        enter_warp(g, (35, 7), 'LEFT', IDS[PARK], 'east gate to park')
        load_ok(g, PARK, 'east_park_arrival')
        # Every lane of the four-tile south exit is usable.
        for exit_lane in (11, 12, 13, 14):
            enter_warp(g, (exit_lane, 48), 'DOWN', IDS[GATE], 'park south exit')
            load_ok(g, GATE, f'park_south_lane_{exit_lane}')
            if exit_lane != 14:
                enter_warp(g, (7, 2), 'UP', IDS[PARK], 'south gate return')
        enter_warp(g, (7, 12), 'DOWN', IDS[R35], 'gate to Route 35')
        load_ok(g, R35, 'route35_return')
    print('All gate doors and park exit lanes, park traversal, both directions PASS', flush=True)


def shortcut():
    geom = Geometry(R35)
    assert (31, 0) not in geom.component((17, 8), blocked={(31, 6)})
    assert (31, 0) in geom.component((17, 8))
    g = StoryGame(spawn=(R35, 31, 7))
    g.tap(K.KEY_UP, hold=18, wait=30)
    assert (g.state()['x'], g.state()['y']) == (31, 7), 'uncut tree did not block'
    # Give the game's reusable Cut tool, then interact with the real object.
    item = int(re.search(r'ITEM_CUT_KEY\s*=\s*(\d+)',
                         (ROOT / 'include/constants/items.h').read_text())[1])
    ptr = g.syms['gStringVar4']
    code = bytes([0x44]) + struct.pack('<HH', item, 1) + bytes([0x6C, 2])
    for i, b in enumerate(code):
        g.write(ptr + i, b)
    g.run(ptr)
    g.tap(K.KEY_A, wait=30)
    finish_dialogue(g)
    navigate(g, (31, 0))
    g.hold(K.KEY_UP, 20)
    load_ok(g, R36, 'cut_shortcut_north')
    assert g.state()['x'] == 15
    g.hold(K.KEY_DOWN, 30)
    load_ok(g, R35, 'cut_shortcut_south')
    navigate(g, (31, 5))
    g.tap(K.KEY_DOWN, hold=18, wait=30)
    assert (g.state()['x'], g.state()['y']) == (31, 5), 'tree should respawn after returning'
    print('Cut tree blocks, actual Cut opens Route 35/36 seam, return and tree respawn PASS', flush=True)


def set_weekday(g, day):
    g.write(g.syms['gSpecialVar_Result'], day, 2)
    call(g, 'Special_SetPocketWatchWeekday')
    assert call(g, 'PoxGetDayOfWeek') == day


def gate_crowds():
    g = StoryGame(spawn=(GATE, 7, 4))
    g.flag('FLAG_SYS_CLOCK_SET', True)
    objects = json.loads((ROOT / f'data/maps/{GATE}/map.json').read_text())['object_events']
    stride = g.sizes['gObjectEvents'] // 16

    def visible_objects():
        result = {}
        for i in range(16):
            ptr = g.syms['gObjectEvents'] + i * stride
            if not g.u8(ptr) & 1 or g.u8(ptr + 2) & 1 or g.u8(ptr + 1) & 0x20:
                continue
            if (g.u8(ptr + 10), g.u8(ptr + 9)) != IDS[GATE]:
                continue
            result[g.u8(ptr + 8)] = (g.s16(ptr + 16) - 7, g.s16(ptr + 18) - 7)
        return result

    for day in range(7):
        set_weekday(g, day)
        contest_day = day in (2, 4, 6)
        # A completed daily entry must not hide the scheduled-day crowd.
        g.flag('FLAG_POX_DAILY_PARK_CONTEST', contest_day)
        for side, x, y in [('south', 7, 4), ('east', 38, 7)]:
            g.warp(GATE, x, y)
            g.frame(120)
            assert g.flag('FLAG_POX_HIDE_PARK_CONTEST_CROWD') == (not contest_day), day
            expected = {i + 1: (obj['x'], obj['y']) for i, obj in enumerate(objects)
                        if (obj['x'] < 25) == (side == 'south')
                        and (obj['flag'] == '0' or contest_day)}
            visible = visible_objects()
            assert visible == expected, (day, side, expected, visible)
            assert len(visible) == (6 if contest_day else 2), (day, side, visible)
            for pos in visible.values():
                assert g.collision_at(*pos)[0] == 0, ('NPC on solid tile', day, side, pos)
            if day in (1, 2):
                g.shot(f'national_park_{side}_crowd_' + ('contest.png' if contest_day else 'quiet.png'))
    print('Both gates: actual NPC crowds on all seven weekdays, clear floor positions, crowd retained after daily entry PASS', flush=True)


def contest():
    g = StoryGame(spawn=(GATE, 7, 10))
    g.run('Pox_Cyndaquil')
    g.flag('FLAG_SYS_CLOCK_SET', True)
    # Check the real RTC schedule without bypassing the day check.
    for day in range(7):
        set_weekday(g, day)
        assert call(g, 'PlasticOxContest_CheckEntry') == (0 if day in (2, 4, 6) else 1), day
    print('RTC: contest open Tue/Thu/Sat and closed Sun/Mon/Wed/Fri PASS', flush=True)
    for side, attendant, spawn in [(0, 'South', (3, 3)), (1, 'East', (38, 3))]:
        set_weekday(g, 2 if side == 0 else 4)
        g.warp(GATE, *spawn)
        original_count = g.count()
        original_species = g.party_species()
        g.tap(K.KEY_UP, hold=2, wait=12)
        g.tap(K.KEY_A, hold=2, wait=30)
        assert g.u8(g.syms['sGlobalScriptContextStatus']) != 2, 'attendant did not respond'
        # A accepts the offer and selects the first healthy party Pokemon.
        finish_dialogue(g)
        load_ok(g, PARK, f'contest_{attendant.lower()}_entry')
        assert g.u8(g.syms['sRunning']) and g.count() == 1
        assert g.u8(g.syms['gNumSafariBalls']) == 20
        assert g.flag('FLAG_POX_DAILY_PARK_CONTEST')
        # Retain a specimen through the actual catch/staging code, then exit.
        # Seed the catch boundary with a Pokemon; catch battle coverage is
        # separate from these map-exit and party-restoration assertions.
        stride = g.sizes['gParties'] // 24
        for i in range(stride):
            g.write(g.syms['sCandidate'] + i, g.u8(g.syms['gParties'] + i))
        g.write(g.syms['sNewCatch'], 1)
        g.write(g.syms['gSpecialVar_0x8004'], 1, 2)
        call(g, 'PlasticOxContest_AcceptCatch')
        assert g.u8(g.syms['sHasCatch'])
        approach, direction = ((12, 48), 'DOWN') if side == 0 else ((39, 19), 'RIGHT')
        enter_warp(g, approach, direction, IDS[GATE], 'contest exit to judging')
        finish_dialogue(g)
        load_ok(g, GATE, f'contest_{attendant.lower()}_results')
        assert not g.u8(g.syms['sRunning']) and not g.u8(g.syms['sPartyReduced'])
        assert g.count() == original_count + 1 and g.party_species() == original_species
        assert not g.u8(g.syms['sHasCatch'])
        assert call(g, 'PlasticOxContest_CheckEntry') == 2, 'same-day reentry allowed'
        for flag in ('FLAG_POX_CONTEST_PRIZE_PENDING', 'FLAG_POX_CONTEST_EVERSTONE_PENDING',
                     'FLAG_POX_CONTEST_SITRUS_PENDING', 'FLAG_POX_CONTEST_ORAN_PENDING'):
            assert not g.flag(flag), ('unclaimed prize', flag)
    print('Both gate attendants: registration, park entry, catch retained, exit judging, party restored, prizes, daily limit/reset PASS', flush=True)


def endings():
    for side, tag in [(0, 'timeout'), (1, 'retire')]:
        g = StoryGame(spawn=(GATE, 7, 10))
        g.run('Pox_Cyndaquil')
        g.flag('FLAG_SYS_CLOCK_SET', True)
        set_weekday(g, 2)
        g.write(g.syms['gSpecialVar_0x8007'], side, 2)
        g.write(g.syms['gSpecialVar_0x8004'], 0, 2)
        assert call(g, 'PlasticOxContest_Start') == 0
        g.run('PlasticOxContest_EventScript_EnterPark')
        if side == 0:
            g.write(g.syms['gSafariZoneStepCounter'], 1, 2)
            g.tap(K.KEY_RIGHT, hold=18, wait=180)
        else:
            g.run('PlasticOxContest_EventScript_Finish')
        finish_dialogue(g)
        load_ok(g, GATE, tag)
        assert not g.u8(g.syms['sRunning']) and not g.u8(g.syms['sPartyReduced'])
        assert g.count() == 1 and not g.flag('FLAG_POX_CONTEST_ORAN_PENDING')
        assert g.state()['x'] == (7 if side == 0 else 35), 'wrong return gate'
    print('Step expiry and retirement return to entry gate, restore party, judge and award participation prize PASS', flush=True)


def actual_catch():
    from test_sudowoodo_v1 import (SudoGame, in_battle, in_overworld, wait_for_battle,
                                  battle_mon, bag, POCKET_BALLS)
    g = SudoGame()
    g.warp(GATE, 3, 3)
    call(g, 'GivePlasticOxPlayerParty')
    original = [g.party_species(i) for i in range(g.count())]
    g.flag('FLAG_SYS_CLOCK_SET', True)
    set_weekday(g, 2)
    g.begin('Gate_NationalPark_EventScript_SouthAttendant')
    finish_dialogue(g)
    navigate(g, (26, 30))
    g.write(g.syms['sWildEncountersDisabled'], 0)
    for i in range(100):
        g.tap(K.KEY_RIGHT if i % 2 else K.KEY_LEFT, hold=18, wait=8)
        if in_battle(g):
            break
    assert wait_for_battle(g), 'no contest encounter'
    g.write(g.syms['sWildEncountersDisabled'], 1)
    species = battle_mon(g, 1)['species']
    assert species in (10, 13, 11, 14, 46, 48, 12, 15, 313, 314), species
    assert not g.u32(g.syms['gBattleTypeFlags']) & (1 << 7), 'Safari battle lacks Pokemon combat'
    assert bag(g, 24, POCKET_BALLS) == 20
    g.shot('national_park_contest_actual_battle.png')
    for turn in range(20):
        assert wait_for_battle(g)
        # Lower the wild bug's battle HP and put it to sleep for the fixture.
        # The Sport Ball, battle result, and catch callback run unmodified.
        layout = [g.u32(g.syms['gMetamonTestLayout'] + i * 4) for i in range(16)]
        g.write(g.syms['gBattleMons'] + layout[6] + layout[10], 1, 2)
        g.write(g.syms['gBattleMons'] + layout[6] + layout[14], 3, 4)
        g.write(g.syms['gBagPosition'] + 5, 1)
        g.write(g.syms['gBagPosition'] + 10, 0, 2)
        g.write(g.syms['gBagPosition'] + 20, 0, 2)
        before = g.u8(g.syms['gNumSafariBalls'])
        g.write(g.syms['gActionSelectionCursor'], 1)
        g.tap(K.KEY_A, hold=2, wait=90)
        slots = g.u32(g.syms['gBagPockets'] + g.sizes['gBagPockets'] // 5)
        idx = [g.u16(slots + 4 * i) for i in range(64)].index(24)
        for _ in range(idx):
            g.tap(K.KEY_DOWN, hold=2, wait=12)
        for _ in range(20):
            g.tap(K.KEY_A, hold=2, wait=18)
            if g.u8(g.syms['gNumSafariBalls']) < before:
                break
        assert g.u8(g.syms['gNumSafariBalls']) == before - 1
        for _ in range(1600):
            g.tap(K.KEY_A, hold=1, wait=4)
            if in_overworld(g) or (in_battle(g) and g.controller('HandleInputChooseAction')):
                break
        if in_overworld(g):
            break
    assert g.u8(g.syms['gBattleOutcome']) == 7, 'no catch'
    g.frame(180)
    pos = (g.state()['x'], g.state()['y'])
    path = find_path_elev(g, lambda x, y, _w, _h: abs(x - pos[0]) + abs(y - pos[1]) == 1)
    assert path and len(path) >= 2, 'no free post-battle step'
    direction = {(0, -1): K.KEY_UP, (0, 1): K.KEY_DOWN,
                 (-1, 0): K.KEY_LEFT, (1, 0): K.KEY_RIGHT}
    dx, dy = path[1][0] - pos[0], path[1][1] - pos[1]
    g.tap(direction[dx, dy], hold=18, wait=45)
    finish_dialogue(g)
    assert g.u8(g.syms['sHasCatch']) and g.box_species(g.syms['sRetained']) == species
    g.run('PlasticOxContest_EventScript_Finish')
    finish_dialogue(g)
    load_ok(g, GATE, 'actual_catch_results')
    assert g.count() == 6 and [g.party_species(i) for i in range(6)] == original
    # The party was full, so the catch must arrive in the PC's first box slot.
    assert g.box_species(g.u32(g.syms['gPokemonStoragePtr']) + 4) == species
    assert bag(g, 24, POCKET_BALLS) == 0, 'loaned Sport Balls remained'
    print('Real grass bug battle, Sport Ball consumption, catch callback, gate judging, six original Pokemon restored, catch in PC PASS', flush=True)


if __name__ == '__main__':
    gate_crowds()
    gates()
    shortcut()
    contest()
    endings()
    actual_catch()
