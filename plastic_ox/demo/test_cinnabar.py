#!/usr/bin/env python3
"""Cinnabar regression in mGBA; setup writes emulator RAM, never ROM/save files."""
import json
import struct
from pathlib import Path

from test_sudowoodo_v1 import (SudoGame, battle_mon, const, drain, give_item,
    in_battle, opcode, run_code, settle, talk, wait_for_battle, bag,
    POCKET_KEY_ITEMS, POCKET_BALLS, pocket, K, in_overworld, settle_overworld, fight)
import test_story
from test_single_player import boot_new_game

ROOT = Path(__file__).resolve().parents[2]
SHOTS = Path('/tmp/pox_cinnabar_shots')
KEY = const('ITEM_SECRET_KEY', 'items.h')
ENTEI = const('SPECIES_ENTEI', 'species.h')


class Game(SudoGame):
    def flag(self, name, value=None):
        flag = self.const(name)
        if 0xB00 <= flag < 0xB80:
            ptr = self.u32(self.syms['gSaveBlock3Ptr'])
            addr = ptr + self.sizes['gSaveblock3'] - 16 + (flag - 0xB00) // 8
            if value is not None:
                self.write(addr, (self.u8(addr) & ~(1 << (flag % 8))) | (bool(value) << (flag % 8)))
            return bool(self.u8(addr) & (1 << (flag % 8)))
        return super().flag(name, value)


def game():
    test_story.boot_test_game = boot_new_game
    g = Game()
    g.flag('FLAG_POX_TRIGGERS_ENABLED', True)
    run_code(g, opcode(g, 'callnative') + struct.pack('<I', g.syms['GivePlasticOxPlayerParty'] | 1)
             + opcode(g, 'releaseall'))
    for n in range(1, 9):
        g.flag(f'FLAG_BADGE{n:02}_GET', False)
    # Initialize virtual storage through the native flag implementation.
    run_code(g, opcode(g, 'setflag') + struct.pack('<H', 0xB7F)
             + opcode(g, 'clearflag') + struct.pack('<H', 0xB7F))
    give_item(g, const('ITEM_POKE_BALL', 'items.h'), 20)
    return g


def shot(g, name):
    SHOTS.mkdir(exist_ok=True)
    g.fb.to_pil().convert('RGB').save(SHOTS / (name + '.png'))


def at(g, name):
    groups = json.loads((ROOT / 'data/maps/map_groups.json').read_text())
    wanted = next((i, groups[n].index(name)) for i, n in enumerate(groups['group_order']) if name in groups[n])
    return (g.state()['group'], g.state()['num']) == wanted


def test_doors():
    g = game()
    g.warp('CinnabarIsland_Frlg', 8, 4)
    g.frame(120)
    g.hold(K.KEY_UP, 40)
    assert at(g, 'CinnabarIsland_Frlg'), g.state()
    shot(g, 'door_attempt')
    assert 'locked' in g.text(), (g.text(), g.state())
    shot(g, 'mansion_locked')
    settle(g)
    g.warp('CinnabarIsland_Frlg', 20, 5)
    g.frame(120)
    g.hold(K.KEY_UP, 60)
    g.frame(150)
    assert at(g, 'CinnabarIsland_Gym_Frlg'), g.state()
    shot(g, 'gym_open')
    g.flag('FLAG_BADGE04_GET', True)
    g.flag('FLAG_POX_STORY_FUJI', True)
    g.warp('CinnabarIsland_Gym_Frlg', 5, 5)
    g.frame(120)
    assert talk(g, K.KEY_UP)['battle']
    assert wait_for_battle(g)
    assert battle_mon(g, 1)['species'] == const('SPECIES_NINETALES', 'species.h')
    finish_trainer(g, True)
    assert g.u8(g.syms['gBattleOutcome']) == 1
    if not settle(g, 1200):
        pc = g.u32(g.syms['sGlobalScriptContext'] + 8)
        print('stuck', g.text(), hex(pc), sorted(((pc-a,n) for n,a in g.syms.items() if a<=pc), key=lambda x:x[0])[:8], flush=True)
        shot(g, 'reward_stuck')
        raise AssertionError('reward did not end')
    assert bag(g, KEY) == 1 and g.flag('FLAG_POX_MANSION_KEY'), (bag(g, KEY), g.flag('FLAG_POX_MANSION_KEY'), g.text(), g.u8(g.syms['sGlobalScriptContextStatus']))
    assert g.flag('FLAG_BADGE05_GET')
    g.warp('CinnabarIsland_Frlg', 8, 4)
    g.frame(120)
    g.hold(K.KEY_UP, 60)
    g.frame(150)
    assert at(g, 'PokemonMansion_1F_Frlg'), g.state()
    shot(g, 'mansion_open')
    g.hold(K.KEY_DOWN, 70)
    g.frame(150)
    assert at(g, 'CinnabarIsland_Frlg'), g.state()
    print('PASS: locked Mansion; open gym; Blaine reward; Mansion entry and exit', flush=True)
    return g


def test_puzzle(g):
    g.warp('PokemonMansion_1F_Frlg', 5, 6)
    g.frame(120)
    initial = g.flag('FLAG_POX_MANSION_SWITCH')
    tile = g.metatile_at(22, 10)
    assert talk(g, K.KEY_UP)['dialogue']
    assert g.flag('FLAG_POX_MANSION_SWITCH') != initial
    changed = g.metatile_at(22, 10)
    assert tile != changed
    g.warp('CinnabarIsland_Frlg', 8, 4)
    g.frame(120)
    g.warp('PokemonMansion_1F_Frlg', 5, 6)
    g.frame(120)
    assert g.metatile_at(22, 10) == changed
    assert talk(g, K.KEY_UP)['dialogue']
    assert g.flag('FLAG_POX_MANSION_SWITCH') == initial
    assert g.metatile_at(22, 10)[0] == tile[0], (tile, g.metatile_at(22, 10))
    shot(g, 'mansion_switch')
    print('PASS: statue toggles doors, persists across map reload, toggles back', flush=True)
    return g


def test_sage_start(g):
    g.warp('PokemonMansion_B1F_Frlg', 5, 9)
    g.frame(120)
    shot(g, 'sage_entei')
    g.warp('PokemonMansion_B1F_Frlg', 5, 8)
    g.frame(120)
    assert talk(g, K.KEY_UP)['battle']
    assert wait_for_battle(g)
    assert g.u32(g.syms['gBattleTypeFlags']) & 8
    assert not g.flag(0xB40)
    shot(g, 'sage_battle')
    print('PASS: Sage trainer battle starts; victory flag unset', battle_mon(g, 1), flush=True)
    return g



def finish_trainer(g, win):
    """Real battle outcomes, with HP/stats adjusted only to shorten the fixture."""
    lay = [g.u32(g.syms['gMetamonTestLayout'] + i * 4) for i in range(16)]
    stride = g.sizes['gParties'] // 24
    if not win:
        for i in range(1, 6):
            g.write(g.syms['gParties'] + i * stride + stride - 14, 0, 2)
    for i in range(20000):
        if in_overworld(g):
            g.frame(30)
            return
        if g.controller('HandleInputChooseAction'):
            g.write(g.syms['gActionSelectionCursor'], 0)
            base = g.syms['gBattleMons']
            if win:
                g.write(base + lay[6] + lay[10], 1, 2)
                for off in range(2, 12, 2):
                    g.write(base + off, 9999, 2)
                g.write(base + lay[7], const('MOVE_AERIAL_ACE', 'moves.h'), 2)
                g.write(base + lay[12], 30)
            else:
                g.write(base + lay[10], 1, 2)
                for off in range(2, 12, 2):
                    g.write(base + off, 1, 2)
                g.write(base + lay[7], const('MOVE_SPLASH', 'moves.h'), 2)
            g.tap(K.KEY_A, hold=1, wait=4)
        elif g.controller('HandleInputChooseMove'):
            g.write(g.syms['gMoveSelectionCursor'], 0)
            g.tap(K.KEY_A, hold=1, wait=4)
        else:
            g.tap(K.KEY_A, hold=1, wait=4)
    shot(g, 'trainer_timeout')
    raise AssertionError('Trainer battle did not finish')


def test_retry_and_win(g):
    start = g.core.save_raw_state()
    finish_trainer(g, False)
    assert g.u8(g.syms['gBattleOutcome']) == 2
    assert not g.flag(0xB40) and not g.flag('FLAG_POX_ENTEI')
    g.frame(600)
    assert settle_overworld(g) is not None
    g.frame(120)
    # The blackout's healing/warp has finished before retrying.
    g.warp('PokemonMansion_B1F_Frlg', 5, 8)
    g.frame(120)
    assert talk(g, K.KEY_UP)['battle']
    assert wait_for_battle(g)
    print('PASS: real trainer loss leaves Sage repeatable', flush=True)
    assert g.core.load_raw_state(start)
    finish_trainer(g, True)
    assert g.u8(g.syms['gBattleOutcome']) == 1
    assert g.flag(0xB40) and not g.flag('FLAG_POX_ENTEI')
    assert wait_for_battle(g)
    assert g.u32(g.syms['gBattleTypeFlags']) & (1 << 14)
    assert battle_mon(g, 1)['species'] == ENTEI
    shot(g, 'entei_reward')
    print('PASS: real six-Pokemon trainer victory unlocks Entei reward battle', flush=True)
    return g


def test_catch(g):
    reward = g.core.save_raw_state()
    fight(g, 'run')
    assert drain(g)
    assert g.u8(g.syms['gBattleOutcome']) == 4
    assert not g.flag('FLAG_POX_ENTEI') and g.flag(0xB40)
    # Interact with Entei itself, then decline at the actual yes/no menu.
    g.warp('PokemonMansion_B1F_Frlg', 6, 8)
    g.frame(120)
    g.tap(K.KEY_UP, hold=2, wait=16)
    for _ in range(300):
        if g.task('Task_HandleYesNoInput'):
            break
        g.tap(K.KEY_A, hold=1, wait=6)
    assert g.task('Task_HandleYesNoInput')
    g.frame(30)
    g.tap(K.KEY_B, hold=2, wait=30)
    assert drain(g)
    assert not in_battle(g) and not g.flag('FLAG_POX_ENTEI')
    save_reload(g)
    assert at(g, 'PokemonMansion_B1F_Frlg')
    assert g.flag(0xB40) and not g.flag('FLAG_POX_ENTEI')
    assert talk(g, K.KEY_UP)['battle']
    assert wait_for_battle(g)
    assert not (g.u32(g.syms['gBattleTypeFlags']) & 8)
    assert g.u32(g.syms['gBattleTypeFlags']) & (1 << 14)
    assert battle_mon(g, 1)['species'] == ENTEI
    print('PASS: fleeing, declining and save/Continue preserve unclaimed reward; Entei interaction skips Sage rematch', flush=True)
    assert g.core.load_raw_state(reward)
    finish_trainer(g, True)  # Deliberately KO the reward instead of catching it.
    assert g.u8(g.syms['gBattleOutcome']) == 1
    assert drain(g)
    assert not g.flag('FLAG_POX_ENTEI') and g.flag(0xB40)
    assert talk(g, K.KEY_UP)['battle']
    assert wait_for_battle(g)
    assert not (g.u32(g.syms['gBattleTypeFlags']) & 8)
    assert battle_mon(g, 1)['species'] == ENTEI
    print('PASS: reward KO preserves Entei and skips the defeated Sage on retry', flush=True)
    for name in ['ITEM_POKE_BALL', 'ITEM_PREMIER_BALL', 'ITEM_ULTRA_BALL']:
        assert g.core.load_raw_state(reward)
        item = const(name, 'items.h')
        slots, capacity = pocket(g, POCKET_BALLS)
        g.write(slots, item, 2)  # Keep encrypted count; vary only the first ball.
        before = bag(g, item, POCKET_BALLS)
        assert battle_mon(g, 1)['hp'] == battle_mon(g, 1)['maxhp']
        g.write(g.syms['gActionSelectionCursor'], 1)
        g.tap(K.KEY_A, hold=1, wait=60)
        g.write(g.syms['gBagPosition'] + 5, POCKET_BALLS)
        g.write(g.syms['gBagPosition'] + 8 + 2 * POCKET_BALLS, 0)
        g.frame(60)
        for _ in range(20):
            g.tap(K.KEY_A, hold=2, wait=30)
            if bag(g, item, POCKET_BALLS) < before:
                break
        assert bag(g, item, POCKET_BALLS) == before - 1
        for _ in range(2000):
            if in_overworld(g) and g.flag('FLAG_POX_ENTEI'):
                break
            g.tap(K.KEY_B, hold=2, wait=10)
        assert g.u8(g.syms['gBattleOutcome']) == 7
        assert g.flag('FLAG_POX_ENTEI') and g.flag(0xB40)
        assert drain(g)
        stride = g.sizes['gParties'] // 24
        storage = g.u32(g.syms['gPokemonStoragePtr'])
        assert any(g.box_species(storage + 4 + (stride - 20) * i) == ENTEI for i in range(30))
        g.warp('PokemonMansion_1F_Frlg', 8, 31)
        g.frame(60)
        g.warp('PokemonMansion_B1F_Frlg', 5, 8)
        g.frame(120)
        shot(g, 'caught_' + name)
        stride_obj = g.sizes['gObjectEvents'] // 16
        live_ids = {g.u8(g.syms['gObjectEvents'] + i * stride_obj + 8)
                    for i in range(16) if g.u8(g.syms['gObjectEvents'] + i * stride_obj) & 1}
        assert 6 not in live_ids and 7 not in live_ids, live_ids
        assert not talk(g, K.KEY_UP)['battle']
        print('PASS: first ' + name + ' catches full-HP Entei; boxed with full party; persistent removal', flush=True)
    return g


def save_reload(g):
    # Save through the game's own save routine, then reset and Continue.
    from test_qol import begin_code
    begin_code(g, opcode(g, 'callnative') + struct.pack('<I', g.syms['Script_ForceSaveGame'] | 1)
               + opcode(g, 'waitstate') + opcode(g, 'releaseall') + opcode(g, 'end'))
    assert settle(g, 2000)
    g.core.reset()
    for _ in range(300):
        g.tap(K.KEY_A, hold=2, wait=20)
        if in_overworld(g):
            break
    g.frame(180)


def test_save_reload(g):
    g.warp('PokemonMansion_1F_Frlg', 5, 6)
    g.frame(120)
    assert talk(g, K.KEY_UP)['dialogue']
    assert g.flag('FLAG_POX_MANSION_SWITCH')
    save_reload(g)
    assert at(g, 'PokemonMansion_1F_Frlg')
    assert g.flag('FLAG_POX_MANSION_SWITCH') and g.flag('FLAG_POX_ENTEI') and g.flag(0xB40)
    assert bag(g, KEY) == 1
    g.warp('PokemonMansion_B1F_Frlg', 5, 8)
    g.frame(120)
    assert not talk(g, K.KEY_UP)['battle']
    shot(g, 'after_save_reload')
    # The reward marker must never carry into unrelated scripted encounters.
    run_code(g, opcode(g, 'setwildbattle') + struct.pack('<HBHHBH', const('SPECIES_RATTATA', 'species.h'), 5, 0, 0, 0, 0)
             + opcode(g, 'dowildbattle'), frames=1)
    assert wait_for_battle(g)
    assert not (g.u32(g.syms['gBattleTypeFlags']) & (1 << 14))
    print('PASS: native save/reset/Continue preserves key, Sage win, capture and puzzle; normal battles have no catch guarantee', flush=True)


if __name__ == '__main__':
    test_save_reload(test_catch(test_retry_and_win(test_sage_start(test_puzzle(test_doors())))))
