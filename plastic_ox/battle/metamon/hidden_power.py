#!/usr/bin/env python3
"""Production ROM Hidden Power UI and private-own-type observation checks.

Uses disposable emulator state only. Run with the mgba311 environment.
"""
import ctypes
import json
import re
import struct

from smoke import Game, ROOT, test_story, boot_new_game, begin_code, opcode
from verify import Observation
from walklib import K


def encoded(text):
    return bytes(0xA1 + int(c) if c.isdigit() else
                 0xD5 + ord(c) - ord('a') if c.islower() else
                 0xBB + ord(c) - ord('A') for c in text)


def displayed(g):
    return bytes(g.u8(g.syms['gDisplayedStringBattle'] + i) for i in range(256)).split(b'\xff', 1)[0]


def main():
    test_story.boot_test_game = boot_new_game
    g = Game()
    out = ROOT / 'plastic_ox/battle/metamon/build/hidden-power'
    out.mkdir(parents=True, exist_ok=True)
    names = ['FIGHTING', 'FLYING', 'POISON', 'GROUND', 'ROCK', 'BUG', 'GHOST', 'STEEL',
             'FIRE', 'WATER', 'GRASS', 'ELECTRIC', 'PSYCHIC', 'ICE', 'DRAGON', 'DARK']
    header = (ROOT / 'include/constants/pokemon.h').read_text()
    types = [int(re.search(r'\bTYPE_' + n + r'\s*=\s*(\d+)', header)[1]) for n in names]
    begin_code(g, opcode(g, 'callnative') + struct.pack('<I', g.syms['GivePlasticOxPlayerParty'] | 1)
               + opcode(g, 'setmonmove') + struct.pack('<BBH', 0, 0, 237)
               + opcode(g, 'releaseall') + opcode(g, 'end'))
    g.frame(60)
    field = g.core.save_raw_state()

    # Open real summary pages for a physical and a special Hidden Power.
    for idx in (0, 13):
        assert g.core.load_raw_state(field)
        g.write(g.syms['gSpecialVar_0x8004'], 0, 2)
        g.write(g.syms['gSpecialVar_Result'], types[idx], 2)
        begin_code(g, opcode(g, 'callnative') + struct.pack('<I', g.syms['SetTrainingKitHiddenPower'] | 1)
                   + opcode(g, 'end'))
        g.frame(40)
        g.write(g.syms['gMain'] + 4, g.syms['CB2_ShowPokemonSummaryScreen'] | 1, 4)
        g.frame(120)
        g.tap(K.KEY_RIGHT, wait=40)
        g.tap(K.KEY_RIGHT, wait=40)
        g.tap(K.KEY_A, wait=40)
        g.fb.to_pil().convert('RGB').save(str(out / f'summary-{names[idx].lower()}.png'))

    assert g.core.load_raw_state(field)
    g.write(g.syms['gSpecialVar_0x8004'], 0, 2)
    g.write(g.syms['gSpecialVar_Result'], types[13], 2)
    begin_code(g, opcode(g, 'callnative') + struct.pack('<I', g.syms['SetTrainingKitHiddenPower'] | 1)
               + opcode(g, 'end'))
    g.frame(40)
    g.warp('OldaleTown', 6, 17)
    g.begin('OldaleTown_EventScript_Lance')
    g.wait_action()
    if not g.u32(g.syms['gMetamonDecisions']):
        g.ready()
    layout = [g.u32(g.syms['gMetamonTestLayout'] + 4*i) for i in range(16)]
    state, stride, moves, pp = layout[2], layout[6], layout[7], layout[12]
    action_menu = g.core.save_raw_state()
    g.write(g.syms['gActionSelectionCursor'], 0)
    g.tap(K.KEY_A, hold=1, wait=45)
    assert g.controller('HandleInputChooseMove')
    assert encoded('Ice') in displayed(g), displayed(g).hex()
    g.fb.to_pil().convert('RGB').save(str(out / 'battle-type-ice.png'))
    g.tap(K.KEY_L, wait=40)
    assert encoded('70') in displayed(g)
    g.fb.to_pil().convert('RGB').save(str(out / 'battle-details-ice.png'))

    # Exercise every power bit pattern through the actual battle description.
    for bits in range(64):
        assert g.core.load_raw_state(action_menu)
        ivs = [2*((bits >> i) & 1) for i in range(6)]
        g.write(g.syms['gBattleMons'] + moves + 8, sum(iv << (5*i) for i, iv in enumerate(ivs)), 4)
        g.write(g.syms['gActionSelectionCursor'], 0)
        g.tap(K.KEY_A, hold=1, wait=45)
        assert encoded('Fighting') in displayed(g), displayed(g).hex()
        g.tap(K.KEY_L, wait=40)
        assert encoded(str(30 + 40*bits//63)) in displayed(g), bits
        if bits == 0:
            g.fb.to_pil().convert('RGB').save(str(out / 'battle-details-fighting-30.png'))

    base = g.u32(g.syms['sMetamon'])
    g.write(g.syms['gBattleMainFunc'], g.syms['BeginBattleIntroDummy'] | 1, 4)
    g.write(base + state, 0)
    g.write(g.syms['gBattlerControllerFuncs'] + 4, next(iter(g.functions['OpponentHandleChooseAction'])) | 1, 4)
    saved = g.core.save_raw_state()
    report = {}
    for idx, name in enumerate(names):
        assert g.core.load_raw_state(saved)
        own = g.syms['gBattleMons'] + stride
        bits = min(((idx + 1)*63 - 1)//15, 63)
        ivs = [30 + ((bits >> i) & 1) for i in range(6)]
        for i, move in enumerate((237, 85, 46, 97)):
            g.write(own + moves + 2*i, move, 2)
        # BattlePokemon packs its six IVs immediately after the four u16 moves.
        g.write(own + moves + 8, sum(iv << (5*i) for i, iv in enumerate(ivs)), 4)
        g.write(own + pp, 24)
        g.ready()
        assert not g.u32(g.syms['gMetamonFault'])
        raw = bytes(g.u8(base + i) for i in range(ctypes.sizeof(Observation)))
        obs = Observation.from_buffer_copy(raw)
        found = [j for j in range(4) if obs.move_cat[j*3] == 238]
        assert len(found) == 1, (list(obs.move_cat[:12]), stride, moves,
            [g.u16(own + moves + 2*i) for i in range(4)],
            [g.u8(g.syms['gBattlerPartyIndexes']+i) for i in range(2)])
        j = found[0]
        category = 2 if idx < 8 else 3
        assert obs.move_cat[j*3+1:j*3+3] == [idx+3, category], (name, list(obs.move_cat[:12]))
        assert obs.move_flags[j] & 24 == 24
        assert not obs.move_flags[j] & 2, 'Power must match the training unknown mask'
        report[name] = dict(type_token=idx+3, category=category, status='passed')
        print(name, 'PASS', flush=True)
    (out / 'results.json').write_text(json.dumps(dict(types=report, power_patterns=64), indent=2) + '\n')


if __name__ == '__main__':
    main()
