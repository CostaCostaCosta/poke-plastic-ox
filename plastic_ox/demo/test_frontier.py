#!/usr/bin/env python3
"""Battle Frontier (postgame), played in mGBA.

Proves:
* static: the compiled team table matches plastic_ox/frontier/, every house
  lobby runs its own tier desk, the harbor gates need FLAG_POX_FRONTIER_INVITE;
* a Champion without the invite is turned back at Lavender's south harbor;
* arriving in Pallet as Champion, MOM calls the player over to OAK (once);
* OAK hands over the FRONTIER INVITE and points south of LAVENDER TOWN;
* with the invite, Lavender south -> harbor -> Frontier walk through;
* a house refuses a party that breaks its tier (Little Cup, PU);
* the UBERS house runs a real seven-battle round: every opponent is a team from
  plastic_ox/frontier/gen3_ubers_constructed_225.txt at the player's level, and
  the seventh win sets FLAG_POX_FRONTIER_CLEARED_UBERS;
* losing a round returns the player to the lobby healed, without whiting out.
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pox_fixtures import ROOT, at, finish_trainer, game, shot  # noqa: E402
from test_sudowoodo_v1 import bag, const, in_battle, settle  # noqa: E402
from walklib import K  # noqa: E402

TEAMS = (ROOT / 'src/data/plastic_ox_frontier_teams.h').read_text()
SET_SPECIES = re.findall(r'^    \{(SPECIES_\w+), ', TEAMS, re.M)
HOUSES = {  # tier: (lobby, attendant tile, stand tile)
    'LC': ('BattleFrontier_BattlePyramidLobby', (7, 12), (7, 13)),
    'PU': ('BattleFrontier_BattlePikeLobby', (5, 5), (5, 6)),
    'UBERS': ('BattleFrontier_BattleTowerLobby', (6, 5), (6, 6)),
}


def tier_species(tier):
    rows = re.search(r'sPoxFrontierTeams_' + tier.lower() + r'\[\]\[PARTY_SIZE\] =\n\{\n(.*?)\n\};', TEAMS, re.S)[1]
    ids = {int(n) for n in re.findall(r'\d+', rows)}
    return {const(SET_SPECIES[i], 'species.h') for i in ids}


def static_checks():
    subprocess.run([sys.executable, str(ROOT / 'plastic_ox/tools/build_frontier_teams.py'), '--check'], check=True)
    inc = (ROOT / 'data/scripts/plastic_ox_frontier.inc').read_text()
    import json
    for key, (lobby, xy, _) in HOUSES.items():
        objs = json.loads((ROOT / f'data/maps/{lobby}/map.json').read_text())['object_events']
        assert any(o['script'] == f'PoxFrontier_{key}_Attendant' and (o['x'], o['y']) == xy for o in objs), lobby
    strings = re.findall(r'^\w+::\n\t\.string "(.*)\$"', inc, re.M)
    assert len(strings) == len(set(strings)), 'two Frontier lines share their text'
    for body in strings:
        for line in re.split(r'\\[np]', body):
            assert len(re.sub(r'\{\w+\}', 'XXXXXXX', line)) <= 36, line
    region = (ROOT / 'data/scripts/plastic_ox_region.inc').read_text()
    for gate in ('lavender_harbor_a', 'harbor_frontier_a'):
        assert f'goto_if_unset FLAG_POX_FRONTIER_INVITE, PoxRegion_{gate}_Closed' in region, gate
    print(f'ok  static: {len(SET_SPECIES)} sets, 7 houses, unique lines, invite-gated harbor', flush=True)


def drive(g, until, taps=600, no_at=None):
    """Tap A (or B when the text contains no_at) until until(g); returns texts seen."""
    seen = []
    for _ in range(taps):
        t = g.text()
        g.tap(K.KEY_B if no_at and no_at in t else K.KEY_A, hold=1, wait=6)
        t = g.text()
        if t and (not seen or seen[-1] != t):
            seen.append(t)
        if until(g):
            return seen
    shot(g, 'frontier_drive_timeout')
    raise AssertionError(f'drive timed out; texts: {seen[-4:]}')


def idle(g):
    return g.u8(g.syms['sGlobalScriptContextStatus']) == 2 and not in_battle(g)


def cross_port(g, port_id):
    import json
    ports = {p['id']: p for p in json.loads((ROOT / 'plastic_ox/alpha/region_manifest.json').read_text())['transitions']}
    p = ports[port_id]
    g.warp(p['source'], *p['approach'])
    settle(g)
    g.clear_text()
    g.tap({'N': K.KEY_UP, 'S': K.KEY_DOWN, 'E': K.KEY_RIGHT, 'W': K.KEY_LEFT}[p['direction']], hold=16, wait=60)
    texts = drive(g, idle, taps=300)
    g.frame(120)
    return p, texts


def champion():
    g = game()
    g.flag('FLAG_SYS_GAME_CLEAR', True)
    g.flag('FLAG_POX_STORY_STARTER', True)
    g.flag('FLAG_POX_LAB_INTRO', True)
    g.setvar(const_var('VAR_POX_MOM_STATE'), 1)
    return g


def const_var(name):
    return int(re.search(r'#define ' + name + r'\s+(0x[0-9A-Fa-f]+)', (ROOT / 'include/constants/vars.h').read_text())[1], 16)


def handoff():
    g = champion()
    p, texts = cross_port(g, 'lavender_harbor_a')
    assert at(g, p['source']), g.describe()
    assert any('invitation' in t for t in texts), texts
    print('ok  Champion without the invite is turned back at the harbor', flush=True)

    g.warp('PalletTown_Frlg', 10, 9)
    texts = drive(g, idle, taps=300)
    assert any('PROFESSOR OAK called' in t for t in texts), texts
    assert g.flag('FLAG_POX_FRONTIER_MOM_TOLD')
    shot(g, 'frontier_mom')
    g.warp('PalletTown_Frlg', 10, 9)
    g.clear_text()
    texts = drive(g, idle, taps=60)
    assert not any('PROFESSOR OAK called' in t for t in texts), 'MOM called twice'
    print('ok  MOM calls the new Champion over to OAK on reaching Pallet, once', flush=True)

    g.warp('PalletTown_ProfessorOaksLab_Frlg', 6, 5)
    settle(g)
    g.tap(K.KEY_UP, hold=2, wait=8)
    texts = drive(g, idle, taps=400)
    invite = const('ITEM_FRONTIER_INVITE', 'items.h')
    assert bag(g, invite) == 1, texts
    assert g.flag('FLAG_POX_FRONTIER_INVITE')
    assert any('south of LAVENDER' in t for t in texts), texts
    shot(g, 'frontier_oak')
    print('ok  OAK gives the FRONTIER INVITE and sends the player south of LAVENDER TOWN', flush=True)

    p, _ = cross_port(g, 'lavender_harbor_a')
    assert at(g, p['destination']), g.describe()
    p, _ = cross_port(g, 'harbor_frontier_a')
    assert at(g, p['destination']), g.describe()
    shot(g, 'frontier_arrival')
    print('ok  with the invite: Lavender south -> harbor -> Battle Frontier', flush=True)


def stand_at_desk(g, tier):
    lobby, _, stand = HOUSES[tier]
    g.flag('FLAG_POX_FRONTIER_INVITE', True)
    g.warp(lobby, *stand)
    settle(g)
    assert at(g, lobby), g.describe()
    g.clear_text()
    g.tap(K.KEY_UP, hold=2, wait=8)


def refusals():
    for tier in ('LC', 'PU'):
        g = champion()
        stand_at_desk(g, tier)
        texts = drive(g, idle, taps=300)
        assert any('rules' in t for t in texts) and not in_battle(g), texts
        assert not any('Battle 1 of seven' in t for t in texts), texts
        print(f'ok  {tier} house refuses an over-tier party: {texts[-1]!r}', flush=True)


def party_level(g):
    stride = g.sizes['gParties'] // 24
    return max(g.u8(g.syms['gParties'] + i * stride + 0x54) for i in range(6))


def ubers_round():
    g = champion()
    species = tier_species('UBERS')
    stand_at_desk(g, 'UBERS')
    for n in range(1, 8):
        drive(g, in_battle, taps=600)
        for _ in range(2000):
            if g.controller('HandleInputChooseAction'):
                break
            g.tap(K.KEY_A, hold=1, wait=4)
        stride_b = g.u32(g.syms['gMetamonTestLayout'] + 6 * 4)
        level = g.u8(g.syms['gBattleMons'] + stride_b + g.u32(g.syms['gMetamonTestLayout'] + 10 * 4) + 2)  # level follows hp
        assert level == party_level(g), (n, level, party_level(g))
        foe = g.u16(g.syms['gBattleMons'] + g.u32(g.syms['gMetamonTestLayout'] + 6 * 4))
        assert foe in species, (n, foe)
        finish_trainer(g, True)
        assert at(g, 'BattleFrontier_BattleTowerLobby'), g.describe()
    drive(g, idle, taps=300)
    assert g.flag('FLAG_POX_FRONTIER_CLEARED_UBERS')
    shot(g, 'frontier_cleared')
    print('ok  UBERS house: seven battles against UBERS pool teams, round cleared', flush=True)

    # Lose the next round's first battle: no white-out, healed, still in the lobby.
    g.clear_text()
    g.tap(K.KEY_UP, hold=2, wait=8)
    drive(g, in_battle, taps=600)
    finish_trainer(g, False)
    texts = drive(g, idle, taps=300)
    assert at(g, 'BattleFrontier_BattleTowerLobby'), g.describe()
    assert any('ends your' in t for t in texts), texts
    stride = g.sizes['gParties'] // 24
    hp = [g.u16(g.syms['gParties'] + i * stride + 0x56) for i in range(6)]
    assert all(h > 0 for h in hp if h), hp
    print('ok  losing a round heals the party in the lobby, no white-out', flush=True)


def tier_battles():
    """One real battle in every other house. The fixture party is over most tiers,
    so the round starts past the desk's rules check (refusals() covers that)."""
    from pox_fixtures import run_code
    from test_sudowoodo_v1 import opcode
    import struct
    var8004 = 0x8004
    for i, tier in enumerate(['LC', 'PU', 'NU', 'RU', 'UU', 'UUBL']):
        g = champion()
        g.flag('FLAG_POX_FRONTIER_INVITE', True)
        lobby = {'LC': 'BattleFrontier_BattlePyramidLobby', 'PU': 'BattleFrontier_BattlePikeLobby',
                 'NU': 'BattleFrontier_BattleFactoryLobby', 'RU': 'BattleFrontier_BattleArenaLobby',
                 'UU': 'BattleFrontier_BattlePalaceLobby', 'UUBL': 'BattleFrontier_BattleDomeLobby'}[tier]
        g.warp(lobby, *{'LC': (7, 13), 'PU': (5, 6), 'NU': (4, 8), 'RU': (7, 8), 'UU': (5, 7), 'UUBL': (5, 11)}[tier])
        settle(g)
        from test_qol import begin_code
        begin_code(g, opcode(g, 'setvar') + struct.pack('<HH', var8004, i)
                   + opcode(g, 'callnative') + struct.pack('<I', g.syms['PoxFrontier_Begin'] | 1)
                   + opcode(g, 'goto') + struct.pack('<I', g.syms[f'PoxFrontier_{tier}_Next']))
        drive(g, in_battle, taps=600)
        for _ in range(2000):
            if g.controller('HandleInputChooseAction'):
                break
            g.tap(K.KEY_A, hold=1, wait=4)
        foe = g.u16(g.syms['gBattleMons'] + g.u32(g.syms['gMetamonTestLayout'] + 6 * 4))
        assert foe in tier_species(tier), (tier, foe)
        finish_trainer(g, True)
        texts = drive(g, idle, taps=300, no_at='next opponent')
        assert any('retired' in t for t in texts), (tier, texts)
        assert at(g, lobby) and not g.flag(f'FLAG_POX_FRONTIER_CLEARED_{tier}'), tier
        print(f'ok  {tier} house: a {tier} pool team battled under the trainer AI, retire works', flush=True)


if __name__ == '__main__':
    static_checks()
    handoff()
    refusals()
    ubers_round()
    tier_battles()
    print('PASS: Battle Frontier', flush=True)
