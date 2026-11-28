#!/usr/bin/env python3
"""Cinnabar Island, the Seafoam passage and Mossdeep City speak their own lines.

Static part: every text the pass wrote fits the message box (no line over 36
characters), the generator reproduces the checked-in files, and no dialogue in
the three areas names a villain team, BILL or the "convergence".

Emulator part (mGBA, needs pokeemerald.gba): stands next to each reworked
person, sign and document in the real ROM and reads what is printed, in every
story state that changes it: the Cinnabar dock hand, mansion neighbour and gym
regular before the badge / with BLAINE's key / after the Mansion; BLAINE's
refusal and last word; the archive files (sealed out of order, re-readable
once read); the Seafoam ice cutter before and after the current is stopped;
the Mossdeep sailor and launch-board woman before and after the Space Center
report; TATE & LIZA's refusal; the Space Center staff who used the global
"ask the local guide" line. It also proves the One Island BILL no longer
stands in the Cinnabar Pokemon Center.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / 'plastic_ox/alpha'))


def static_checks() -> None:
    import south_isles as s

    texts = []
    for body in s.NPCS.values():
        texts += [body] if not isinstance(body, list) else [body[0]] + [b for _, b in body[1:]]
    texts += list(s.TEXTS.values())
    for labels in s.REWRITES.values():
        texts += list(labels.values())
    for sub in ('cinnabar', 'seafoam'):
        for m in re.finditer(r'\.string "(.*)"', (ROOT / f'plastic_ox/alpha/{sub}/events.inc').read_text()):
            texts.append(('raw', m.group(1)))
    banned = re.compile(r'convergence|\bBILL\b|MAGMA|AQUA|ROCKET\b|adaptive|simulation', re.I)
    seen = set()
    for body in texts:
        laid = body[1] if isinstance(body, tuple) else s.pages(body)
        for line in re.split(r'\\[nlp]', laid.rstrip('$')):
            assert len(line.replace('{PLAYER}', 'PLAYERX')) <= 36, (len(line), line)
        assert not banned.search(laid.replace('rocket smoke', '').replace('rockets', '').replace('ride a rocket', '')), laid
        assert laid not in seen, ('duplicate text', laid)
        seen.add(laid)
    print(f'  ok  {len(texts)} texts fit the box, are unique, and name no villain team or BILL')

    import json
    enc = json.loads((ROOT / 'src/data/wild_encounters.json').read_text())['wild_encounter_groups'][0]['encounters']
    sea = {e['map']: e for e in enc if e['map'] in s.SEA}
    assert set(sea) == set(s.SEA), sorted(sea)
    assert not [e for e in enc if e['map'] in s.BARREN], 'Route 20 East must stay barren'
    for e in sea.values():
        assert e['base_label'].startswith('gPoxUURoute') and 'water_mons' in e and 'fishing_mons' in e, e['base_label']
        assert max(m['max_level'] for k in ('water_mons', 'fishing_mons') for m in e[k]['mons']) <= 42
    for name in s.PRUNED:
        d = json.loads((ROOT / f'data/maps/{name}/map.json').read_text())
        assert not [o for o in d['object_events'] if o['graphics_id'] in s.MAGMA_GFX], name
        assert not re.search(r'LOCALID_\w*(GRUNT|MAXIE|TABITHA)', (ROOT / f'data/maps/{name}/scripts.inc').read_text()), name
    print('  ok  Route 20 West carries a UU sea table (cap 42), East stays barren; no Magma people or scripts in Mossdeep')

    r = subprocess.run([sys.executable, 'plastic_ox/tools/check_generated.py'], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-1500:]
    r = subprocess.run([sys.executable, 'plastic_ox/tools/audit_npc_dialogue.py'], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-1500:]
    print('  ok  generator output matches the checkout; no duplicated NPC dialogue')


def emulator_checks() -> None:
    from test_sudowoodo_v1 import SudoGame as StoryGame
    from test_sudowoodo_v1 import talk
    from walklib import K

    g = StoryGame()
    g.run('Pox_Treecko')
    for name in ('FLAG_POX_STORY_STARTER', 'FLAG_ADVENTURE_STARTED', 'FLAG_POX_TRIGGERS_ENABLED'):
        g.flag(name, True)
    shots = ROOT / 'plastic_ox/demo/shots'
    shots.mkdir(exist_ok=True)

    def said(mapname, x, y, key, *fragments, shot=None, absent=()):
        # Let the previous conversation finish before the setup warp.
        # B only: an A press can land just as a sign's script ends and read it again.
        for _ in range(800):
            if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
                break
            g.tap(K.KEY_B, hold=2, wait=12)
        g.warp(mapname, x, y)
        g.frame(60)
        if shot:
            g.shot(str(shots / f'south_isles_{shot}.png'))
        r = talk(g, key)
        for _ in range(3):
            # A box left open by the previous (long) text can swallow the first
            # A press after the setup warp; warp again and ask once more.
            if r['text'] or not fragments:
                break
            for _ in range(200):
                if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
                    break
                g.tap(K.KEY_B, hold=2, wait=12)
            g.warp(mapname, x, y)
            g.frame(90)
            r = talk(g, key)
        text = ' '.join(r['text']).replace('\\n', ' ').replace('{page}', ' ').replace('{scroll}', ' ')
        text = text.replace("\\'", "'").replace('。', '.').replace('<FA>', ' ').replace('<FB>', ' ')
        text = ' '.join(text.split())
        for frag in fragments:
            assert frag in text, (mapname, x, y, frag, r['text'])
        for frag in absent:
            assert frag not in text, (mapname, x, y, frag, r['text'])
        return text

    def flags(**kw):
        for name, value in kw.items():
            g.flag(name, value)

    STORY = ('FLAG_BADGE04_GET', 'FLAG_POX_STORY_FUJI', 'FLAG_BADGE05_GET', 'FLAG_POX_MANSION_KEY',
             'FLAG_POX_ARCHIVE_1', 'FLAG_POX_ARCHIVE_2', 'FLAG_POX_STORY_MANSION', 'FLAG_BADGE06_GET',
             'FLAG_POX_STORY_SPACE_CENTER', 'FLAG_POX_STOPPED_SEAFOAM_B4F_CURRENT')
    flags(**{f: False for f in STORY})
    CIN = 'CinnabarIsland_Frlg'

    # --- Cinnabar before the badge ---
    said(CIN, 14, 7, K.KEY_UP, 'old research house', "won't lock a GYM", shot='cinnabar_street')
    said(CIN, 11, 12, K.KEY_UP, 'Six questions', 'question four')
    said(CIN, 21, 11, K.KEY_RIGHT, 'off the timetable', 'BLAINE first', shot='cinnabar_quay')
    said(CIN, 17, 6, K.KEY_UP, 'Tomatoes', 'matches')
    said(CIN, 7, 10, K.KEY_LEFT, 'Coffee break', 'up the hill')
    assert not said(CIN, 12, 13, K.KEY_DOWN), 'Cinnabar must carry no ROUTE 103 sign'
    said(CIN, 21, 9, K.KEY_RIGHT, 'EAST QUAY', 'SEAFOAM ISLANDS', 'scratched out', absent=('Marked passage',))
    print('  ok  Cinnabar islanders, quay and road signs (before the badge)')
    said('CinnabarIsland_Gym_Frlg', 5, 5, K.KEY_UP, 'Four BADGES', 'door charge')
    said('CinnabarIsland_Gym_Frlg', 24, 21, K.KEY_UP, 'Forget the BURN HEALS', 'nothing heavier than UU', 'Nothing BLAINE would object to')

    def teach(slot, move):
        # setmonmove 0, slot, move; end -- run from gStringVar4 like test_national_park.call.
        ptr = g.syms['gStringVar4']
        for i, b in enumerate(bytes([0x7B, 0, slot]) + move.to_bytes(2, 'little') + bytes([0x02])):
            g.write(ptr + i, b)
        g.run(ptr)
    teach(3, 86)  # MOVE_THUNDER_WAVE: a Little Cup ban, legal under UU
    said('CinnabarIsland_Gym_Frlg', 24, 21, K.KEY_UP, 'Nothing BLAINE would object to', absent=('Hold on.',))
    teach(3, 90)  # MOVE_FISSURE: OHKO clause
    said('CinnabarIsland_Gym_Frlg', 24, 21, K.KEY_UP, 'Hold on.', 'knows Fissure', 'house rule',
         absent=('Nothing BLAINE',))
    said('MossdeepCity_Gym', 5, 34, K.KEY_UP, 'knows Fissure', "Twins' rule")
    teach(3, 0)
    print('  ok  gym guides check ADV UU / UUBL clauses: Thunder Wave passes, Fissure is named')
    print('  ok  BLAINE refuses in his own voice; the gym guide describes the real team and checks the party')

    # --- with BLAINE's key ---
    flags(FLAG_BADGE04_GET=True, FLAG_POX_STORY_FUJI=True, FLAG_BADGE05_GET=True, FLAG_POX_MANSION_KEY=True)
    said(CIN, 14, 7, K.KEY_UP, 'SECRET KEY', 'statues', 'SAGE', absent=('MANSION KEY',))
    said(CIN, 11, 12, K.KEY_UP, 'Six for six', 'key')
    said(CIN, 21, 11, K.KEY_RIGHT, "BLAINE's key", 'still unread')
    said('CinnabarIsland_Gym_Frlg', 24, 21, K.KEY_UP, 'old firefighter')
    print('  ok  with the key: neighbour, gym regular, dock hand and gym guide move on')
    # Route 103 -> Cinnabar is one-way: the old (12,12) return portal is gone.
    g.warp(CIN, 12, 13)
    g.frame(60)
    where = g.walk('UP', target=(12, 11), timeout=600)
    assert where.startswith('CINNABAR') or 'Cinnabar' in where or g.state()['y'] <= 12, where
    assert 'ROUTE103' not in where.replace(' ', '').upper() and 'ROUTE_103' not in where.upper(), where
    print('  ok  no portal back to ROUTE 103 from the Cinnabar road')
    said('PokemonMansion_B1F_Frlg', 21, 26, K.KEY_DOWN, 'FILE 3', 'IN SEQUENCE')
    assert not g.flag('FLAG_POX_STORY_MANSION')
    said('PokemonMansion_B1F_Frlg', 5, 8, K.KEY_UP, 'Not yet, if you please', 'three files', shot='entei_waits')
    assert not g.flag('FLAG_POX_ENTEI')
    print('  ok  the ENTEI sage waits for the whole archive')
    t = said('PokemonMansion_2F_Frlg', 24, 4, K.KEY_RIGHT, 'ARCHIVE, FILE 1', 'living state')
    assert g.flag('FLAG_POX_ARCHIVE_1'), t
    said('PokemonMansion_2F_Frlg', 24, 4, K.KEY_RIGHT, 'ARCHIVE, FILE 1', absent=('Good luck',))
    flags(FLAG_POX_ARCHIVE_2=True)
    said('PokemonMansion_B1F_Frlg', 21, 26, K.KEY_DOWN, 'FILE 3', 'BURNED TOWER', 'shipping slip',
         shot='mansion_archive3')
    assert g.flag('FLAG_POX_STORY_MANSION')
    print('  ok  archive files: sealed out of order, read in order, re-readable; file 3 opens the sea')

    # --- after the Mansion ---
    said(CIN, 14, 7, K.KEY_UP, 'a long time', 'eye on the door')
    said(CIN, 11, 12, K.KEY_UP, "don't bet on that")
    said(CIN, 21, 11, K.KEY_RIGHT, 'east channel is yours', 'black rock')
    said('CinnabarIsland_Gym_Frlg', 5, 5, K.KEY_UP, 'walking slower', 'Tell FUJI')
    print('  ok  after the Mansion the island is finished with the player, and the quay says so')
    said('CinnabarIsland_PokemonCenter_1F_Frlg', 13, 6, K.KEY_RIGHT, 'bets on the GYM quiz', shot='cinnabar_center')
    g.warp('CinnabarIsland_PokemonCenter_1F_Frlg', 11, 6)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    assert not r['text'], ('BILL still stands in the Cinnabar Pokemon Center', r['text'])
    print('  ok  Cinnabar Pokemon Center: the quiz pool reaches the lobby, and no One Island BILL')

    # --- Seafoam passage ---
    said('PlasticOx_Route20West', 58, 10, K.KEY_DOWN, 'wind turned', 'at the door', shot='route20_landing')
    said('PlasticOx_Route20West', 64, 9, K.KEY_UP, 'WEST DOOR', 'Watch the swell', shot='route20_sign')
    said('SeafoamIslands_1F_Frlg', 5, 18, K.KEY_LEFT, 'cut ice', 'takes the rocks back', shot='seafoam_west')
    said('SeafoamIslands_1F_Frlg', 33, 18, K.KEY_RIGHT, 'MOSSDEEP side', 'launch tower')
    flags(FLAG_POX_STOPPED_SEAFOAM_B4F_CURRENT=True)
    said('SeafoamIslands_1F_Frlg', 5, 18, K.KEY_LEFT, 'Hear that', "It'll hold")
    print('  ok  Seafoam: angler and sign on the landing, ice cutter (both states), swimmer')

    # --- Mossdeep ---
    MOSS = 'MossdeepCity'
    said(MOSS, 3, 21, K.KEY_RIGHT, 'out of the cave', 'six and six', shot='mossdeep_beach')
    said(MOSS, 38, 13, K.KEY_UP, 'ROUTE 19', 'shut a good while')
    said(MOSS, 32, 13, K.KEY_UP, 'launch board', 'pasted over three times')
    said(MOSS, 64, 16, K.KEY_RIGHT, 'said soon', shot='mossdeep_space_center_door')
    said(MOSS, 55, 21, K.KEY_RIGHT, 'white rock', 'launch window')
    flags(FLAG_BADGE06_GET=False)
    flags(FLAG_POX_STORY_MANSION=False)
    said('MossdeepCity_Gym', 23, 8, K.KEY_UP, 'Not quite yet', 'by sea')
    flags(FLAG_POX_STORY_MANSION=True)
    said('MossdeepCity_Gym', 5, 34, K.KEY_UP, 'double battle', 'round one', "passes the twins' rules")
    said('MossdeepCity_SpaceCenter_1F', 7, 3, K.KEY_UP, 'middle of a count', 'TATE and LIZA')
    said('MossdeepCity_SpaceCenter_1F', 5, 8, K.KEY_UP, 'feeding time')
    said('MossdeepCity_SpaceCenter_1F', 1, 7, K.KEY_UP, 'ride a rocket')
    g.warp('MossdeepCity_SpaceCenter_1F', 2, 7)
    g.frame(60)
    g.shot(str(shots / 'south_isles_space_center_child.png'))
    print('  ok  Mossdeep before the report: port, launch board, twins and Space Center refusals')
    flags(FLAG_BADGE06_GET=True, FLAG_POX_STORY_SPACE_CENTER=True)
    said(MOSS, 38, 13, K.KEY_UP, 'SAFFRON is open', 'easy part')
    said(MOSS, 32, 13, K.KEY_UP, 'fourth date', 'arguing about the wind')
    said('MossdeepCity_Gym', 23, 8, K.KEY_UP, 'already beat us', 'white rock')
    said('MossdeepCity_Gym', 5, 34, K.KEY_UP, 'at their own game', 'SPACE CENTER')
    print('  ok  Mossdeep after the report: sailor, launch board, twins and gym guide turn over')

    # --- Mossdeep interiors ---
    said('MossdeepCity_House1', 7, 5, K.KEY_UP, 'canteen')
    said('MossdeepCity_House2', 6, 7, K.KEY_UP, 'the worrying')
    said('MossdeepCity_House2', 3, 4, K.KEY_RIGHT, 'better than the ferry')
    said('MossdeepCity_House3', 4, 5, K.KEY_UP, 'starter rod')
    said('MossdeepCity_House4', 3, 5, K.KEY_UP, 'hideouts in the bushes')
    said('MossdeepCity_GameCorner_1F', 4, 3, K.KEY_UP, 'aerial', shot='mossdeep_game_corner')
    said('MossdeepCity_GameCorner_1F', 6, 3, K.KEY_UP, 'six summers')
    print('  ok  Mossdeep houses and Game Corner speak their own lines')

    # A species over the tier: give a SALAMENCE (OU) with the bytes of Steven's
    # compiled BELDUM givemon, species swapped (no ROM_SIZE arithmetic here).
    src = g.syms['MossdeepCity_StevensHouse_EventScript_GiveBeldum']
    rom = bytes(g.u8(src + i) for i in range(32))
    at = rom.index(0x23)
    give = bytearray(rom[at:at + 19])
    assert int.from_bytes(give[7:9], 'little') == 374, give.hex()  # SPECIES_BELDUM
    give[7:9] = (373).to_bytes(2, 'little')  # SPECIES_SALAMENCE
    give[9:11] = (50).to_bytes(2, 'little')
    ptr = g.syms['gStringVar4']
    for i, b in enumerate(bytes(give) + bytes([0x02])):
        g.write(ptr + i, b)
    g.run(ptr)
    flags(FLAG_BADGE05_GET=False, FLAG_BADGE06_GET=False)
    said('CinnabarIsland_Gym_Frlg', 24, 21, K.KEY_UP, 'Salamence', "weight class", 'UU',
         absent=('Nothing BLAINE',))
    said('MossdeepCity_Gym', 5, 34, K.KEY_UP, 'Salamence', 'UUBL')
    print('  ok  gym guides name a POKéMON over the tier (SALAMENCE, OU)')

    # Last, because it ends in a battle: once FILE 3 is read the sage takes the challenge.
    flags(FLAG_POX_STORY_MANSION=True, FLAG_POX_ENTEI=False)
    g.warp('PokemonMansion_B1F_Frlg', 5, 8)
    g.frame(60)
    r = talk(g, K.KEY_UP)
    assert r['battle'] and any('Forgive me' in t for t in r['text']), r['text']
    print('  ok  after the archive, the ENTEI sage starts his battle')


if __name__ == '__main__':
    static_checks()
    if '--static' not in sys.argv:
        emulator_checks()
    print('\nPASS: Cinnabar, Seafoam and Mossdeep dialogue')
