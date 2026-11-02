#!/usr/bin/env python3
"""Play the Route 36 Sudowoodo battle through Burned Tower B1F in mGBA."""
import json
from pathlib import Path

from test_sudowoodo_v1 import (ITEM_SQUIRT_BOTTLE, POCKET_ITEMS, armed, bag,
                               battle_mon, drain, fight, go_tree, in_battle,
                               new_game, settle, talk, wait_for_battle)
from walk_leg1 import navigate
from walklib import K

ROOT = Path(__file__).resolve().parents[2]
SHOTS = Path('/tmp/pox_burned_tower_shots')
FIRE_STONE = 211


def map_id(name):
    groups = json.loads((ROOT / 'data/maps/map_groups.json').read_text())
    return next((i, groups[group].index(name))
                for i, group in enumerate(groups['group_order'])
                if name in groups[group])


def at(g, name):
    state = g.state()
    return (state['group'], state['num']) == map_id(name)


def shot(g, name):
    SHOTS.mkdir(exist_ok=True)
    g.fb.to_pil().convert('RGB').save(SHOTS / name)


def visible_actor_ids(g):
    stride = g.sizes['gObjectEvents'] // 16
    return {g.u8(g.syms['gObjectEvents'] + i * stride + 8)
            for i in range(16)
            if g.u8(g.syms['gObjectEvents'] + i * stride) & 1}


def wait_map(g, name, frames=180):
    for _ in range(frames):
        if at(g, name):
            assert g.wait_warp_complete(map_id(name)), name
            g.frame(60)
            return
        g.frame(1)
    raise AssertionError(f'failed to enter {name}: {g.describe()}')


def test_story_walk():
    g = new_game(badge02=True, party=True)
    armed(g)
    assert bag(g, ITEM_SQUIRT_BOTTLE) == 1
    go_tree(g)
    assert talk(g, K.KEY_UP)['battle']
    assert wait_for_battle(g)
    enemy = battle_mon(g, 1)
    assert (enemy['species'], enemy['level']) == (185, 20), enemy
    fight(g, 'attack')
    assert drain(g) and g.flag('FLAG_POX_SUDOWOODO_CLEARED')
    assert bag(g, ITEM_SQUIRT_BOTTLE) == 0
    # The battle callback leaves this diagnostic flag stale on the field;
    # walk_demo's path helper expects zero before it checks each step.
    g.write(g.syms['gBattleTypeFlags'], 0, 4)
    print('Sudowoodo defeated; tree cleared', flush=True)

    navigate(g, (35, 0))
    g.hold(K.KEY_UP, 90)
    wait_map(g, 'Route37_hns')
    navigate(g, (17, 0))
    g.hold(K.KEY_UP, 24)
    wait_map(g, 'EcruteakCity_hns')
    shot(g, 'ecruteak_arrival.png')
    print('walked Route 36 -> Route 37 -> Ecruteak', flush=True)

    navigate(g, (22, 15))
    g.hold(K.KEY_UP, 60)
    wait_map(g, 'PlasticOx_BurnedTower')
    shot(g, 'tower_1f.png')
    navigate(g, (22, 18))
    assert talk(g, K.KEY_RIGHT)['dialogue']
    assert g.flag('FLAG_POX_BURNED_TOWER_FIRE_STONE')
    assert bag(g, FIRE_STONE, POCKET_ITEMS) == 1
    navigate(g, (24, 11))
    g.hold(K.KEY_UP, 48)
    wait_map(g, 'PlasticOx_BurnedTowerB1F')
    shot(g, 'tower_b1f.png')
    navigate(g, (8, 10))
    assert not g.flag('FLAG_POX_STORY_BURNED_TOWER')
    assert {1, 4, 5} <= visible_actor_ids(g), 'Morty and both sages must attend'
    original_wall = g.metatile_at(10, 9)
    scene = talk(g, K.KEY_UP, stop_at='For a moment')
    assert scene['stopped'] and not g.flag('FLAG_POX_STORY_BURNED_TOWER'), scene
    assert g.metatile_at(10, 9)[0] == 0x2A6
    shot(g, 'tower_memory.png')
    scene_text = []
    for _ in range(300):
        scene_text.append(g.text())
        if g.flag('FLAG_POX_STORY_BURNED_TOWER') and settle(g, 1):
            break
        g.tap(K.KEY_A, hold=2, wait=16)
    assert g.flag('FLAG_POX_STORY_BURNED_TOWER')
    dialogue = ' '.join(scene_text)
    assert 'MORTY: Sages, search throughout' in dialogue, dialogue
    assert 'SAGE: We will go, MORTY' in dialogue, dialogue
    assert 'there to help' in dialogue, dialogue
    assert not ({1, 4, 5} & visible_actor_ids(g)), 'Morty and sages must depart'
    assert g.metatile_at(10, 9) == original_wall
    shot(g, 'tower_after.png')
    print('Fire Stone obtained; basement memory finished; Morty returned', flush=True)

    navigate(g, (26, 8))
    g.hold(K.KEY_UP, 48)
    wait_map(g, 'PlasticOx_BurnedTower')
    navigate(g, (9, 21))
    caretaker = talk(g, K.KEY_UP)
    assert 'MORTY sent our sages' in ' '.join(caretaker['text']), caretaker
    navigate(g, (15, 21))
    g.hold(K.KEY_DOWN, 48)
    wait_map(g, 'EcruteakCity_hns')
    print('walked B1F -> 1F -> Ecruteak', flush=True)
    g.warp('PlasticOx_BurnedTowerB1F', 8, 10)
    g.frame(90)
    assert not ({1, 4, 5} & visible_actor_ids(g)), 'Departed actors must stay hidden'
    g.warp('PlasticOx_MortyGym', 5, 3)
    g.frame(90)
    assert talk(g, K.KEY_UP, stop_at='MORTY:')['stopped']
    assert wait_for_battle(g, 200), 'Morty did not accept the challenge after the tower scene'
    print('Morty Gym battle unlocked', flush=True)


def test_gym_gate():
    g = new_game(badge02=True, party=True)
    g.warp('PlasticOx_MortyGym', 5, 3)
    g.frame(90)
    result = talk(g, K.KEY_UP)
    assert result['dialogue'] and not result['battle']
    assert not g.flag('FLAG_POX_STORY_BURNED_TOWER')
    print('Morty Gym battle gated before tower scene', flush=True)


def test_basement_wild():
    g = new_game(badge02=True, party=True)
    g.flag('FLAG_POX_STORY_BURNED_TOWER', True)
    g.warp('PlasticOx_BurnedTowerB1F', 7, 10)
    g.frame(90)
    g.write(g.syms['sWildEncountersDisabled'], 0)
    for _ in range(160):
        g.tap(K.KEY_UP, hold=16, wait=10)
        if in_battle(g):
            break
        g.tap(K.KEY_DOWN, hold=16, wait=10)
        if in_battle(g):
            break
    assert in_battle(g), 'no B1F encounter after 160 corridor laps'
    assert wait_for_battle(g)
    enemy = battle_mon(g, 1)
    assert enemy['species'] in {109, 92, 19, 206, 358, 41, 302}, enemy
    assert 23 <= enemy['level'] <= 26, enemy
    print(f"B1F wild encounter: species {enemy['species']} level {enemy['level']}", flush=True)


if __name__ == '__main__':
    test_gym_gate()
    test_story_walk()
    test_basement_wild()
    print('Burned Tower playthrough: PASS', flush=True)
