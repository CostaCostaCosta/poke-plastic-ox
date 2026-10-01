#!/usr/bin/env python3
"""Exercise normal ROM battle cleanup with injected end-of-battle party damage.

The fixture starts a real trainer battle so the engine captures held items, then
simulates consumption/exchange and dispatches the normal battle finish handler.
"""
import json
import struct

from test_story import StoryGame, ROOT
from test_training_kit import run_code
from test_qol import opcode
from walklib import K


def secure(g, mon, edit=None):
    size = g.sizes['gParties'] // 24 - 52
    key = g.u32(mon) ^ g.u32(mon + 4)
    data = bytearray().join(struct.pack('<I', g.u32(mon + 32 + i) ^ key)
                            for i in range(0, size, 4))
    offsets = [g.u8(g.syms['sSubstructOffsets'] + s * 24 + g.u32(mon) % 24)
               * (size // 4) for s in range(4)]
    if edit:
        edit(data, offsets)
        for i in range(0, size, 4):
            g.write(mon + 32 + i, struct.unpack_from('<I', data, i)[0] ^ key, 4)
        g.write(mon + 28, sum(struct.unpack('<' + 'H' * (size // 2), data)) & 65535, 2)
    return data, offsets


def item(g, mon, value=None):
    def edit(data, offsets):
        word = struct.unpack_from('<H', data, offsets[0] + 2)[0]
        struct.pack_into('<H', data, offsets[0] + 2, (word & ~1023) | value)
    data, offsets = secure(g, mon, edit if value is not None else None)
    return struct.unpack_from('<H', data, offsets[0] + 2)[0] & 1023


def check(outcome, trainer=True):
    g = StoryGame()
    stride = g.sizes['gParties'] // 24
    mons = [g.symbol_address('gParties') + i * stride for i in range(3)]
    original = [520, 472, 0]  # Oran Berry, Leftovers, empty slot.
    for mon, held in zip(mons, original):
        run_code(g, opcode(g, 'callnative') + struct.pack('<I', g.syms['ScrCmd_createmon'] | 1)
                 + struct.pack('<BBHHI', 0, 6, 19, 5, 0))
        item(g, mon, held)
    pp_before = []
    for mon in mons:
        data, offsets = secure(g, mon)
        pp_before.append(bytes(data[offsets[1] + 8:offsets[1] + 12]))
    g.flag('FLAG_POX_STORY_STARTER', True)
    g.flag('FLAG_POX_STORY_ILEX', True)
    objects = json.loads((ROOT / 'data/maps/RustboroCity_Gym/map.json').read_text())['object_events']
    obj = next(o for o in objects if o['script'] == 'Pox_Roxanne')
    g.warp('RustboroCity_Gym', obj['x'], obj['y'] + 1)
    g.tap(K.KEY_UP, hold=2, wait=12)
    for _ in range(300):
        g.tap(K.KEY_A, hold=2, wait=10)
        if g.u32(g.syms['gBattleTypeFlags']) & 8:
            break
    else:
        raise AssertionError('Trainer battle did not start')
    g.frame(240)
    # Consumed berry, removed item, and an acquired item on an originally empty slot.
    for i, mon in enumerate(mons):
        item(g, mon, [0, 0, 523][i])
        g.write(mon + stride - 20, 8, 4)  # Poison.
        g.write(mon + stride - 14, 1 if i == 0 else 0, 2)
        def drain(data, offsets):
            data[offsets[1] + 8:offsets[1] + 12] = bytes(4)
        secure(g, mon, drain)
    if not trainer:
        g.write(g.syms['gBattleTypeFlags'], 0, 4)
    g.write(g.syms['gBattleOutcome'], outcome)
    g.write(g.syms['gCurrentActionFuncId'], 11)
    g.write(g.syms['gBattleMainFunc'], g.syms['HandleEndTurn_FinishBattle'] | 1, 4)
    g.frame(240)
    for i, mon in enumerate(mons):
        assert g.box_species(mon) == 19
        data, offsets = secure(g, mon)
        if trainer:
            assert item(g, mon) == original[i], (i, item(g, mon))
            assert g.u16(mon + stride - 14) == g.u16(mon + stride - 12)
            assert g.u32(mon + stride - 20) == 0
            assert bytes(data[offsets[1] + 8:offsets[1] + 12]) == pp_before[i]
        else:
            assert item(g, mon) == [0, 0, 523][i]
            assert g.u16(mon + stride - 14) == (1 if i == 0 else 0)
            assert g.u32(mon + stride - 20) == 8
    print(f'Trainer={trainer}, outcome={outcome}: held items, HP, status, PP PASS', flush=True)


if __name__ == '__main__':
    check(1)
    check(2)
    check(1, trainer=False)
