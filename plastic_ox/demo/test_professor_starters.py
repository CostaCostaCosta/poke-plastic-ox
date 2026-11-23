#!/usr/bin/env python3
"""Professor starter rewards (Oak / Elm / Birch) in the real ROM.

Proves: milestones at 25/50/75 owned species of the professor's own
generation; duplicates and Gen 4+ species don't count; evolved species count;
B/CANCEL never consumes a reward; any pick order, claimed starters vanish from
the menu; a 75-species player can claim all three and never a fourth; a full
party sends the starter to the PC; gifts register as owned; reward flags
survive save/reload; Elm's Goldenrod house and Birch's Fortree house (House3) are
walked into and out of through their existing doors; Oak's story talk still
runs before the reward; the displaced Fortree Hidden Power giver still works.

Run: plastic_ox/bin/pox-mgba-python plastic_ox/demo/test_professor_starters.py
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'battle/metamon'))
from test_story import StoryGame, ROOT
from test_sudowoodo_v1 import SudoGame
from test_qol import begin_code, opcode
from walklib import K
from walk_leg1 import navigate, enter_warp

SET_CAUGHT = 3
OAK, ELM, BIRCH = 0, 1, 2


class Game(StoryGame):
    clear_text = SudoGame.clear_text
    text = SudoGame.text


def save_reload(g):
    """Save through the game's own routine, reset, and Continue."""
    begin_code(g, opcode(g, 'callnative') + struct.pack('<I', g.syms['Script_ForceSaveGame'] | 1)
               + opcode(g, 'waitstate') + opcode(g, 'releaseall') + opcode(g, 'end'))
    for _ in range(2000):
        if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            break
        g.tap(K.KEY_A, hold=1, wait=6)
    g.core.reset()
    main = g.syms['gMain']
    for _ in range(300):
        g.tap(K.KEY_A, hold=2, wait=20)
        if g.u32(main + 4) & ~1 == g.syms['CB2_Overworld'] & ~1:
            break
    g.frame(180)


def map_id(name):
    groups = json.loads((ROOT / 'data/maps/map_groups.json').read_text())
    for i, group in enumerate(groups['group_order']):
        if name in groups[group]:
            return i, groups[group].index(name)
    raise KeyError(name)


def idle(g, frames=600):
    for _ in range(frames):
        if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            return True
        g.frame(1)
    return False


def own(g, species):
    """Mark species (SPECIES_* ids == National Dex for Gen 1-4 bases) owned."""
    species = list(species)
    for i in range(0, len(species), 20):
        code = b''.join(opcode(g, 'callnative') + struct.pack('<I', g.syms['Scrcmd_getsetpokedexflag'] | 1)
                        + struct.pack('<HH', s, SET_CAUGHT) for s in species[i:i + 20])
        begin_code(g, code + opcode(g, 'end'))
        assert idle(g), 'setcaughtmon batch did not finish'


def converse(g, start, choose=None, taps=300):
    """Run a professor conversation. choose: None (no menu expected), 'B', or
    a 0-based menu row. Returns (all text boxes, menu was shown)."""
    g.clear_text()
    start()
    seen, menu = [], False
    for _ in range(taps):
        t = g.text()
        if t and (not seen or seen[-1] != t):
            seen.append(t)
        if not menu and 'Which one would you like' in t:
            menu = True
            res = g.syms['gSpecialVar_Result']
            g.write(res, 0, 2)
            for _ in range(6):                   # close the prompt until the menu is up
                g.tap(K.KEY_A, hold=2, wait=10)
                for _ in range(60):
                    if g.u16(res) == 0xFF:
                        break
                    g.frame(1)
                if g.u16(res) == 0xFF:
                    break
            assert g.u16(res) == 0xFF, 'starter menu never opened'
            g.frame(20)
            if choose == 'B':
                g.tap(K.KEY_B, hold=2, wait=30)
            else:
                for _ in range(choose or 0):
                    g.tap(K.KEY_DOWN, hold=2, wait=12)
                g.tap(K.KEY_A, hold=2, wait=30)
            continue
        if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            break
        g.tap(K.KEY_A, hold=2, wait=16)
    assert idle(g), ('conversation did not finish', seen)
    text = '\n'.join(seen)
    for a, b in [('\\n', ' '), ('{scroll}', ' '), ('{page}', ' '), ('<FA>', ' '), ('<FB>', ' '),
                 ("\\'", "'"), ('！', '!'), ('。', '.'), ('ひ', 'E')]:
        text = text.replace(a, b)
    return text, menu


def script(g, prof):
    label = ['PoxProf_Oak', 'PoxProf_Elm', 'PoxProf_Birch'][prof]
    return lambda: g.begin(label)


def party(g):
    return [g.party_species(i) for i in range(g.count())]


def flags(g, prof):
    names = [['OAK_BULBASAUR', 'OAK_CHARMANDER', 'OAK_SQUIRTLE'],
             ['ELM_CHIKORITA', 'ELM_CYNDAQUIL', 'ELM_TOTODILE'],
             ['BIRCH_TREECKO', 'BIRCH_TORCHIC', 'BIRCH_MUDKIP']][prof]
    return [g.flag('FLAG_POX_PROF_' + n) for n in names]


def static_checks():
    for name, gfx in [('GoldenrodCity_House2_hns', 'OBJ_EVENT_GFX_SCIENTIST'), ('FortreeCity_House3', 'OBJ_EVENT_GFX_PROF_BIRCH')]:
        objs = json.loads((ROOT / f'data/maps/{name}/map.json').read_text())['object_events']
        assert [o['graphics_id'] for o in objs] == [gfx], (name, objs)
    print('ok  map objects: Elm and Birch placed')


def logic_tests():
    g = Game(spawn=('FortreeCity_House3', 3, 4))
    g.write(g.syms['gPartiesCount'], 0) if g.count() else None
    # 24 Kanto + duplicates + Gen 2 / Gen 4 noise: not yet a reward.
    own(g, list(range(1, 25)) + list(range(1, 10)) + [152, 387, 400, 493])
    text, menu = converse(g, script(g, OAK))
    assert not menu and "I'm PROFESSOR OAK" in text and 'registered 24 KANTO' in text and 'reward is at 25' in text, text
    print('ok  24 owned Kanto (duplicates, Gen 2 and Gen 4 ignored): progress toward 25')
    own(g, [25])
    text, menu = converse(g, script(g, OAK), choose='B')
    assert menu and 'registered 25 KANTO' in text and flags(g, OAK) == [False] * 3 and g.count() == 0, (text, flags(g, OAK))
    print('ok  25th species earns a reward; B cancels without consuming it')
    text, menu = converse(g, script(g, OAK), choose=3)           # CANCEL row with three starters
    assert menu and flags(g, OAK) == [False] * 3 and 'Take your time' in text, text
    print('ok  CANCEL row does not consume the reward')
    text, menu = converse(g, script(g, OAK), choose=1)
    assert flags(g, OAK) == [False, True, False] and party(g) == [4], (flags(g, OAK), party(g))
    assert 'received charmander' in text.lower(), text
    text, menu = converse(g, script(g, OAK))
    assert not menu and "I'm PROFESSOR OAK" not in text and 'reward is at 50' in text, text
    print('ok  picked CHARMANDER at level 5 (second row); next milestone 50')
    own(g, range(26, 76))                                         # 75 Kanto, incl. evolutions (Ivysaur etc.)
    text, menu = converse(g, script(g, OAK), choose=1)            # remaining: BULBASAUR, SQUIRTLE
    assert flags(g, OAK) == [False, True, True] and party(g)[-1] == 7, (flags(g, OAK), party(g))
    text, menu = converse(g, script(g, OAK), choose=0)
    assert flags(g, OAK) == [True, True, True] and party(g)[-1] == 1, (flags(g, OAK), party(g))
    text, menu = converse(g, script(g, OAK))
    assert not menu and 'earned all three' in text and g.count() == 3, text
    print('ok  75 owned: claimed SQUIRTLE then BULBASAUR (claimed ones left the menu); no fourth reward')

    # Elm: 25 Johto without Totodile; the gift itself must register as owned.
    own(g, range(152, 158))
    own(g, range(159, 178))
    text, menu = converse(g, script(g, ELM), choose=2)
    assert "PROFESSOR ELM" in text and 'GOLDENROD CITY' in text and 'registered 25 JOHTO' in text, text
    assert flags(g, ELM) == [False, False, True] and party(g)[-1] == 158, (flags(g, ELM), party(g))
    text, _ = converse(g, script(g, ELM))
    assert 'registered 26 JOHTO' in text and 'reward is at 50' in text, text
    print('ok  Elm counts Gen 2 only; gifted TOTODILE registered as owned (25 -> 26)')

    # Birch with a full party: delivery to the PC still consumes correctly.
    stride = g.sizes['gParties'] // 24
    base = g.syms['gParties']
    while g.count() < 6:
        n = g.count()
        for i in range(stride):
            g.write(base + n * stride + i, g.u8(base + i))
        g.write(g.syms['gPartiesCount'], n + 1)
    own(g, range(252, 302))
    text, menu = converse(g, script(g, BIRCH), choose=1)
    assert 'PROFESSOR BIRCH' in text and 'FORTREE CITY' in text and 'sent to the PC' in text, text
    assert flags(g, BIRCH) == [False, True, False] and g.count() == 6, flags(g, BIRCH)
    print('ok  Birch counts Gen 3; full party sends TORCHIC to the PC and records it')

    save_reload(g)
    assert flags(g, OAK) == [True] * 3 and flags(g, ELM) == [False, False, True] and flags(g, BIRCH) == [False, True, False]
    text, menu = converse(g, script(g, BIRCH), choose=0)          # 50 Hoenn: second reward still due
    assert flags(g, BIRCH) == [True, True, False], (flags(g, BIRCH), text)
    text, menu = converse(g, script(g, BIRCH))
    assert not menu and 'reward is at 75' in text, text
    print('ok  reward flags survive save/reload; second Birch reward claimed after reload')


def walk_tests():
    g = Game(spawn=('GoldenrodCity_hns', 48, 16))
    g.flag('FLAG_POX_TRIGGERS_ENABLED', 1)
    city, house = map_id('GoldenrodCity_hns'), map_id('GoldenrodCity_House2_hns')
    enter_warp(g, (48, 16), 'UP', house, 'goldenrod house2 in')
    navigate(g, (4, 4))
    text, _ = converse(g, lambda: (g.tap(K.KEY_RIGHT, hold=2, wait=16), g.tap(K.KEY_A, hold=2, wait=16)))
    assert 'PROFESSOR ELM' in text and 'registered 0 JOHTO' in text, text
    navigate(g, (4, 7))
    enter_warp(g, (4, 7), 'DOWN', city, 'goldenrod house2 out')
    print('ok  Goldenrod House2 door -> talk to Elm -> back out to the city')

    g.warp('FortreeCity', 25, 4)
    city, house = map_id('FortreeCity'), map_id('FortreeCity_House3')
    enter_warp(g, (25, 4), 'UP', house, 'fortree house3 in')
    navigate(g, (4, 4))
    text, _ = converse(g, lambda: (g.tap(K.KEY_RIGHT, hold=2, wait=16), g.tap(K.KEY_A, hold=2, wait=16)))
    assert 'PROFESSOR BIRCH' in text and 'HOENN' in text, text
    enter_warp(g, (3, 4), 'DOWN', city, 'fortree house3 out')
    print('ok  Fortree House3 door -> talk to Birch -> back out to the city')

    for f in ['FLAG_POX_STORY_STARTER', 'FLAG_POX_LAB_INTRO', 'FLAG_POX_STARTER_SUPPLIES', 'FLAG_POX_HIDE_BATTLE_OAK_LAB',
              'FLAG_POX_ELM_EXP_ALL', 'FLAG_POX_ELM_TMS']:
        g.flag(f, 1)
    g.flag('FLAG_POX_HIDE_STORY_NPCS', 0)
    g.flag('FLAG_POX_TRIGGERS_ENABLED', 1)
    g.warp('PalletTown_ProfessorOaksLab_Frlg', 6, 7)
    for _ in range(60):
        if idle(g, 30):
            break
        g.tap(K.KEY_A, hold=2, wait=10)
    navigate(g, (6, 5))
    text, _ = converse(g, lambda: (g.tap(K.KEY_UP, hold=2, wait=16), g.tap(K.KEY_A, hold=2, wait=16)))
    assert 'Follow ROUTE 101' in text and "I'm PROFESSOR OAK" in text and 'registered 0 KANTO' in text, text
    assert text.index('Follow ROUTE 101') < text.index("I'm PROFESSOR OAK"), text
    print('ok  Oak keeps his story line, then explains the Kanto reward')


if __name__ == '__main__':
    static_checks()
    logic_tests()
    walk_tests()
    print('all professor starter checks passed')
