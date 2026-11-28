#!/usr/bin/env python3
"""Delibird MAIL errand: WEBSTER (Route35_hns) gives the bird, RANDY (Route33_hns) takes the letter.

Talks to both NPCs in the real ROM, walks to RANDY, and checks the flags the
POX_PU_MailGuard / POX_PU_MailRecipient scripts drive. Also covers a save whose
VAR_POX_DELIBIRD_IDENTITY no longer matches the bird: RANDY must still accept
Webster's own Delibird holding Webster's letter.
"""
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_sudowoodo_v1 import new_game, talk, opcode, run_code
from pox_fixtures import save_reload
from walk_leg1 import navigate
from walklib import K

SPECIES_DELIBIRD = 225
VAR_REPEL_STEP_COUNT = 0x4021        # include/constants/vars.h
VAR_POX_DELIBIRD_IDENTITY = 0x40DC   # include/constants/vars.h


def receive(g):
    g.warp('Route35_hns', 20, 7)          # below WEBSTER (20,6)
    g.frame(90)
    r = talk(g, K.KEY_UP)
    assert g.flag('FLAG_POX_DELIBIRD_RECEIVED'), ('no delibird', r)
    species = [g.party_species(i) for i in range(g.count())]
    assert SPECIES_DELIBIRD in species, species


def deliver(g):
    # Route 33's hiker ANTHONY would otherwise stop the walk for a battle.
    # A repel keeps wild encounters out of this dialogue check.
    run_code(g, opcode(g, 'settrainerflag') + struct.pack('<H', g.const('TRAINER_PLASTIC_OX_PU_ROUTE33'))
             + opcode(g, 'setvar') + struct.pack('<HH', VAR_REPEL_STEP_COUNT, 250)
             + opcode(g, 'releaseall'))
    g.warp('Route33_hns', 25, 30)
    g.frame(120)
    navigate(g, (25, 28))                  # step up to RANDY (25,27)
    r = talk(g, K.KEY_UP)
    assert g.flag('FLAG_POX_DELIBIRD_DELIVERED'), ('RANDY refused delivery', r)
    assert any('A letter from WEBSTER' in t for t in r['text']), r
    r = talk(g, K.KEY_UP)
    assert any('Thanks again' in t for t in r['text']), r


def main():
    g = new_game()
    receive(g)
    print('ok  WEBSTER gives DELIBIRD holding MAIL')
    save_reload(g)
    assert g.flag('FLAG_POX_DELIBIRD_RECEIVED')
    print('ok  save/reload keeps the errand')
    deliver(g)
    print('ok  RANDY accepts the DELIBIRD MAIL, then thanks')

    g = new_game()
    receive(g)
    run_code(g, opcode(g, 'setvar') + struct.pack('<HH', VAR_POX_DELIBIRD_IDENTITY, 0)
             + opcode(g, 'releaseall'))
    deliver(g)
    print('ok  RANDY accepts the bird even when the identity var is stale')


if __name__ == '__main__':
    main()
