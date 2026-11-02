#!/usr/bin/env python3
"""Training Kit regression checks against the ordinary (non-TESTING) ROM.

Uses the real field script/native handlers and reads emulator RAM only.
"""
import re
import struct

from test_story import StoryGame, ROOT
from test_qol import opcode, begin_code


def run_code(g, code):
    begin_code(g, code + opcode(g, 'end'))
    g.frame(30)
    assert g.u8(g.syms['sGlobalScriptContextStatus']) == 2


def native(g, name):
    run_code(g, opcode(g, 'callnative') + struct.pack('<I', g.syms[name] | 1))


def evs(g, mon):
    stride = g.sizes['gParties'] // 24
    pid, ot = g.u32(mon), g.u32(mon + 4)
    offset = g.u8(g.syms['sSubstructOffsets'] + 2 * 24 + pid % 24)
    addr = mon + 32 + ((stride - 52) // 4) * offset
    data = b''.join(struct.pack('<I', g.u32(addr + i) ^ pid ^ ot) for i in (0, 4))
    return list(data[:6])


def ability_num(g, mon):
    stride = g.sizes['gParties'] // 24
    pid, ot = g.u32(mon), g.u32(mon + 4)
    offset = g.u8(g.syms['sSubstructOffsets'] + 3 * 24 + pid % 24)
    addr = mon + 32 + ((stride - 52) // 4) * offset
    flags = g.u32(addr + 8) ^ pid ^ ot
    return (flags >> 29) & 3


def main():
    g = StoryGame()
    # Create a fixture without relying on the story's starter dialogue.
    run_code(g, opcode(g, 'callnative') + struct.pack('<I', g.syms['ScrCmd_createmon'] | 1)
             + struct.pack('<BBHHI', 0, 6, 19, 50, 0))
    mon = g.symbol_address('gParties')
    assert g.u8(g.symbol_address('gPartiesCount')) == 1
    g.write(g.syms['gSpecialVar_0x8004'], 0, 2)

    # All 16 types, including changing back from Dark to Fighting.
    headers = (ROOT / 'include/constants/pokemon.h').read_text()
    names = ['FIGHTING', 'FLYING', 'POISON', 'GROUND', 'ROCK', 'BUG', 'GHOST',
             'STEEL', 'FIRE', 'WATER', 'GRASS', 'ELECTRIC', 'PSYCHIC', 'ICE',
             'DRAGON', 'DARK']
    types = [int(re.search(r'\bTYPE_' + n + r'\s*=\s*(\d+)', headers)[1]) for n in names]
    for idx in list(range(16)) + [0]:
        g.write(g.syms['gSpecialVar_Result'], types[idx], 2)
        native(g, 'SetTrainingKitHiddenPower')
        ivs = g.box_ivs(mon)
        bits = sum((iv & 1) << i for i, iv in enumerate(ivs))
        assert 15 * bits // 63 == idx, (names[idx], ivs)
        assert all(iv in (30, 31) for iv in ivs)
        g.frame(60)
        assert g.box_ivs(mon) == ivs
    print('All 16 Hidden Power selections persist with matching IVs: PASS', flush=True)

    script = (ROOT / 'data/scripts/plastic_ox_items.inc').read_text()
    menu = script.split('TrainingKit_EVStatMenu::')[1].split('TrainingKit_EVValueMenu::')[0]
    entries = re.findall(r'dynmultipush TrainingKit_Text_(\w+), (\d+)', menu)
    assert entries == [('HP', '0'), ('Attack', '1'), ('Defense', '2'),
                       ('SpAttack', '4'), ('SpDefense', '5'), ('Speed', '3'), ('Back', '6')]
    for stat in range(6):
        g.write(g.syms['gSpecialVar_0x8005'], stat, 2)
        g.write(g.syms['gSpecialVar_0x8006'], 4 * (stat + 1), 2)
        native(g, 'SetTrainingKitEVs')
    assert evs(g, mon) == [4, 8, 12, 16, 20, 24]
    print('Speed is last; every EV selection edits its correct stat: PASS', flush=True)

    # Rattata has Run Away and Guts in its standard Gen III ability slots. Its
    # expansion hidden ability in slot 2 must not be exposed by the kit.
    for slot, succeeds, expected in [(1, True, 1), (2, False, 1), (0, True, 0)]:
        g.write(g.syms['gSpecialVar_Result'], slot, 2)
        native(g, 'SetTrainingKitAbility')
        result = bool(g.u16(g.syms['gSpecialVar_Result']))
        actual = ability_num(g, mon)
        assert result == succeeds, (slot, result, succeeds, actual)
        assert actual == expected, (slot, actual, expected)
    native(g, 'PrepareTrainingKitAbilityMenu')
    assert g.u8(g.syms['gStringVar1']) != 0xFF
    assert g.u8(g.syms['gStringVar2']) != 0xFF
    print('Only standard Gen III ability slots are available: PASS', flush=True)

    original_nature = g.u32(mon) % 25
    for nature in range(25):
        g.write(g.syms['gSpecialVar_Result'], nature, 2)
        native(g, 'SetHiddenNature')
        assert original_nature ^ (g.u8(mon + 18) >> 3) == nature
    selected = (original_nature + 1) % 25
    g.write(g.syms['gSpecialVar_Result'], selected, 2)
    native(g, 'SetHiddenNature')
    # Open the actual summary info page and inspect its memo placeholder.
    g.write(g.syms['gMain'] + 4, g.syms['CB2_ShowPokemonSummaryScreen'] | 1, 4)
    g.frame(120)
    nature_size = g.sizes['gNaturesInfo'] // 25
    expected = g.u32(g.syms['gNaturesInfo'] + selected * nature_size)
    assert g.u32(g.syms['sStringPointers'] + 2 * 4) == expected
    print('All 25 nature changes persist; trainer memo displays changed nature: PASS', flush=True)


if __name__ == '__main__':
    main()
