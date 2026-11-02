#!/usr/bin/env python3
"""Rustboro gym wiring check: story Roxanne plays her existing team via Metamon.

Boots with a 3-mon player party to prove the relaxed activation gate, then
plays the Pox_Roxanne trainerbattle_single to completion in mGBA. Asserts the
arena allocates, decisions/commits stay consistent, no fault fires, and the
badge script flag lands after the battle.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(ROOT / 'plastic_ox/demo'))
import test_story
from test_single_player import boot_new_game
from test_qol import begin_code, opcode
from walklib import K
from smoke import Game


class GymGame(Game):
    def task(self, name):
        funcs = self.functions.get(name, set())
        return any(self.u8(self.syms['gTasks'] + i * 40 + 4) and
                   self.u32(self.syms['gTasks'] + i * 40) & ~0x02000001 in funcs
                   for i in range(16))


def main():
    test_story.boot_test_game = boot_new_game
    g = GymGame()
    out = ROOT / 'plastic_ox/battle/metamon/build'
    begin_code(g, opcode(g, 'callnative')
               + struct.pack('<I', g.syms['GivePlasticOxPlayerParty'] | 1)
               + opcode(g, 'releaseall') + opcode(g, 'end'))
    g.frame(60)
    assert g.count() == 6
    # GivePlasticOxPlayerParty sets every badge (demo obedience helper), which
    # sends Pox_Roxanne to its already-beaten branch. Clear them again: the
    # gift mons are player-OT, so obedience does not depend on badges.
    for badge in range(1, 9):
        g.flag(f'FLAG_BADGE0{badge}_GET', False)
    # Exercise the relaxed gate: play the gym battle with a 3-mon party.
    g.write(g.syms['gPartiesCount'], 3)
    assert g.count() == 3
    g.flag('FLAG_POX_STORY_ILEX', True)
    g.warp('RustboroCity_Gym', 5, 3)
    # Talk to the story Roxanne NPC like a player: face her, then mash A
    # through the intro until the trainer battle starts.
    g.tap(K.KEY_UP, hold=2, wait=12)
    for _ in range(300):
        g.tap(K.KEY_A, hold=2, wait=10)
        if g.u32(g.syms['gBattleTypeFlags']) & 8:
            break
    else:
        g.fb.to_pil().convert('RGB').save(str(out / 'gym-failed.png'))
        raise AssertionError('trainer battle did not start')
    try:
        g.wait_action()
    except AssertionError:
        g.fb.to_pil().convert('RGB').save(str(out / 'gym-failed.png'))
        raise
    arena = g.u32(g.syms['sMetamon'])
    assert arena, 'Metamon arena not allocated for TRAINER_PLASTIC_OX_ROXANNE'
    print('Arena', hex(arena), 'bytes', g.u32(g.syms['gMetamonArenaBytes']), flush=True)
    assert not any(g.u8(arena + g.u32(g.syms['gMetamonTestLayout']) + i) for i in range(1536)), \
        'Recurrent state not reset'
    layout = [g.u32(g.syms['gMetamonTestLayout'] + i * 4) for i in range(16)]
    move_off, pp_off = layout[7], layout[12]
    last = -1
    for step in range(50000):
        if not g.u32(g.syms['sMetamon']):
            break
        assert not g.u32(g.syms['gMetamonFault']), g.u32(g.syms['gMetamonFault'])
        count = g.u32(g.syms['gMetamonCommits'])
        if count != last:
            last = count
            print('commits', count, 'decisions', g.u32(g.syms['gMetamonDecisions']),
                  'moves', g.u32(g.syms['gMetamonMoves']),
                  'switches', g.u32(g.syms['gMetamonSwitches']),
                  'replacements', g.u32(g.syms['gMetamonReplacements']), flush=True)
        if g.controller('HandleInputChooseAction'):
            g.write(g.syms['gActionSelectionCursor'], 0)
            g.tap(K.KEY_A, hold=1, wait=2)
        elif g.controller('HandleInputChooseMove'):
            b = g.syms['gBattleMons']
            available = []
            for i in range(4):
                move = g.u16(b + move_off + 2 * i)
                pp = g.u8(b + pp_off + i)
                if move and pp:
                    power = struct.unpack('<f', bytes(g.u8(g.syms['sMoveInfo'] + move * 20 + j) for j in range(4)))[0]
                    if move in (69, 82, 101):
                        power = 0.2
                    available.append((power, i))
            slot = max(available, default=(0, 0))[1]
            g.write(g.syms['gMoveSelectionCursor'], slot)
            g.tap(K.KEY_A, hold=1, wait=2)
        elif g.task('Task_HandleChooseMonInput'):
            size = g.sizes['gParties'] // 24
            slots = [i for i in range(1, 3) if g.u16(g.syms['gParties'] + i * size + size - 14) > 0]
            if slots:
                g.write(g.syms['gPartyMenu'] + 9, slots[0])
            g.tap(K.KEY_A, hold=1, wait=3)
        else:
            g.tap(K.KEY_A, hold=1, wait=3)
        if step % 2000 == 0:
            g.fb.to_pil().convert('RGB').save(str(out / 'gym-progress.png'))
    else:
        raise AssertionError('Gym battle did not complete')
    result = {name: g.u32(g.syms[name]) for name in
              ('gMetamonDecisions', 'gMetamonCommits', 'gMetamonFrames', 'gMetamonMoves',
               'gMetamonSwitches', 'gMetamonReplacements', 'gMetamonFault')}
    result.update(outcome=g.u8(g.syms['gBattleOutcome']))
    print(result, flush=True)
    assert not result['gMetamonFault'], result
    assert result['gMetamonDecisions'] > 0, result
    assert result['gMetamonCommits'] == result['gMetamonMoves'] + result['gMetamonSwitches'] + result['gMetamonReplacements'], result
    # Drain the post-battle dialogue so the script reaches its badge flag.
    for _ in range(300):
        if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            break
        g.tap(K.KEY_A, hold=1, wait=10)
    assert g.flag('FLAG_BADGE01_GET'), 'badge flag not set after gym victory'
    g.fb.to_pil().convert('RGB').save(str(out / 'gym-smoke.png'))
    print('Rustboro gym Metamon smoke: PASS', flush=True)


if __name__ == '__main__':
    main()
