#!/usr/bin/env python3
"""Seafoam Sage regression: real battles/capture/save with RAM-only fixtures."""
import sys
from pathlib import Path

from test_cinnabar import game, finish_trainer, save_reload
from test_sudowoodo_v1 import (K, const, talk, wait_for_battle, battle_mon,
    drain, fight, settle_overworld, bag, POCKET_BALLS, in_overworld)
from test_burned_tower import visible_actor_ids
from walk_leg1 import navigate

ROOT = Path(__file__).resolve().parents[2]
MAP = 'SeafoamIslands_B4F_Frlg'
CAUGHT = 'FLAG_POX_HIDE_ARTICUNO'
VICTORY = 0xB41  # POX_SAGE_TRAINER_FLAGS_START + (939 - 938).
ARTICUNO = const('SPECIES_ARTICUNO', 'species.h')
SHOTS = Path('/tmp/pox_seafoam_shots')


def shot(g, name):
    SHOTS.mkdir(exist_ok=True)
    g.fb.to_pil().convert('RGB').save(SHOTS / (name + '.png'))


def test_team():
    sys.path.insert(0, str(ROOT / 'plastic_ox/agent'))
    from test_trainer_teams_v2 import parse_mon
    import pox_progression as p
    team = (ROOT / 'plastic_ox/alpha/seafoam/trainers.party').read_text()
    assert team.strip() in (ROOT / 'src/data/trainers.party').read_text()
    mons = [parse_mon(b) for b in team.strip().split('\n\n')[1:]]
    assert [m['name'] for m in mons] == ['Jynx', 'Donphan', 'Vaporeon', 'Machamp', 'Houndoom', 'Articuno']
    abilities = p.load_abilities()
    for mon in mons:
        assert p.tier_of(mon['species']) == 'UUBL', mon
        assert mon['ability'].upper().replace(' ', '_') in abilities[mon['species']], mon
        assert sum(mon['evs'].values()) <= 510 and max(mon['evs'].values()) <= 252
        for move in mon['moves']:
            legal, reason = p.move_legal(mon['species'], move, mon['level'], gen3_only=True)
            assert legal, (mon['name'], move, reason)
    print('PASS: six UUBL species, Articuno only legendary, legal moves/abilities/EVs', flush=True)


def test_encounter():
    g = game()
    # Simulate completed boulder puzzle; use the real calm-water layout.
    g.flag('FLAG_POX_STOPPED_SEAFOAM_B4F_CURRENT', True)
    g.warp(MAP, 10, 3)
    g.frame(120)
    assert {3, 5} <= visible_actor_ids(g)
    shot(g, 'sage_and_articuno')
    # Walk the chamber stairs to ensure the new Sage does not block access.
    navigate(g, (10, 4))
    navigate(g, (9, 3))
    assert talk(g, K.KEY_UP)['battle'], 'Articuno must invoke Sage before capture'
    assert wait_for_battle(g)
    assert g.u32(g.syms['gBattleTypeFlags']) & 8
    assert not g.flag(VICTORY) and not g.flag(CAUGHT)
    stride = g.sizes['gParties'] // 24
    enemy = g.syms['gParties'] + 6 * stride
    expected = [const('SPECIES_' + name, 'species.h') for name in
                ['JYNX', 'DONPHAN', 'VAPOREON', 'MACHAMP', 'HOUNDOOM', 'ARTICUNO']]
    assert [g.box_species(enemy + i * stride) for i in range(6)] == expected
    shot(g, 'sage_battle')
    start = g.core.save_raw_state()
    finish_trainer(g, False)
    assert g.u8(g.syms['gBattleOutcome']) == 2
    assert not g.flag(VICTORY) and not g.flag(CAUGHT)
    g.frame(600)
    assert settle_overworld(g) is not None
    g.warp(MAP, 10, 3)
    g.frame(120)
    assert talk(g, K.KEY_UP)['battle']
    assert wait_for_battle(g)
    print('PASS: both actors start Sage battle; six correct opponents; loss retries', flush=True)

    assert g.core.load_raw_state(start)
    finish_trainer(g, True)
    assert g.flag(VICTORY) and not g.flag(CAUGHT)
    assert wait_for_battle(g)
    assert not g.u32(g.syms['gBattleTypeFlags']) & 8
    assert g.u32(g.syms['gBattleTypeFlags']) & (1 << 14)
    assert (battle_mon(g, 1)['species'], battle_mon(g, 1)['level']) == (ARTICUNO, 50)
    shot(g, 'articuno_reward')
    reward = g.core.save_raw_state()

    fight(g, 'run')
    assert drain(g) and not g.flag(CAUGHT) and g.flag(VICTORY)
    g.warp(MAP, 10, 3)
    g.frame(120)
    g.tap(K.KEY_UP, hold=2, wait=16)
    for _ in range(300):
        if g.task('Task_HandleYesNoInput'):
            break
        g.tap(K.KEY_A, hold=1, wait=6)
    assert g.task('Task_HandleYesNoInput')
    g.frame(30)
    g.tap(K.KEY_B, hold=2, wait=30)
    assert drain(g)
    save_reload(g)
    assert g.flag(VICTORY) and not g.flag(CAUGHT)
    assert {3, 5} <= visible_actor_ids(g)
    assert talk(g, K.KEY_UP)['battle']
    assert wait_for_battle(g)
    assert not g.u32(g.syms['gBattleTypeFlags']) & 8
    assert battle_mon(g, 1)['species'] == ARTICUNO
    print('PASS: victory unlocks level 50 reward; flee/decline/save retain access without rematch', flush=True)

    assert g.core.load_raw_state(reward)
    finish_trainer(g, True)
    assert g.u8(g.syms['gBattleOutcome']) == 1
    assert drain(g) and not g.flag(CAUGHT)
    assert talk(g, K.KEY_UP)['battle']
    assert wait_for_battle(g)
    assert battle_mon(g, 1)['species'] == ARTICUNO
    assert not g.u32(g.syms['gBattleTypeFlags']) & 8
    print('PASS: knocking out reward allows another capture attempt', flush=True)

    assert g.core.load_raw_state(reward)
    ball = const('ITEM_POKE_BALL', 'items.h')
    before = bag(g, ball, POCKET_BALLS)
    g.write(g.syms['gActionSelectionCursor'], 1)
    g.tap(K.KEY_A, hold=1, wait=60)
    g.write(g.syms['gBagPosition'] + 5, POCKET_BALLS)
    g.write(g.syms['gBagPosition'] + 8 + 2 * POCKET_BALLS, 0)
    g.frame(60)
    for _ in range(20):
        g.tap(K.KEY_A, hold=2, wait=30)
        if bag(g, ball, POCKET_BALLS) < before:
            break
    assert bag(g, ball, POCKET_BALLS) == before - 1
    for _ in range(2000):
        if in_overworld(g) and g.flag(CAUGHT):
            break
        g.tap(K.KEY_B, hold=2, wait=10)
    assert g.u8(g.syms['gBattleOutcome']) == 7 and g.flag(CAUGHT)
    assert drain(g)
    storage = g.u32(g.syms['gPokemonStoragePtr'])
    assert any(g.box_species(storage + 4 + (stride - 20) * i) == ARTICUNO for i in range(30))
    assert not {3, 5} & visible_actor_ids(g)
    g.warp('SeafoamIslands_B3F_Frlg', 15, 8)
    g.frame(120)
    g.warp(MAP, 10, 3)
    g.frame(120)
    save_reload(g)
    assert g.flag(CAUGHT) and g.flag(VICTORY)
    assert not {3, 5} & visible_actor_ids(g)
    shot(g, 'caught_after_continue')
    print('PASS: first Poke Ball catches reward; full-party boxing; both actors stay removed after reentry/save/Continue', flush=True)


if __name__ == '__main__':
    test_team()
    test_encounter()
    print('Seafoam Articuno encounter: PASS', flush=True)
