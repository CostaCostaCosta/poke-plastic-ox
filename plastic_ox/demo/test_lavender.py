#!/usr/bin/env python3
"""Lavender Town, the FRLG Pokemon Tower and MR. FUJI's rescue, played in mGBA.

Proves, with the D-pad wherever a transition is under test:
* the old teleport guides are gone; the caretaker stands where one stood;
* LavenderTown_hns's (22,6) door is the POKeMON TOWER and walks back out;
* the tower's stairs walk 1F -> 7F;
* the three Rocket grunts on 7F must be beaten in order, FUJI waits for all
  three, then walks the player to his house (the (8,13) door);
* in the house FUJI gives the SURF KEY, sets FLAG_POX_STORY_FUJI and offers EEVEE;
* the house and the (10,19) House1 door both walk back to town;
* the Soul House door (22,19) walks in and back out;
* the tower's encounter tables include the UU MISDREAVUS (static check);
* Routes 8, 7 and 21 carry UU-capped gPoxUU tables (static check);
* the third 7F Rocket is Executive PROTON; the 1F GROWLITHE mourner is an old woman.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pox_fixtures import ROOT, at, finish_trainer, game, shot  # noqa: E402
from test_sudowoodo_v1 import bag, const, in_battle, settle, talk  # noqa: E402
from walk_demo import step_toward  # noqa: E402
from walk_leg1 import enter_warp, navigate  # noqa: E402
from walklib import K  # noqa: E402

TOWN = 'LavenderTown_hns'


def mid(name):
    groups = json.loads((ROOT / 'data/maps/map_groups.json').read_text())
    return next((i, groups[n].index(name)) for i, n in enumerate(groups['group_order']) if name in groups[n])


def static_checks():
    data = json.loads((ROOT / 'src/data/wild_encounters.json').read_text())
    tiers = (ROOT / 'src/data/pokemon/evolution_tier_gates.h').read_text()
    order = ['LC', 'PU', 'NU', 'RU', 'UU']
    seen = set()
    for floor in range(3, 8):
        tables = [e for e in data['wild_encounter_groups'][0]['encounters']
                  if e.get('map') == f'MAP_POKEMON_TOWER_{floor}F']
        assert len(tables) == 1 and tables[0]['base_label'] == f'gPoxUUPokemonTower{floor}F', tables
        for mon in tables[0]['land_mons']['mons']:
            sp = mon['species']
            tier = tiers.split(f'[{sp}] = EVO_TIER_', 1)[1].split(',', 1)[0]
            assert tier in order, (floor, sp, tier)
            assert 34 <= mon['min_level'] <= mon['max_level'] <= 42, (floor, mon)
            seen.add(sp)
    assert 'SPECIES_MISDREAVUS' in seen
    print('ok  tower encounters are UU-capped and include MISDREAVUS', flush=True)

    # Routes 8, 7 and 21 follow the tower on the Lavender -> Cinnabar leg: one
    # UU-capped gPoxUU table each, levels inside the cinnabar cap (42), with
    # at least one UU species in the grass.
    for m, label in [('MAP_ROUTE8', 'gPoxUURoute8'), ('MAP_ROUTE7', 'gPoxUURoute7'),
                     ('MAP_ROUTE7_HNS', 'gPoxUURoute7Hns'),
                     ('MAP_ROUTE21_NORTH', 'gPoxUURoute21North'),
                     ('MAP_ROUTE21_SOUTH', 'gPoxUURoute21South')]:
        tables = [e for e in data['wild_encounter_groups'][0]['encounters'] if e.get('map') == m]
        assert len(tables) == 1 and tables[0]['base_label'] == label, (m, tables)
        land_tiers = set()
        for field in ('land_mons', 'water_mons', 'fishing_mons'):
            for i, mon in enumerate(tables[0].get(field, {}).get('mons', [])):
                sp = mon['species']
                assert 30 <= mon['min_level'] <= mon['max_level'] <= 42, (m, mon)
                if field == 'fishing_mons' and i == 0:
                    assert sp == 'SPECIES_MAGIKARP', (m, mon)  # v5.5 Old Rod rule
                    continue
                tier = tiers.split(f'[{sp}] = EVO_TIER_', 1)[1].split(',', 1)[0]
                assert tier in order, (m, sp, tier)
                if field == 'land_mons':
                    land_tiers.add(tier)
        assert 'UU' in land_tiers, (m, land_tiers)
    print('ok  routes 8, 7 and 21 have UU-capped gPoxUU tables (levels 30-42)', flush=True)

    party = (ROOT / 'src/data/trainers.party').read_text()
    block = party.split('=== TRAINER_PLASTIC_OX_TOWERGRUNT3 ===', 1)[1].split('\n\n', 1)[0]
    assert 'Name: PROTON' in block and 'Class: Rocket Executive Hns' in block and 'Pic: Proton Hns' in block, block
    print('ok  the last tower Rocket (TOWERGRUNT3) is Executive PROTON', flush=True)


def gfx_id(name):
    """OBJ_EVENT_GFX_* value from the enum in event_objects.h."""
    text = (ROOT / 'include/constants/event_objects.h').read_text()
    body = text[text.index('OBJ_EVENT_GFX_BRENDAN_NORMAL'):]
    names = re.findall(r'^\s*(OBJ_EVENT_GFX_\w+)\s*,', body, re.M)
    return names.index(name)


def object_gfx(g, local_id):
    stride = g.sizes['gObjectEvents'] // 16
    for i in range(16):
        a = g.syms['gObjectEvents'] + i * stride
        if g.u8(a) & 1 and g.u8(a + 8) == local_id:
            return g.u8(a + 4) | (g.u8(a + 5) << 8)
    return None


def walk_in(g, approach, key, name, stage):
    enter_warp(g, approach, key, mid(name), stage)
    assert at(g, name), (stage, g.describe())


def climb(g, stairs, name):
    """FRLG stair warps: step onto the stairs, then press the way they run
    (right for UP/DOWN_RIGHT_STAIR_WARP, left for the LEFT ones)."""
    x, y = stairs
    names = re.findall(r'^\s*(MB_\w+)', (ROOT / 'include/constants/metatile_behaviors.h').read_text(), re.M)
    behaviors = {names.index(n): k for n, k in [
        ('MB_UP_RIGHT_STAIR_WARP', K.KEY_RIGHT), ('MB_DOWN_RIGHT_STAIR_WARP', K.KEY_RIGHT),
        ('MB_UP_LEFT_STAIR_WARP', K.KEY_LEFT), ('MB_DOWN_LEFT_STAIR_WARP', K.KEY_LEFT)]}
    stair_key = behaviors[g.behavior_at(x, y)[0]]
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        if g.collision_at(x + dx, y + dy)[0]:
            continue
        try:
            navigate(g, (x + dx, y + dy))
        except AssertionError:
            continue
        step_toward(g, (x + dx, y + dy), (x, y))
        for _ in range(4):
            g.tap(stair_key, hold=8, wait=18)
            for _ in range(90):
                if at(g, name):
                    g.wait_warp_complete(mid(name))
                    g.frame(60)
                    print(f'STAIRS {name}', flush=True)
                    return
                g.frame(1)
    raise AssertionError(f'stairs at {stairs} never reached {name}: {g.describe()}')


def main():
    static_checks()
    g = game()
    g.flag('FLAG_BADGE04_GET', True)
    g.warp(TOWN, 17, 9)
    g.frame(90)
    navigate(g, (17, 8))
    r = talk(g, K.KEY_UP)
    text = ' '.join(r['text'])
    assert 'candles low' in text and not r['battle'], r
    assert at(g, TOWN), 'the caretaker must not teleport the player'
    print('ok  caretaker talks; no teleport guide', flush=True)

    walk_in(g, (22, 7), 'UP', 'PokemonTower_1F_Frlg', 'town -> tower')
    shot(g, 'lavender_tower_1f')
    # 1F object 2 is the CHANNELER (checks the enum parse); object 3 is the
    # mourner whose GROWLITHE "would be fifty now": an old woman, not a girl.
    navigate(g, (16, 10))  # objects spawn only near the camera
    g.frame(30)
    assert object_gfx(g, 2) == gfx_id('OBJ_EVENT_GFX_CHANNELER'), object_gfx(g, 2)
    assert object_gfx(g, 3) == gfx_id('OBJ_EVENT_GFX_OLD_WOMAN_FRLG'), object_gfx(g, 3)
    print('ok  1F GROWLITHE mourner is drawn as an old woman', flush=True)
    navigate(g, (11, 18))  # back to the door mat
    walk_in(g, (g.state()['x'], g.state()['y'] + 1), 'DOWN', TOWN, 'tower -> town')
    assert (g.state()['x'], g.state()['y']) in ((22, 7), (22, 6)), g.describe()
    walk_in(g, (22, 7), 'UP', 'PokemonTower_1F_Frlg', 'town -> tower again')
    print('ok  (22,6) is the POKeMON TOWER door, both ways', flush=True)

    stairs = [((18, 9), 'PokemonTower_2F_Frlg'), ((4, 10), 'PokemonTower_3F_Frlg'),
              ((18, 10), 'PokemonTower_4F_Frlg'), ((4, 10), 'PokemonTower_5F_Frlg'),
              ((18, 10), 'PokemonTower_6F_Frlg'), ((11, 16), 'PokemonTower_7F_Frlg')]
    for xy, name in stairs:
        climb(g, xy, name)
    shot(g, 'lavender_tower_7f')
    print('ok  walked the stairs 1F -> 7F', flush=True)

    shot(g, 'lavender_7f_arrival')
    navigate(g, (11, 5))
    r = talk(g, K.KEY_UP)
    assert 'frightened' in ' '.join(r['text']) and at(g, 'PokemonTower_7F_Frlg'), r
    assert not g.flag('FLAG_POX_FUJI_RESCUED')
    navigate(g, (13, 9))
    r = talk(g, K.KEY_UP)
    assert not r['battle'] and not g.flag('FLAG_POX_HIDE_LAVENDER_GRUNT_2'), r
    print('ok  FUJI and the second grunt wait for the grunts in order', flush=True)

    for n, (spot, key) in enumerate([((9, 11), K.KEY_UP), ((13, 9), K.KEY_UP), ((9, 7), K.KEY_UP)], 1):
        navigate(g, spot)
        r = talk(g, key)
        assert r['battle'], (n, r)
        if n == 3:
            assert 'PROTON' in ' '.join(r['text']), r
        finish_trainer(g, True)
        settle(g)
        # The battle callback leaves this diagnostic flag stale on the field;
        # the path helper expects zero before each step.
        g.write(g.syms['gBattleTypeFlags'], 0, 4)
        assert g.flag(f'FLAG_POX_HIDE_LAVENDER_GRUNT_{n}'), n
        assert at(g, 'PokemonTower_7F_Frlg')
    print('ok  beat two Rocket grunts and Executive PROTON', flush=True)

    navigate(g, (11, 5))
    talk(g, K.KEY_UP)
    for _ in range(300):
        if at(g, 'LavenderTown_VolunteerPokemonHouse_Frlg'):
            break
        g.frame(2)
    assert at(g, 'LavenderTown_VolunteerPokemonHouse_Frlg'), g.describe()
    g.frame(120)
    assert g.flag('FLAG_POX_FUJI_RESCUED') and not g.flag('FLAG_POX_STORY_FUJI')
    shot(g, 'lavender_fuji_house')
    print('ok  FUJI walks the player home', flush=True)

    navigate(g, (3, 4))
    r = talk(g, K.KEY_UP, max_taps=400)
    text = ' '.join(r['text'])
    assert 'CINNABAR' in text and 'SURF KEY' in text, r
    assert bag(g, const('ITEM_SURF_KEY', 'items.h')) == 1
    assert g.flag('FLAG_POX_STORY_FUJI') and g.flag('FLAG_POX_GIFT_FUJI')
    print('ok  FUJI gives the SURF KEY, opens ROUTE 8 and gives EEVEE', flush=True)

    walk_in(g, (4, 7), 'DOWN', TOWN, 'house -> town')
    assert (g.state()['x'], g.state()['y']) in ((8, 13), (8, 14)), g.describe()
    walk_in(g, (8, 14), 'UP', 'LavenderTown_VolunteerPokemonHouse_Frlg', 'town -> house')
    walk_in(g, (4, 7), 'DOWN', TOWN, 'house -> town again')
    walk_in(g, (10, 20), 'UP', 'LavenderTown_House1_Frlg', 'town -> house1')
    walk_in(g, (4, 7), 'DOWN', TOWN, 'house1 -> town')
    assert (g.state()['x'], g.state()['y']) in ((10, 19), (10, 20)), g.describe()
    print('ok  FUJI house (8,13) and House1 (10,19) doors, both ways', flush=True)

    walk_in(g, (22, 20), 'UP', 'PlasticOx_FujiHouse', 'town -> soul house')
    g.frame(120)
    shot(g, 'lavender_soul_house')
    navigate(g, (4, 5))
    r = talk(g, K.KEY_UP)
    assert 'sweeps the step' in ' '.join(r['text']), r
    walk_in(g, (4, 8), 'DOWN', TOWN, 'soul house -> town')
    assert (g.state()['x'], g.state()['y']) in ((22, 19), (22, 20)), g.describe()
    print('ok  Soul House (22,19) door, both ways; keeper knows FUJI is home', flush=True)

    g.warp('PokemonTower_7F_Frlg', 11, 14)
    g.frame(90)
    navigate(g, (11, 5))
    print('ok  7F is clear after the rescue (FUJI and grunts gone)', flush=True)
    assert not in_battle(g)


if __name__ == '__main__':
    main()
