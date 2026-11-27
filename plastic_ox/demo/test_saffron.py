#!/usr/bin/env python3
"""Saffron City, BRUNO's Fighting Dojo and Silph Co., played in mGBA.

Proves, with the D-pad wherever a transition is under test:
* the teleport guides are gone: the Dojo doorway (45,12), the Silph door
  (33,30) and the POKeMON CENTER door (18,38) all walk in and back out;
* in the Dojo the desk clerk reports an ADV OU clause the party breaks, BRUNO
  refuses to begin until it is fixed, the middle of the mat is free while a
  BLACK BELT battles whoever steps into his half, BRUNO's battle awards
  badge 7, and exactly one prize fighter can be taken afterwards;
* in Silph the receptionist heals, the stairs are closed on both floors, the
  three Rockets are met in order (lift, east corridor, west corridor) and only
  while their story battle is due, the east pad joins the two halves of 11F,
  stepping into the boardroom starts GIOVANNI's battle, and the terminal sets
  FLAG_POX_STORY_SILPH and brings the PRESIDENT back with the MASTER BALL;
* both purple-door houses open; a loss in Silph whites out to Saffron itself;
* a save made in either retired teleport room can walk out to the street;
* every Saffron line is unique and the dialogue rules hold (static check).
"""
import json
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pox_fixtures import ROOT, at, finish_trainer, game, shot  # noqa: E402
from test_sudowoodo_v1 import (POCKET_BALLS, bag, const, in_battle, opcode, run_code,  # noqa: E402
                               settle, talk)
from walk_demo import step_toward  # noqa: E402
from walk_leg1 import enter_warp, navigate  # noqa: E402
from walklib import K  # noqa: E402

CITY = 'SaffronCity_hns'
DOJO = 'SaffronCity_Dojo_Frlg'
LOBBY = 'SilphCo_1F_Frlg'
BOARD = 'SilphCo_11F_Frlg'
# The BLACK BELTS' halves of the Dojo mat (sight 3 from x=1 and x=11).
MAT = frozenset((x, 10) for x in (2, 3, 4, 8, 9, 10))
# Rocket 1's view down from the lobby lift.
LIFT = frozenset((22, y) for y in (5, 6, 7))
KEYS = {'UP': K.KEY_UP, 'DOWN': K.KEY_DOWN, 'LEFT': K.KEY_LEFT, 'RIGHT': K.KEY_RIGHT}


def mid(name):
    groups = json.loads((ROOT / 'data/maps/map_groups.json').read_text())
    return next((i, groups[n].index(name)) for i, n in enumerate(groups['group_order']) if name in groups[n])


def load(name):
    return json.loads((ROOT / f'data/maps/{name}/map.json').read_text())


def static_checks():
    inc = (ROOT / 'data/scripts/plastic_ox_saffron.inc').read_text()
    story = (ROOT / 'data/scripts/plastic_ox_story.inc').read_text()
    strings = re.findall(r'^(PoxSaffron_Text_\w+)::\n\t\.string "(.*)\$"', inc, re.M)
    for label in ['Bruno', 'Bruno_Defeat', 'SilphGrunt1', 'SilphGrunt1_Defeat', 'SilphGrunt2', 'SilphGrunt2_Defeat',
                  'SilphGrunt3', 'SilphGrunt3_Defeat', 'Giovanni', 'Giovanni_Defeat', 'BlackthornRoad']:
        strings.append(('Pox_Text_' + label,
                        re.search(r'^Pox_Text_' + label + r'::\n\t\.string "(.*)\$"', story, re.M)[1]))
    bodies = [body for _label, body in strings]
    assert len(strings) > 60 and len(set(bodies)) == len(bodies), 'two Saffron lines share their text'
    flat = {label: re.sub(r'\\[np]', ' ', body) for label, body in strings}
    for label, body in flat.items():
        low = body.lower()
        assert 'convergence' not in low and 'sabrina' not in low and 'psychic' not in low, label
        assert 'BILL' not in body, label
        for line in re.split(r'\\[np]', dict(strings)[label]):
            assert len(line) <= 36, (label, line)
    # Only the terminal names the system; no resident or Rocket does.
    named = [label for label, body in flat.items() if 'ADAPTIVE' in body]
    assert named == ['PoxSaffron_Text_Core1'], named
    assert 'did not move a single road' in flat['Pox_Text_Giovanni'] and 'FUJI' in flat['Pox_Text_Giovanni']
    assert 'RETAINED' in flat['PoxSaffron_Text_Core2']
    print(f'ok  {len(strings)} Saffron lines: all unique, no Bill/Sabrina/convergence, system named once', flush=True)

    city = load(CITY)
    scripts = [o['script'] for o in city['object_events']]
    assert not any(s in scripts for s in ('Pox_BrunoGuide', 'Pox_SilphGuide')), scripts
    assert len([s for s in scripts if not s.startswith('PoxRegion_')]) == 9
    assert len(set(scripts)) == len(scripts), 'two Saffron residents share a script'
    for label in ('Pox_BrunoGuide', 'Pox_SilphGuide', 'Pox_BrunoGymExit', 'Pox_SilphExit', 'SaffronCity_EventScript_Npc'):
        assert label not in story + inc + (ROOT / f'data/maps/{CITY}/scripts.inc').read_text(), label
    warps = [(w['x'], w['y'], w['dest_map']) for w in city['warp_events']]
    assert warps[3:] == [(45, 12, 'MAP_SAFFRON_CITY_DOJO'), (33, 30, 'MAP_SILPH_CO_1F'),
                         (18, 38, 'MAP_POKEMON_CENTER_KANTO_HNS'), (21, 21, 'MAP_SAFFRON_CITY_HOUSE'),
                         (47, 38, 'MAP_SAFFRON_CITY_MR_PSYCHICS_HOUSE')], warps
    assert city['layout'] == 'LAYOUT_SAFFRON_CITY_HNS'
    print('ok  nine residents, no teleport guides, five real doors', flush=True)

    party = (ROOT / 'src/data/trainers.party').read_text()
    block = lambda t: party.split(f'=== TRAINER_PLASTIC_OX_{t} ===', 1)[1].split('\n=== ', 1)[0]
    assert 'Pic: Elite Four Bruno Frlg' in block('BRUNO') and 'Class: Leader' in block('BRUNO')
    team = re.findall(r'^(\w+) @', block('BRUNO'), re.M)
    assert team == ['Zapdos', 'Ludicolo', 'Blaziken', 'Heracross', 'Regirock', 'Celebi'], team
    assert 'Rain Dance' in block('BRUNO') and 'Class: Rocket Boss' in block('GIOVANNI')
    for n in (1, 2, 3):
        assert 'Class: Team Rocket Frlg' in block(f'SILPHGRUNT{n}') and 'Aqua' not in block(f'SILPHGRUNT{n}')
    special = (ROOT / 'src/field_specials.c').read_text()
    body = special.split('static u16 CheckADVTierGymRules(enum EvolutionTier maxTier)', 1)[1].split('\n}\n', 1)[0]
    assert 'CheckRustboroGymLittleCupRules' not in body, 'the OU check must not apply the Little Cup bans'
    assert 'CheckSaffronGymOURules(void)    { return CheckADVTierGymRules(EVO_TIER_OU); }' in special
    print('ok  BRUNO has his requested six; GIOVANNI is the ROCKET BOSS; grunts are Team Rocket; OU check is OU', flush=True)


def clean(text):
    """Message-buffer text as prose: control codes become spaces."""
    text = re.sub(r'\{[a-z_]+\}|<[0-9A-F]{2}>', ' ', text).replace('。', '.').replace('ー', '-').replace("\\'", "'")
    return re.sub(r'\s+', ' ', text)


def walk_in(g, approach, key, name, stage):
    enter_warp(g, approach, key, mid(name), stage)
    assert at(g, name), (stage, g.describe())


def pos(g):
    return g.state()['x'], g.state()['y']


def walk_until_spotted(g, key, steps=14):
    """Walk one way until a trainer's sight script starts its battle. Returns
    the text boxes shown and the tile the player stood on when spotted."""
    seen, where = [], None
    g.clear_text()
    for _ in range(steps * 20):
        if in_battle(g):
            return seen, where
        t = clean(g.text())
        if t:
            if not seen or seen[-1] != t:
                seen.append(t)
            if where is None:
                where = pos(g)
            g.tap(K.KEY_A, hold=2, wait=10)
        elif where is None:
            g.tap(KEYS[key], hold=8, wait=16)
        else:
            g.frame(10)
    raise AssertionError(('never spotted', g.describe(), seen))


def battle_id(g):
    g.frame(120)
    return g.u16(g.syms['gTrainerBattleParameter'] + 2)


def win(g):
    finish_trainer(g, True)
    settle(g)
    # The battle callback leaves this diagnostic flag stale on the field; the
    # path helper expects zero before each step.
    g.write(g.syms['gBattleTypeFlags'], 0, 4)


def say(g, stand, key, **kw):
    navigate(g, stand)
    r = talk(g, KEYS[key], **kw)
    r['text'] = [clean(t) for t in r['text']]
    return ' '.join(r['text']), r


def bump(g, stand, key, fragment, avoid=frozenset()):
    """Step from 'stand' onto a closed staircase: text, then pushed back off."""
    navigate(g, stand, avoid)
    here = (g.state()['group'], g.state()['num'])
    g.clear_text()
    for _ in range(3):                      # the first press may only turn the player
        g.tap(KEYS[key], hold=8, wait=30)
        if g.text():
            break
    seen = ''
    for _ in range(60):
        seen += ' ' + clean(g.text())
        g.tap(K.KEY_A, hold=2, wait=12)
    settle(g)
    assert fragment in seen, (fragment, seen)
    assert (g.state()['group'], g.state()['num']) == here, g.describe()


def set_move(g, slot, move):
    assert run_code(g, opcode(g, 'setmonmove') + struct.pack('<BBH', 0, slot, const(move, 'moves.h')))


def hp(g, i=0):
    stride = g.sizes['gParties'] // 24
    a = g.syms['gParties'] + i * stride + stride - 14
    return g.u16(a), g.u16(a + 2), a


def city(g):
    g.warp(CITY, 33, 33)
    g.frame(90)
    text, r = say(g, (35, 32), 'UP')
    assert 'red at the door' in text and at(g, CITY) and not r['battle'], r
    text, _ = say(g, (27, 13), 'UP')
    assert 'METEOR FALLS' in text and 'Nobody asks' in text and at(g, CITY), text
    text, _ = say(g, (47, 15), 'UP')
    assert 'FIGHTING DOJO' in text and 'BRUNO' in text, text
    text, _ = say(g, (52, 13), 'UP')
    assert 'dust sheets' in text and at(g, CITY), text
    shot(g, 'saffron_dojo_street')
    print('ok  residents and signs talk; nobody teleports the player', flush=True)

    walk_in(g, (18, 39), 'UP', 'PokemonCenter_Kanto_hns', 'city -> center')
    walk_in(g, (7, 8), 'DOWN', CITY, 'center -> city')
    assert pos(g) in ((18, 38), (18, 39)), g.describe()
    print('ok  (18,38) is the POKeMON CENTER, both ways', flush=True)

    walk_in(g, (21, 22), 'UP', 'SaffronCity_House_Frlg', 'city -> west house')
    text, _ = say(g, (3, 4), 'RIGHT')
    assert 'counting trains' in text, text
    text, _ = say(g, (5, 3), 'DOWN')
    assert 'RENT IS STILL DUE' in text, text
    walk_in(g, (4, 7), 'DOWN', CITY, 'west house -> city')
    assert pos(g) in ((21, 21), (21, 22)), g.describe()
    walk_in(g, (47, 39), 'UP', 'SaffronCity_MrPsychicsHouse_Frlg', 'city -> south house')
    text, _ = say(g, (8, 4), 'LEFT')
    assert 'left hand' in text, text
    walk_in(g, (4, 7), 'DOWN', CITY, 'south house -> city')
    assert pos(g) in ((47, 38), (47, 39)), g.describe()
    print('ok  both houses (21,21) and (47,38) open, both ways, with their residents', flush=True)


def dojo(g):
    walk_in(g, (45, 13), 'UP', DOJO, 'city -> dojo')
    shot(g, 'saffron_dojo')
    walk_in(g, (6, 14), 'DOWN', CITY, 'dojo -> city')
    assert pos(g) in ((45, 12), (45, 13)), g.describe()
    walk_in(g, (45, 13), 'UP', DOJO, 'city -> dojo again')
    print('ok  (45,12) is the FIGHTING DOJO, both ways', flush=True)

    text, _ = say(g, (7, 13), 'RIGHT')
    assert 'OU rules' in text and 'in order' in text, text
    # DOUBLE TEAM, MINIMIZE and SWAGGER are removed from the ROM; the OHKO
    # clause is the move ban a player can actually break.
    set_move(g, 3, 'MOVE_FISSURE')
    text, _ = say(g, (7, 13), 'RIGHT')
    assert 'FISSURE' in text.upper() and "isn't allowed" in text, text
    navigate(g, (6, 12))
    for _ in range(5):                      # straight up the middle of the mat
        g.tap(K.KEY_UP, hold=8, wait=16)
        assert not in_battle(g), 'a BLACK BELT stopped a challenger on the middle of the mat'
    text, r = say(g, (6, 6), 'UP')
    assert 'Not on this floor' in text and not r['battle'], r
    assert not g.flag('FLAG_BADGE07_GET')
    set_move(g, 3, 'MOVE_TOXIC')
    print('ok  desk reports the banned move; BRUNO will not begin until it is gone', flush=True)

    text, _ = say(g, (5, 4), 'UP')
    assert 'not yours to touch yet' in text and not g.flag('FLAG_POX_DOJO_PRIZE'), text
    text, _ = say(g, (2, 8), 'LEFT')
    assert 'Forty-one' in text, text

    navigate(g, (4, 11), MAT)
    texts, where = walk_until_spotted(g, 'UP')
    assert where == (4, 10) and 'my half of the mat' in ' '.join(texts), (where, texts)
    assert battle_id(g) == g.const('TRAINER_PLASTIC_OX_DOJO_KENJI')
    win(g)
    navigate(g, (4, 11))
    navigate(g, (4, 9))
    assert not in_battle(g), 'a beaten BLACK BELT battled again'
    print('ok  BLACK BELT KENJI battles whoever steps into his half, once', flush=True)

    navigate(g, (6, 6))
    r = talk(g, K.KEY_UP, max_taps=400)
    assert r['battle'] and 'skip the tea' in clean(' '.join(r['text'])), r
    assert battle_id(g) == g.const('TRAINER_PLASTIC_OX_BRUNO')
    assert not g.flag('FLAG_BADGE07_GET'), 'badge awarded before victory'
    shot(g, 'saffron_bruno_battle')
    win(g)
    assert g.flag('FLAG_BADGE07_GET') and at(g, DOJO)
    text, r = say(g, (6, 6), 'UP')
    assert 'whenever you wish' in text and 'still waiting' in text and not r['battle'], r
    text, _ = say(g, (7, 13), 'RIGHT')
    assert 'in the book' in text, text
    print('ok  BRUNO battles as TRAINER_PLASTIC_OX_BRUNO and awards badge 7', flush=True)

    text, _ = say(g, (5, 4), 'UP', max_taps=400)
    assert 'HITMONLEE' in text and 'took HITMONLEE' in text, text
    assert g.flag('FLAG_POX_DOJO_PRIZE')
    text, _ = say(g, (7, 4), 'UP')
    assert 'stays with the hall' in text, text
    text, _ = say(g, (6, 6), 'UP')
    assert 'still waiting' not in text, text
    g.warp(DOJO, 6, 12)
    g.frame(90)
    navigate(g, (6, 4))                     # both prize stands are empty now
    assert not talk(g, K.KEY_LEFT)['text'] and not talk(g, K.KEY_RIGHT)['text']
    print('ok  one prize fighter (HITMONLEE) taken; the other ball is put away', flush=True)
    walk_in(g, (6, 14), 'DOWN', CITY, 'dojo -> city, with the badge')


def silph(g):
    walk_in(g, (33, 31), 'UP', LOBBY, 'city -> silph')
    shot(g, 'saffron_silph_lobby')
    walk_in(g, (8, 20), 'DOWN', CITY, 'silph -> city')
    assert pos(g) in ((33, 30), (33, 31)), g.describe()
    walk_in(g, (33, 31), 'UP', LOBBY, 'city -> silph again')
    print('ok  (33,30) is SILPH CO., both ways', flush=True)

    cur, top, addr = hp(g)
    g.write(addr, 1, 2)
    text, _ = say(g, (3, 9), 'UP', max_taps=400)
    assert 'first-aid cabinet' in text and 'standing in front of it' in text, text
    assert hp(g)[0] == top, 'the receptionist did not heal the party'
    print('ok  receptionist heals', flush=True)

    navigate(g, (20, 7), LIFT)             # the fountain fills the tiles south of (22,7)
    texts, where = walk_until_spotted(g, 'RIGHT')
    assert where[0] == 22 and 5 <= where[1] <= 7 and 'double time' in ' '.join(texts), (where, texts)
    assert battle_id(g) == g.const('TRAINER_PLASTIC_OX_SILPHGRUNT1')
    assert not g.flag('FLAG_POX_HIDE_SILPH_GRUNT_1')
    win(g)
    assert g.flag('FLAG_POX_HIDE_SILPH_GRUNT_1') and at(g, LOBBY)
    bump(g, (31, 3), 'UP', 'chained from the other side')
    assert at(g, LOBBY) and pos(g) == (31, 3), g.describe()
    walk_in(g, (22, 4), 'UP', BOARD, 'lobby lift -> 11F')
    shot(g, 'saffron_silph_11f')
    print('ok  Rocket 1 guards the lift; the stairs are closed; the lift goes to 11F', flush=True)

    bump(g, (7, 3), 'UP', 'wedged a chair')
    navigate(g, (15, 9))
    texts, where = walk_until_spotted(g, 'DOWN')
    assert where == (15, 12) and 'server room' in ' '.join(texts), (where, texts)
    assert battle_id(g) == g.const('TRAINER_PLASTIC_OX_SILPHGRUNT2')
    win(g)
    assert g.flag('FLAG_POX_HIDE_SILPH_GRUNT_2')
    navigate(g, (16, 18))
    step_toward(g, (16, 18), (16, 19))
    for _ in range(240):
        if pos(g)[0] <= 2:
            break
        g.frame(2)
    g.frame(90)
    assert at(g, BOARD) and pos(g) == (2, 5), ('east pad', g.describe())
    print('ok  Rocket 2 holds the east corridor; the pad crosses to the boardroom side', flush=True)

    navigate(g, (1, 9))
    texts, where = walk_until_spotted(g, 'DOWN')
    assert where == (1, 12) and 'read the logs' in ' '.join(texts), (where, texts)
    assert battle_id(g) == g.const('TRAINER_PLASTIC_OX_SILPHGRUNT3')
    win(g)
    assert g.flag('FLAG_POX_HIDE_SILPH_GRUNT_3')

    navigate(g, (5, 15))
    texts, _where = walk_until_spotted(g, 'UP')
    assert 'did not move a single road' in ' '.join(texts), texts
    assert battle_id(g) == g.const('TRAINER_PLASTIC_OX_GIOVANNI')
    assert not g.flag('FLAG_POX_HIDE_SILPH_GIOVANNI') and not g.flag('FLAG_POX_STORY_SILPH')
    shot(g, 'saffron_giovanni_battle')
    win(g)
    g.frame(120)
    assert g.flag('FLAG_POX_HIDE_SILPH_GIOVANNI') and pos(g) == (6, 12), g.describe()
    navigate(g, (6, 14))                    # the trigger is spent
    navigate(g, (6, 12))
    assert not in_battle(g)
    print('ok  Rocket 3, then GIOVANNI on stepping into the boardroom', flush=True)

    assert not g.flag('FLAG_POX_STORY_SILPH')
    text, _ = say(g, (5, 8), 'UP', max_taps=600)
    assert 'ADAPTIVE TRAINER SYSTEM' in text and 'RETAINED' in text and 'lift starts to run' in text, text
    assert g.flag('FLAG_POX_STORY_SILPH')
    shot(g, 'saffron_silph_core_done')
    text, _ = say(g, (5, 8), 'UP')
    assert 'BATTLE ANALYSIS: CONTINUING' in text, text
    text, _ = say(g, (9, 10), 'UP', max_taps=400)
    assert 'display case' in text, text
    assert g.flag('FLAG_POX_SILPH_MASTER_BALL')
    assert bag(g, const('ITEM_MASTER_BALL', 'items.h'), POCKET_BALLS) == 1
    text, _ = say(g, (9, 10), 'UP')
    assert 'maintenance' in text, text
    text, _ = say(g, (11, 10), 'UP')
    assert 'STILL LOCKED IN' in text, text
    print('ok  terminal sets FLAG_POX_STORY_SILPH; PRESIDENT hands over the MASTER BALL once', flush=True)

    navigate(g, (2, 6))
    step_toward(g, (2, 6), (2, 5))
    for _ in range(240):
        if pos(g)[0] >= 15:
            break
        g.frame(2)
    g.frame(90)
    assert pos(g) == (16, 19), ('west pad', g.describe())
    walk_in(g, (13, 4), 'UP', LOBBY, '11F lift -> lobby')
    text, _ = say(g, (3, 9), 'UP', max_taps=400)
    assert 'reopens on Monday' in text, text
    walk_in(g, (8, 20), 'DOWN', CITY, 'silph -> city, resolved')
    text, _ = say(g, (35, 32), 'UP')
    assert 'went green' in text, text
    print('ok  walked back out by pad, lift and door; the street noticed, vaguely', flush=True)


def whiteout():
    """Losing inside Silph comes back to Saffron, healed, at the Center door."""
    g = game()
    g.flag('FLAG_BADGE06_GET', True)
    g.flag('FLAG_POX_STORY_SPACE_CENTER', True)
    g.warp(CITY, 33, 33)                    # entering the city sets the respawn
    g.frame(90)
    walk_in(g, (33, 31), 'UP', LOBBY, 'city -> silph')
    navigate(g, (20, 7), LIFT)
    walk_until_spotted(g, 'RIGHT')
    assert battle_id(g) == g.const('TRAINER_PLASTIC_OX_SILPHGRUNT1')
    finish_trainer(g, False)
    settle(g)
    g.write(g.syms['gBattleTypeFlags'], 0, 4)
    g.frame(120)
    assert at(g, CITY) and pos(g) == (18, 39), ('whiteout', g.describe())
    cur, top, _addr = hp(g)
    assert cur == top and not g.flag('FLAG_POX_HIDE_SILPH_GRUNT_1')
    print('ok  a loss in Silph returns to Saffron (18,39), healed', flush=True)


def dormant_and_retired():
    # A Rocket spots the player only while his own story battle is due.
    g = game()
    g.flag('FLAG_BADGE06_GET', True)
    g.flag('FLAG_POX_STORY_SPACE_CENTER', True)
    g.warp(BOARD, 15, 5)
    g.frame(90)
    navigate(g, (15, 17))
    assert not in_battle(g), 'Rocket 2 battled before Rocket 1 was beaten'
    text, r = say(g, (15, 12), 'RIGHT')
    assert 'Not my floor' in text and not r['battle'], r
    g.warp(BOARD, 5, 18)
    g.frame(90)
    navigate(g, (5, 15))
    g.tap(K.KEY_UP, hold=8, wait=30)
    seen = ''
    for _ in range(80):
        seen += ' ' + clean(g.text())
        g.tap(K.KEY_A, hold=2, wait=12)
    settle(g)
    assert 'left some of my people standing' in seen and not in_battle(g), seen
    text, _ = say(g, (5, 8), 'UP')
    assert 'watching you' in text and not g.flag('FLAG_POX_STORY_SILPH'), text
    print('ok  out of order: Rocket 2 is dormant, GIOVANNI waits, the terminal stays locked', flush=True)

    for room, door, back in [('PlasticOx_BrunoGym', (5, 18), (45, 13)), ('PlasticOx_Silph', (7, 8), (33, 31))]:
        g.warp(room, 5, 17) if room.endswith('Gym') else g.warp(room, 5, 8)
        g.frame(90)
        walk_in(g, door, 'DOWN', CITY, room + ' -> city')
        assert pos(g) in (back, (back[0], back[1] - 1)), (room, g.describe())
    print('ok  both retired teleport rooms walk out to their real doors', flush=True)


def main():
    static_checks()
    g = game()
    g.flag('FLAG_BADGE06_GET', True)
    g.flag('FLAG_POX_STORY_SPACE_CENTER', True)
    city(g)
    dojo(g)
    silph(g)
    whiteout()
    dormant_and_retired()
    print('PASS: Saffron, the Fighting Dojo and Silph Co.', flush=True)


if __name__ == '__main__':
    main()
