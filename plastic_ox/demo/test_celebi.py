#!/usr/bin/env python3
"""Celebi at the Ilex Forest shrine: the GS BALL from Trick House puzzle 5,
a sage who waits after the Burned Tower and battles only with the ball, and
the sage's homecoming in the Ecruteak sage office.

    plastic_ox/bin/pox-mgba-python plastic_ox/demo/test_celebi.py

Setup writes emulator RAM only (flags, items, position); never ROM or save files.
"""
import json
import re
from pathlib import Path

from pox_fixtures import game, at, shot as _shot
from test_sudowoodo_v1 import K, talk, settle, wait_for_battle, battle_mon, const, give_item

ROOT = Path(__file__).resolve().parents[2]
ILEX = 'IlexForest_hns'
OFFICE = 'EcruteakCity_SageOffice2_hns'


def local_id(map_name, name):
    objs = json.loads((ROOT / f'data/maps/{map_name}/map.json').read_text())['object_events']
    return next(i + 1 for i, o in enumerate(objs) if o.get('local_id') == name)


CELEBI = local_id(ILEX, 'LOCALID_POX_CELEBI')
SAGE = local_id(ILEX, 'LOCALID_POX_CELEBI_SAGE')
HOME = local_id(OFFICE, 'LOCALID_POX_HOME_CELEBI_SAGE')


def shot(g, name):
    _shot(g, 'celebi_' + name)


def visible(g):
    stride = g.sizes['gObjectEvents'] // 16
    return {g.u8(g.syms['gObjectEvents'] + i * stride + 8)
            for i in range(16) if g.u8(g.syms['gObjectEvents'] + i * stride) & 1}


def enter(g, map_name, x, y):
    g.warp(map_name, x, y)
    g.frame(120)
    settle(g)


def test_trick_house_prize():
    """Static: puzzle 5 (badge 6 gate) gives the GS BALL, also on the bag-full re-give."""
    end = (ROOT / 'data/maps/Route110_TrickHouseEnd/scripts.inc').read_text()
    block = re.search(r'Route110_TrickHouseEnd_EventScript_CompletedPuzzle5::(.*?)\n\n', end, re.S)[1]
    assert 'giveitem ITEM_GS_BALL' in block and 'ITEM_TM_TAUNT' not in end, block
    entrance = (ROOT / 'data/maps/Route110_TrickHouseEntrance/scripts.inc').read_text()
    assert 'ITEM_TM_TAUNT' not in entrance and 'giveitem ITEM_GS_BALL' in entrance
    gate = re.search(r'CheckReadyForPuzzle5::\n\tcall_if_unset (\w+)', entrance)[1]
    assert gate == 'FLAG_BADGE06_GET', gate
    print('PASS: Trick House puzzle 5 (badge 6) awards the GS BALL', flush=True)


def test_hidden_before_tower():
    g = game()
    g.flag('FLAG_POX_STORY_BURNED_TOWER', False)
    g.flag('FLAG_POX_CAUGHT_CELEBI', False)
    enter(g, ILEX, 24, 30)
    ids = visible(g)
    assert not ({CELEBI, SAGE} & ids), ids
    shot(g, 'before_tower')
    print('PASS: before the Burned Tower the shrine is empty', flush=True)


def test_waits_without_ball():
    g = game()
    g.flag('FLAG_POX_STORY_BURNED_TOWER', True)
    g.flag('FLAG_POX_CAUGHT_CELEBI', False)
    enter(g, ILEX, 24, 29)
    ids = visible(g)
    assert {CELEBI, SAGE} <= ids, ids
    shot(g, 'shrine')
    r = talk(g, K.KEY_UP)
    text = ' '.join(r['text']).replace('\n', ' ')
    assert 'waiting' in text and not r['battle'], r
    print('PASS: after the tower the sage waits by the shrine and will not battle without the ball', flush=True)


def test_battle_with_ball():
    g = game()
    g.flag('FLAG_POX_STORY_BURNED_TOWER', True)
    g.flag('FLAG_POX_CAUGHT_CELEBI', False)
    give_item(g, const('ITEM_GS_BALL', 'items.h'))
    enter(g, ILEX, 24, 29)
    r = talk(g, K.KEY_UP)
    assert r['battle'] and wait_for_battle(g), r
    lead = battle_mon(g, 1)
    assert lead['species'] == const('SPECIES_BRELOOM', 'species.h'), lead
    shot(g, 'sage_battle')
    print('PASS: with the GS BALL the Celebi sage battles (Breloom lead)', lead, flush=True)


def test_caught():
    g = game()
    g.flag('FLAG_POX_STORY_BURNED_TOWER', True)
    g.flag('FLAG_POX_CAUGHT_CELEBI', True)
    enter(g, ILEX, 24, 30)
    assert not ({CELEBI, SAGE} & visible(g)), visible(g)
    enter(g, OFFICE, 4, 8)
    assert HOME in visible(g), visible(g)
    shot(g, 'office')
    g.flag('FLAG_POX_CAUGHT_CELEBI', False)
    enter(g, OFFICE, 4, 8)
    assert HOME not in visible(g), visible(g)
    print('PASS: once caught the shrine empties and the sage is home in the Ecruteak office', flush=True)


if __name__ == '__main__':
    test_trick_house_prize()
    test_hidden_before_tower()
    test_waits_without_ball()
    test_battle_with_ball()
    test_caught()
    print('Celebi: PASS', flush=True)
