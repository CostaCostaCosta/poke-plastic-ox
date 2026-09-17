#!/usr/bin/env python3
"""Headless single-player/link regression checks; uses emulator-only save data."""
import struct
import test_story
from test_qol import opcode, begin_code
from walklib import K


def boot_new_game(g):
    # Skip naming/intro UI for the fixture, using normal new-game initialization.
    g.frame(120)
    print('Title booted; initializing fixture', flush=True)
    g.write(g.syms['gMain'] + 0x438, 0)
    g.write(g.syms['gMain'] + 4, g.syms['CB2_NewGame'] | 1, 4)
    g.frame(360)
    print('New-game fixture ready', flush=True)
    assert g.u32(g.syms['gMain'] + 4) & ~1 == g.syms['CB2_Overworld'] & ~1


def assert_offline(g):
    for name in ('gWirelessCommType', 'gReceivedRemoteLinkPlayers', 'gLinkTransferringData'):
        assert g.u8(g.syms[name]) == 0, name
    task_funcs = {g.u32(g.syms['gTasks'] + i * 40) & ~1 for i in range(16)
                  if g.u8(g.syms['gTasks'] + i * 40 + 4)}
    for name in ('Task_InitUnionRoom', 'Task_RunUnionRoom'):
        if name in g.syms:
            assert g.syms[name] & ~1 not in task_funcs, name


def travel(g, speed):
    g.setvar(0x40FE, speed)
    g.warp('OldaleTown_PokemonCenter_1F', 3, 6)
    assert_offline(g)
    x = g.state()['x']
    g.hold(K.KEY_RIGHT, 32)
    distance = g.state()['x'] - x
    g.frame(60)
    return distance


def main():
    test_story.boot_test_game = boot_new_game
    g = test_story.StoryGame(build='')
    assert_offline(g)
    baseline, fast = travel(g, 0), travel(g, 1)
    assert fast > baseline, (baseline, fast)
    print(f'Center movement in 32 frames: 1x={baseline}, 2x={fast}', flush=True)

    begin_code(g, opcode(g, 'callnative')
               + struct.pack('<I', g.syms['GivePlasticOxPlayerParty'] | 1)
               + opcode(g, 'releaseall') + opcode(g, 'end'))
    g.frame(60)
    assert g.count() > 0
    g.warp('OldaleTown_PokemonCenter_1F', 7, 4)
    g.run('OldaleTown_PokemonCenter_1F_EventScript_Nurse')
    assert_offline(g)
    assert travel(g, 1) > baseline
    print('Nurse healing completes and 2x remains active', flush=True)

    # Save inside the Center through the game's save dialog, then reset the GBA.
    begin_code(g, opcode(g, 'callnative')
               + struct.pack('<I', g.syms['Script_ForceSaveGame'] | 1)
               + opcode(g, 'waitstate') + opcode(g, 'releaseall') + opcode(g, 'end'))
    for _ in range(180):
        g.tap(K.KEY_A, hold=2, wait=10)
        if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            break
    else:
        raise AssertionError('save dialog did not finish')
    saved = g.state()
    g.core.reset()
    for _ in range(180):
        g.tap(K.KEY_A, hold=2, wait=20)
        if g.u32(g.syms['gMain'] + 4) & ~1 == g.syms['CB2_Overworld'] & ~1:
            break
    else:
        raise AssertionError('Continue did not reach overworld')
    g.frame(180)
    assert (g.state()['group'], g.state()['num']) == (saved['group'], saved['num'])
    assert g.var(0x40FE) == 1
    assert_offline(g)
    x = g.state()['x']
    g.hold(K.KEY_LEFT, 32)
    assert x - g.state()['x'] > baseline
    g.frame(60)
    print('Save/reset/Continue preserves working 2x movement in Center', flush=True)

    # Exercise attendants included in this region (unused FRLG maps are pruned).
    checked = 0
    for suffix in ('', '_Frlg'):
        for service in ('TradeCenter', 'Colosseum', 'RecordCorner', 'UnionRoomAttendant',
                        'WirelessClubAttendant', 'DirectCornerAttendant'):
            name = 'CableClub_EventScript_' + service + suffix
            if name not in g.syms:
                continue
            g.run(name)
            assert_offline(g)
            checked += 1
    assert checked >= 6
    print(f'{checked} cable/wireless attendants exit without starting connections', flush=True)
    for name in ('BerryBlender_EventScript_BerryBlenderLink',
                 'LilycoveCity_ContestLobby_EventScript_LinkContestReceptionist',
                 'BattleFrontier_BattleTowerLobby_EventScript_LinkMultisAttendant',
                 'MossdeepCity_GameCorner_1F_EventScript_OldMan2'):
        if name in g.syms:
            g.run(name)
            assert_offline(g)
    g.warp('OldaleTown', 6, 17)
    g.hold(K.KEY_UP, 32)
    g.frame(180)
    assert (g.state()['group'], g.state()['num']) == (saved['group'], saved['num'])
    assert_offline(g)
    g.warp('OldaleTown_PokemonCenter_1F', 7, 7)
    g.hold(K.KEY_DOWN, 48)
    g.frame(180)
    assert g.state()['group'] == 0 and g.state()['num'] == 10
    assert_offline(g)
    print('Animated Center door entry/exit remain offline', flush=True)
    g.warp('PalletTown_Frlg', 12, 18)
    assert_offline(g)
    assert g.var(0x40FE) == 1
    print('SINGLE-PLAYER CHECKS PASSED', flush=True)


if __name__ == '__main__':
    main()
