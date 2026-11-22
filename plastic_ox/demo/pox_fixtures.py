#!/usr/bin/env python3
"""Shared mGBA fixtures (formerly in test_cinnabar.py): RAM-only setup helpers.

Game: SudoGame plus virtual Sage flags (0xB00..0xB7F) in save block 3.
game(): fresh new-game boot with the Plastic Ox party and 20 Poke Balls.
finish_trainer(g, win): drive a real trainer battle to a win or a loss.
save_reload(g): save through the game's own routine, reset, Continue.
"""
import json
import struct
from pathlib import Path

from test_sudowoodo_v1 import (SudoGame, const, give_item, opcode, run_code,
    settle, K, in_overworld)
import test_story
from test_single_player import boot_new_game

ROOT = Path(__file__).resolve().parents[2]
SHOTS = Path('/tmp/pox_fixture_shots')


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
