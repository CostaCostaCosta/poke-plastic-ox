#!/usr/bin/env python3
"""Custom boot, skip, menu return, replay, and real flash-save continue checks."""
import struct
import subprocess
from pathlib import Path
from walklib import GBA, K
from test_story import StoryGame, NM
from test_qol import begin_code, opcode

ROOT = Path(__file__).resolve().parents[2]


def symbols():
    return {f[2]: int(f[0], 16) for line in subprocess.check_output(
        [NM, str(ROOT / 'pokeemerald.elf')], text=True).splitlines()
        if len(f := line.split()) == 3}


def callback(g, syms, name):
    return g.u32(syms['gMain'] + 4) & ~1 == syms[name] & ~1


def opening(g, syms):
    return bool(g.u8(syms['sPoxTitleOpening']))


def title(g, syms):
    assert callback(g, syms, 'MainCB2_PlasticOxTitle')
    assert not opening(g, syms)


def check_title():
    s = symbols()
    for key in (K.KEY_A, K.KEY_B, K.KEY_START):
        g = GBA()
        g.frame(70)
        assert opening(g, s)
        g.tap(key, wait=40)
        title(g, s)
        # Skipping must not also enter the menu.
        g.tap(K.KEY_START, wait=100)
        assert not callback(g, s, 'MainCB2_PlasticOxTitle')
        g.tap(K.KEY_B, wait=100)
        title(g, s)
    g = GBA()
    g.frame(370)
    title(g, s)
    g.frame(2000)
    assert opening(g, s), 'Idle title did not replay custom intro'
    g.frame(340)
    title(g, s)
    print('PASS: A/B/Start skip, natural reveal, menu return, custom idle replay')


def check_continue():
    # GBA() uses an in-memory flash device, never the user's .sav file.
    g = StoryGame()
    s = g.syms
    begin_code(g, opcode(g, 'callnative') + struct.pack('<I', s['Script_ForceSaveGame'] | 1)
               + opcode(g, 'waitstate') + opcode(g, 'end'))
    for _ in range(100):
        g.tap(K.KEY_A, hold=1, wait=15)
        if g.u8(s['sGlobalScriptContextStatus']) == 2:
            break
    else:
        raise AssertionError('Save did not finish')
    g.frame(120)
    g.core.reset()
    g.frame(400)
    title(g, s)
    assert g.u16(s['gSaveFileStatus']) == 1, 'Flash save was not loaded'
    g.tap(K.KEY_START, wait=100)
    g.tap(K.KEY_A, wait=350)  # Continue is the selected first menu item.
    assert callback(g, s, 'CB2_Overworld'), 'Continue did not reach the overworld'
    assert (g.state()['group'], g.state()['num']) == (38, 1)
    save2 = g.u32(s['gSaveBlock2Ptr'])
    assert g.u8(save2) == 0xCA and g.u8(save2 + 1) == 0xFF
    print('PASS: save to emulator flash, reset, custom title, Continue restores identity/location')


if __name__ == '__main__':
    check_title()
    check_continue()
