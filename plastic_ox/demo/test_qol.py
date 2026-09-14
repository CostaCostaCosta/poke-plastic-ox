#!/usr/bin/env python3
"""Headless checks of Options, dialogue boundaries, field speed and audio clock.

Run with the local mgba311 environment after building the ordinary ROM.
Only the emulator's RAM is changed; no player save files are written.
"""
import json
import struct

from test_story import StoryGame, ROOT
from walklib import K


def opcode(g, name):
    table = g.syms['gScriptCmdTable']
    for i in range((g.syms['gScriptCmdTableEnd'] - table) // 4):
        if g.u32(table + 4 * i) & ~0x02000001 == g.syms['ScrCmd_' + name] & ~1:
            return bytes([i])
    raise AssertionError(name)


def begin_code(g, code):
    ptr = g.syms['gStringVar2']
    for i, value in enumerate(code):
        g.write(ptr + i, value)
    g.begin(ptr)


def option_menu(g, text_speed, world_speed):
    main = g.syms['gMain']
    g.write(main + 8, g.syms['CB2_ReturnToField'] | 1, 4)
    g.write(main + 0x438, 0)
    g.write(main + 4, g.syms['CB2_InitOptionMenu'] | 1, 4)
    g.frame(50)
    tasks = g.syms['gTasks']
    task = next(tasks + 40 * i for i in range(16)
                if g.u8(tasks + 40 * i + 4)
                and g.u32(tasks + 40 * i) & ~1 == g.syms['Task_OptionMenuProcessInput'] & ~1)
    while g.u16(task + 10) != text_speed:
        g.tap(K.KEY_RIGHT)
    for _ in range(6):
        g.tap(K.KEY_DOWN)
    while g.u16(task + 22) != world_speed:
        g.tap(K.KEY_RIGHT)
    g.fb.to_pil().convert('RGB').save(f'/tmp/plastic-ox-qol-options-{world_speed}.png')
    g.tap(K.KEY_B)
    g.frame(90)
    assert g.state()['textspeed'] == text_speed
    assert g.var(0x40FE) == world_speed


def dialogue(g):
    text = g.syms['gStringVar1']
    # A, color red, B, page clear, C, 30-frame pause, D, scroll, E, EOS.
    data = bytes([0xBB, 0xFC, 1, 4, 0xBC, 0xFB, 0xBD,
                  0xFC, 8, 30, 0xBE, 0xFA, 0xBF, 0xFF])
    for i, value in enumerate(data):
        g.write(text + i, value)
    code = (opcode(g, 'lockall') + opcode(g, 'message') + struct.pack('<I', text)
            + opcode(g, 'waitmessage') + opcode(g, 'waitbuttonpress')
            + opcode(g, 'yesnobox') + bytes([0, 0])
            + opcode(g, 'releaseall') + opcode(g, 'end'))
    begin_code(g, code)
    g.frame(60)
    g.frame(60)
    assert g.u8(g.syms['sGlobalScriptContextStatus']) != 2
    # The animated prompt may change, but the printer must remain live.
    assert g.u32(g.syms['sFirstTextPrinter']) != 0
    g.tap(K.KEY_A, hold=1, wait=3)
    g.frame(8)
    paused = g.hash()
    g.frame(8)
    assert g.hash() == paused, 'scripted pause consumed multiple ticks per frame'
    g.frame(60)
    assert g.u32(g.syms['sFirstTextPrinter']) != 0, 'scroll prompt was discarded'
    g.tap(K.KEY_B, hold=1, wait=40)
    assert g.u8(g.syms['sGlobalScriptContextStatus']) != 2, 'final confirmation skipped'
    g.tap(K.KEY_A, hold=1, wait=40)
    assert g.u8(g.syms['sGlobalScriptContextStatus']) != 2, 'choice auto-selected'
    g.tap(K.KEY_B, hold=1, wait=40)
    assert g.u8(g.syms['sGlobalScriptContextStatus']) == 2
    assert g.u16(g.syms['gSpecialVar_Result']) == 0
    print('Instant: color, page clear, timed pause, scroll, A/B confirmation and choice PASS', flush=True)


def traversal(g, speed, held=None, prevent=False):
    g.setvar(0x40FE, speed)
    g.warp('PalletTown_Frlg', 12, 18)
    g.flag('FLAG_PREVENT_OVERWORLD_SPEEDUP', prevent)
    main, music = g.syms['gMain'], g.syms['gMPlayInfo_BGM']
    before = (g.u32(main + 0x20), g.u32(music + 12))
    song = g.u32(music)
    tempo = tuple(g.u16(music + off) for off in (28, 30, 32))
    start_y = g.state()['y']
    keys = (K.KEY_UP,) if held is None else (K.KEY_UP, held)
    g.core.set_keys(*keys)
    g.frame(32)
    g.core.clear_keys(*keys)
    end_y = g.state()['y']
    g.frame(88)
    after = (g.u32(main + 0x20), g.u32(music + 12))
    assert g.u32(music) == song, 'music restarted during traversal'
    assert tuple(g.u16(music + off) for off in (28, 30, 32)) == tempo
    g.flag('FLAG_PREVENT_OVERWORLD_SPEEDUP', False)
    result = (start_y - end_y, after[0] - before[0], after[1] - before[1])
    print(f'World option={speed} held={held} prevent={prevent}: tiles/VBlanks/music ticks {result}', flush=True)
    return result


def doors(g, speed):
    g.setvar(0x40FE, speed)
    g.warp('OldaleTown', 5, 8)
    g.hold(K.KEY_UP, 80)
    g.frame(150)
    groups = json.loads((ROOT / 'data/maps/map_groups.json').read_text())
    ids = {name: (i, j) for i, group in enumerate(groups['group_order'])
           for j, name in enumerate(groups[group])}
    assert (g.state()['group'], g.state()['num']) == ids['OldaleTown_House1']
    g.hold(K.KEY_DOWN, 100)
    g.frame(150)
    assert (g.state()['group'], g.state()['num']) == ids['OldaleTown']
    assert g.var(0x40FE) == speed and g.state()['textspeed'] == 3
    print(f'{1 << speed}x: animated door entry/exit and settings retained PASS', flush=True)


def main():
    g = StoryGame(build='')
    assert g.var(0x40FE) == 0, 'new save did not default to 1x'
    for speed in range(4):
        option_menu(g, speed, speed)
        option_menu(g, 3, speed)
        dialogue(g)
    results = [traversal(g, speed) for speed in range(4)]
    assert all(result[1:] == results[0][1:] for result in results), results
    assert results[1][0] > results[0][0] and results[2][0] > results[1][0], results
    assert traversal(g, 3, held=K.KEY_R)[0] == results[0][0]
    assert traversal(g, 3, prevent=True)[0] == results[0][0]
    assert traversal(g, 0xFFFF)[0] == results[0][0]
    for speed in range(4):
        doors(g, speed)
    print('QOL RUNTIME CHECKS PASSED', flush=True)


if __name__ == '__main__':
    main()
