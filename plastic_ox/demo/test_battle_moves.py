#!/usr/bin/env python3
"""Battle moves that once hung the game, played in mGBA.

* Charge: the player's POKeMON and a wild POKeMON (every move slot Charge)
  both use Charge for several turns; the battle must keep returning to the
  action menu (no hang in the effect script or the animation).
"""
import struct
import sys

from pox_fixtures import game, shot
from test_sudowoodo_v1 import const, opcode, begin_code, in_overworld
from walklib import K


def start_wild(g, species, level):
    begin_code(g, opcode(g, 'setwildbattle') + struct.pack('<HBHHBH', species, level, 0, 0, 0, 0)
               + opcode(g, 'dowildbattle') + opcode(g, 'releaseall') + opcode(g, 'end'))
    for _ in range(600):
        g.frame(10)
        if g.u32(g.syms['gBattleTypeFlags']):
            return
    raise AssertionError('wild battle did not start')


def use_move_turns(g, move, turns, foe_move=None, timeout=6000):
    lay = [g.u32(g.syms['gMetamonTestLayout'] + i * 4) for i in range(16)]
    base = g.syms['gBattleMons']
    done, frames, waiting = 0, 0, True
    while done < turns:
        if frames > timeout:
            shot(g, 'battle_moves_hang')
            raise AssertionError(f'battle hung using move {move} (turn {done + 1})')
        if g.controller('HandleInputChooseAction'):
            for b, m in ((0, move), (1, foe_move or move)):
                mon = base + b * lay[6]
                for slot in range(4):
                    g.write(mon + lay[7] + slot * 2, m, 2)
                    g.write(mon + lay[12] + slot, 30)
                g.write(mon + lay[10], 500, 2)
                g.write(mon + lay[11], 500, 2)
            if not waiting:
                done += 1
                frames = 0
                if done >= turns:
                    break
            waiting = False
            g.write(g.syms['gActionSelectionCursor'], 0)
            g.tap(K.KEY_A, hold=1, wait=4)
        elif g.controller('HandleInputChooseMove'):
            g.write(g.syms['gMoveSelectionCursor'], 0)
            g.tap(K.KEY_A, hold=1, wait=4)
        else:
            g.tap(K.KEY_A, hold=1, wait=4)
        frames += 5
    return done


def main():
    g = game()
    charge = const('MOVE_CHARGE', 'moves.h')
    start_wild(g, const('SPECIES_PIKACHU', 'species.h'), 30)
    turns = use_move_turns(g, charge, 4)
    print(f'PASS Charge used by player and wild foe for {turns} turns without hanging', flush=True)


if __name__ == '__main__':
    sys.exit(main())
