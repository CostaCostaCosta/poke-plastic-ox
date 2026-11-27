#!/usr/bin/env python3
"""Clear Bell chain: ZAPDOS at the Goldenrod Radio Tower once New Mauville's
generator is off (and OU is open), the engineer's CLEAR BELL, and MORTY under
the Burned Tower ringing it for SUICUNE.

    plastic_ox/bin/pox-mgba-python plastic_ox/demo/test_clear_bell.py

Setup writes emulator RAM only (flags, vars, items, position); never ROM or saves.
"""
import re
from pathlib import Path

from pox_fixtures import game, shot as _shot
from test_sudowoodo_v1 import K, talk, wait_for_battle, battle_mon, const, give_item
from test_tin_tower import visible, home

ROOT = Path(__file__).resolve().parents[2]
RADIO = 'GoldenrodCity_RadioTower_5F_hns'
TOWER = 'PlasticOx_BurnedTowerB1F'
GYM = 'PlasticOx_MortyGym'
OFFICE = 'EcruteakCity_SageOffice2_hns'
ZAPDOS, ZAPDOS_SAGE, ENGINEER = 4, 5, 6      # after the three Goldenrod import NPCs
MORTY, SUICUNE = 17, 18                      # after the sixteen story-scene objects
GYM_MORTY = 1
OFFICE_ZAPDOS = 10                           # keeper 2, home sages 3..9, Zapdos sage 10


def var_id(name):
    return int(re.search(r'#define ' + name + r'\s+(0x[0-9A-Fa-f]+)',
                         (ROOT / 'include/constants/vars.h').read_text())[1], 16)


def shot(g, name):
    _shot(g, 'clear_bell_' + name)


def text_of(r):
    return ' '.join(r['text']).replace('\n', ' ')


def radio(g, generator_off, ou, caught=False):
    g.setvar(var_id('VAR_NEW_MAUVILLE_STATE'), 2 if generator_off else 0)
    g.flag('FLAG_POX_STORY_SPACE_CENTER', ou)
    g.flag('FLAG_POX_CAUGHT_ZAPDOS', caught)
    g.warp(RADIO, 29, 13)
    g.frame(120)
    return visible(g)


def test_radio_tower_states():
    g = game()
    ids = radio(g, False, True)
    assert ENGINEER in ids and not ({ZAPDOS, ZAPDOS_SAGE} & ids), ids
    r = talk(g, K.KEY_RIGHT)
    assert 'Clean signal' in text_of(r), r
    ids = radio(g, True, False)
    assert not ({ZAPDOS, ZAPDOS_SAGE} & ids), ids
    r = talk(g, K.KEY_RIGHT)
    assert 'Static' in text_of(r) and not r['battle'], r
    print('PASS: Radio Tower 5F is quiet with the generator on, static (no ZAPDOS) before OU', flush=True)


def test_zapdos_sage_battle():
    g = game()
    ids = radio(g, True, True)
    assert {ZAPDOS, ZAPDOS_SAGE} <= ids, ids
    r = talk(g, K.KEY_RIGHT)
    assert 'robes' in text_of(r), r
    g.warp(RADIO, 27, 9)
    g.frame(120)
    shot(g, 'zapdos')
    r = talk(g, K.KEY_UP)
    assert 'HOENN' in text_of(r) and r['battle'] and wait_for_battle(g), r
    lead = battle_mon(g, 1)
    assert lead['species'] == const('SPECIES_JOLTEON', 'species.h'), lead
    print('PASS: generator off + OU shows ZAPDOS and its sage; the sage battle opens with Jolteon', flush=True)


def test_zapdos_caught_bell_and_home():
    g = game()
    ids = radio(g, True, True, caught=True)
    assert not ({ZAPDOS, ZAPDOS_SAGE} & ids), ids
    r = talk(g, K.KEY_RIGHT)
    assert 'footing' in text_of(r), r
    r = talk(g, K.KEY_RIGHT)
    assert 'whistle' in text_of(r), r      # second visit: already holds the bell
    home(g, 0)
    g.warp(OFFICE, 7, 5)
    g.frame(120)
    ids = visible(g)
    assert OFFICE_ZAPDOS in ids, ids
    print('PASS: caught ZAPDOS hides the pair; engineer gives the CLEAR BELL once; sage is home', flush=True)


def tower(g, badge, bell=False, rang=False, caught=False):
    g.flag('FLAG_POX_STORY_BURNED_TOWER', True)
    g.flag('FLAG_BADGE03_GET', badge)
    g.flag('FLAG_POX_RANG_CLEAR_BELL', rang)
    g.flag('FLAG_POX_CAUGHT_SUICUNE', caught)
    if bell:
        give_item(g, const('ITEM_CLEAR_BELL', 'items.h'))
    g.warp(TOWER, 16, 13)
    g.frame(120)
    return visible(g)


def test_morty_waits():
    g = game()
    ids = tower(g, False)
    assert not ({MORTY, SUICUNE} & ids), ids
    ids = tower(g, True)
    assert MORTY in ids and SUICUNE not in ids, ids
    shot(g, 'morty_waiting')
    r = talk(g, K.KEY_UP)
    assert 'wait' in text_of(r) and not r['battle'], r
    g.warp(GYM, 5, 5)
    g.frame(120)
    assert GYM_MORTY not in visible(g), visible(g)
    print('PASS: after badge 3 MORTY waits under the Burned Tower and is away from his Gym', flush=True)


def test_bell_calls_suicune():
    g = game()
    tower(g, True, bell=True)
    r = talk(g, K.KEY_UP)
    text = text_of(r)
    assert 'Shall I ring' in text and r['battle'] and wait_for_battle(g), r
    assert g.flag('FLAG_POX_RANG_CLEAR_BELL'), 'bell flag not set'
    lead = battle_mon(g, 1)
    assert lead['species'] == const('SPECIES_GENGAR', 'species.h'), lead
    shot(g, 'morty_battle')
    print('PASS: MORTY rings the CLEAR BELL, SUICUNE returns, MORTY battles as its sage (Gengar lead)', flush=True)


def test_rang_and_caught_states():
    g = game()
    ids = tower(g, True, rang=True)
    assert {MORTY, SUICUNE} <= ids, ids
    shot(g, 'suicune_back')
    ids = tower(g, True, rang=True, caught=True)
    assert not ({MORTY, SUICUNE} & ids), ids
    g.warp(GYM, 5, 5)
    g.frame(120)
    assert GYM_MORTY in visible(g), visible(g)
    print('PASS: rung bell keeps SUICUNE beside MORTY; once caught both leave and MORTY is back at the Gym', flush=True)


if __name__ == '__main__':
    test_radio_tower_states()
    test_zapdos_sage_battle()
    test_zapdos_caught_bell_and_home()
    test_morty_waits()
    test_bell_calls_suicune()
    test_rang_and_caught_states()
    print('Clear Bell: PASS', flush=True)
