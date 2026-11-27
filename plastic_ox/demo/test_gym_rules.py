#!/usr/bin/env python3
"""Every gym's party-rules special, run in the real ROM (mGBA).

src/field_specials.c gives each gym one check: Rustboro is Little Cup (LC species
only, plus the Little Cup move/item bans); Goldenrod PU through Blackthorn OU use
CheckADVTierGymRules(tier): species at or below the tier in
src/data/pokemon/evolution_tier_gates.h, no Ubers, and the ADV clauses (OHKO,
evasion moves and items, Assist, Swagger). Each returns 1 for a move, 2 for an
item, 3 for a species, 0 for a legal party.

The specials are called with real script bytes (specialvar VAR_RESULT, ...) for
each party below; then every greeter (Rustboro's guide and door, the Goldenrod,
Ecruteak, Saffron and Blackthorn hall greeters, Fortree's guide) is talked to.
4 is the Species Clause (two of one species), 5 a banned ability (Sand Veil,
Soundproof).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

GYMS = ['CheckRustboroGymLittleCupRules', 'CheckGoldenrodGymPURules', 'CheckEcruteakGymNURules',
        'CheckFortreeGymRURules', 'CheckCinnabarGymUURules', 'CheckMossdeepGymUUBLRules',
        'CheckSaffronGymOURules', 'CheckBlackthornGymOURules']
THUNDER_WAVE, FISSURE = 86, 90
BELDUM, SALAMENCE, MEWTWO, KANGASKHAN = 374, 373, 150, 115
TREECKO, SANDSHREW = 252, 27


def main() -> None:
    from test_sudowoodo_v1 import SudoGame as StoryGame
    from test_sudowoodo_v1 import talk
    from walklib import K

    g = StoryGame()
    g.run('Pox_Treecko')
    for name in ('FLAG_POX_STORY_STARTER', 'FLAG_ADVENTURE_STARTED', 'FLAG_POX_TRIGGERS_ENABLED'):
        g.flag(name, True)
    ptr = g.syms['gStringVar4']

    def script(code):
        for i, b in enumerate(bytes(code) + bytes([0x02])):  # ...; end
            g.write(ptr + i, b)
        g.run(ptr)

    def rules():
        out = []
        for name in GYMS:
            script(bytes([0x26]) + (0x800D).to_bytes(2, 'little') + g.syms['SPECIAL_' + name].to_bytes(2, 'little'))
            out.append(g.u16(g.syms['gSpecialVar_Result']))
        return out

    def teach(slot, move):
        script(bytes([0x7B, 0, slot]) + move.to_bytes(2, 'little'))

    # givemon: the bytes of Steven's compiled BELDUM gift, species swapped.
    src = g.syms['MossdeepCity_StevensHouse_EventScript_GiveBeldum']
    rom = bytes(g.u8(src + i) for i in range(32))
    give_bytes = bytearray(rom[rom.index(0x23):rom.index(0x23) + 19])
    assert int.from_bytes(give_bytes[7:9], 'little') == BELDUM, give_bytes.hex()

    stride = g.sizes['gParties'] // 24  # MAX_BATTLE_TRAINERS (4) x PARTY_SIZE

    def only_lead():
        base = g.syms['gParties']
        for i in range(stride, 6 * stride):
            g.write(base + i, 0)
        g.write(g.syms['gPartiesCount'], 1)

    def give(species, level=50):
        only_lead()
        code = bytearray(give_bytes)
        code[7:9] = species.to_bytes(2, 'little')
        code[9:11] = level.to_bytes(2, 'little')
        script(code)
        assert g.u8(g.syms['gPartiesCount']) == 2

    def expect(label, want):
        got = rules()
        assert got == want, (label, dict(zip(GYMS, got)), want)
        print(f'  ok  {label}: {got}')

    expect('TREECKO (LC) only, legal everywhere', [0] * 8)
    teach(3, THUNDER_WAVE)
    expect('Thunder Wave: Little Cup ban only', [1, 0, 0, 0, 0, 0, 0, 0])
    teach(3, FISSURE)
    expect('Fissure: OHKO clause in every tier', [1] * 8)
    teach(3, 0)
    give(SALAMENCE)
    expect('SALAMENCE (OU): over every tier below OU', [3, 3, 3, 3, 3, 3, 0, 0])
    give(KANGASKHAN)
    expect('KANGASKHAN (UU): legal from Cinnabar up', [3, 3, 3, 3, 0, 0, 0, 0])
    give(MEWTWO)
    expect('MEWTWO (Uber): over every tier', [3] * 8)
    give(BELDUM, 5)
    expect('BELDUM (LC): legal everywhere', [0] * 8)
    give(TREECKO, 5)
    expect('second TREECKO: Species Clause in every gym', [4] * 8)
    give(SANDSHREW, 5)
    expect('SANDSHREW (Sand Veil): ability ban in every gym', [5] * 8)

    def said(mapname, x, y, key, *fragments):
        g.warp(mapname, x, y)
        g.frame(60)
        r = talk(g, key)
        text = ' '.join(r['text']).replace('{page}', ' ').replace('\\n', ' ').replace('<FA>', ' ').replace('<FB>', ' ')
        text = ' '.join(text.split())
        for frag in fragments:
            assert frag in text, (mapname, frag, r['text'])

    give(SALAMENCE)
    g.flag('FLAG_BADGE01_GET', False)
    said('RustboroCity_Gym', 3, 19, K.KEY_UP, 'LITTLE CUP', 'is a Salamence', 'leave it in the PC')
    said('PlasticOx_WhitneyGym', 7, 18, K.KEY_UP, 'PU rules', 'is a Salamence', 'over the tier')
    for mapname, x, y, rule in (('PlasticOx_MortyGym', 7, 18, 'NU rules'),
                                ('PlasticOx_ClairGym', 7, 18, 'OU rules'),
                                ('FortreeCity_Gym', 15, 22, 'RU rules')):
        if rule == 'OU rules':
            give(MEWTWO)
            said(mapname, x, y, K.KEY_UP, rule, 'is a Mewtwo', 'over the tier')
        else:
            give(SALAMENCE)
            said(mapname, x, y, K.KEY_UP, rule, 'is a Salamence', 'over the tier')
    # BRUNO's Gym is the Fighting Dojo; its desk clerk (8,13) runs the same check
    # in her own words (plastic_ox/alpha/saffron.py).
    g.flag('FLAG_BADGE07_GET', False)
    give(MEWTWO)
    said('SaffronCity_Dojo_Frlg', 7, 13, K.KEY_RIGHT, 'OU rules', 'is a Mewtwo', 'above what this floor allows')
    give(TREECKO, 5)
    said('SaffronCity_Dojo_Frlg', 7, 13, K.KEY_RIGHT, 'is a second Treecko', 'One of each')
    give(SANDSHREW, 5)
    said('SaffronCity_Dojo_Frlg', 7, 13, K.KEY_RIGHT, 'has Sand Veil', 'allowed on this floor')
    give(TREECKO, 5)
    said('PlasticOx_ClairGym', 7, 18, K.KEY_UP, 'OU rules', 'is a second Treecko', 'one of each')
    give(SANDSHREW, 5)
    said('FortreeCity_Gym', 15, 22, K.KEY_UP, 'RU rules', 'has Sand Veil', 'ability is banned')
    print('  ok  Ecruteak, Saffron, Blackthorn and Fortree greeters run their tier checks')
    give(SALAMENCE)
    print('  ok  Rustboro guide and Goldenrod greeter name the over-tier SALAMENCE')
    # Rustboro's door turns an over-tier party away (warp back to the city).
    g.warp('RustboroCity_Gym', 5, 19)
    g.frame(60)
    gym = (g.state()['group'], g.state()['num'])
    g.tap(K.KEY_UP, hold=10, wait=60)
    for _ in range(60):
        g.tap(K.KEY_B, hold=2, wait=20)
        if g.u8(g.syms['sGlobalScriptContextStatus']) == 2 and (g.state()['group'], g.state()['num']) != gym:
            break
    state = g.state()
    assert (state['group'], state['num']) != gym and (state['x'], state['y']) == (27, 20), state
    print('  ok  Rustboro door turns the over-tier party back out to the city at (27,20)')
    only_lead()
    print('\nPASS: gym party rules')


if __name__ == '__main__':
    main()
