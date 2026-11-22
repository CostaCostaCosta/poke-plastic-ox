#!/usr/bin/env python3
"""Ecruteak City NPCs speak about what stands next to them, and follow story state.

Talks to the real field objects in mGBA and reads the expanded message buffer:

* the old man beside the BURNED TOWER door talks about the tower (before and
  after FLAG_POX_STORY_BURNED_TOWER), never the LEAGUE;
* the lamp-trimmer south of the tower stops pointing at MORTY once badge 3 is won;
* the bell-founder and the carpenter's boy do not mention the tower's bell or
  its momentary restoration before the tower beat has happened;
* the east door watch no longer says the door is open while still standing in it;
* the House 2 river dredger offers the engine in-game trade
  INGAME_TRADE_RELICANTH (CLAMPERL -> RELICANTH), accepts a decline, and has
  distinct post-trade text.

Run: plastic_ox/bin/pox-mgba-python plastic_ox/demo/test_ecruteak_npcs.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_story import StoryGame  # noqa: E402
from test_sudowoodo_v1 import CHARMAP  # noqa: E402
from walklib import K  # noqa: E402

CITY, HOUSE = 'EcruteakCity_hns', 'EcruteakCity_House2_hns'


def text(g):
    addr = g.syms['gStringVar4']
    out = []
    for i in range(600):
        b = g.u8(addr + i)
        if b == 0xFF:
            break
        out.append(CHARMAP.get(b, ' '))
    return ''.join(out).replace('\\n', ' ').replace('{page}', ' ').replace('{scroll}', ' ')


def idle(g):
    return g.u8(g.syms['sGlobalScriptContextStatus']) == 2


def talk(g, map_name, stand, face, key=K.KEY_A):
    """Warp next to an NPC, face it, talk, and return every message shown."""
    g.warp(map_name, *stand)
    g.frame(60)
    g.tap(face, hold=1, wait=12)   # turn in place toward the NPC
    g.write(g.syms['gStringVar4'], 0xFF)
    g.tap(K.KEY_A, hold=2, wait=20)
    seen = []
    for _ in range(120):
        t = text(g)
        if t and (not seen or seen[-1] != t):
            seen.append(t)
        if idle(g):
            break
        g.tap(key, hold=2, wait=14)
    assert idle(g), ('script did not finish', map_name, stand, seen)
    joined = ' | '.join(seen)
    assert joined, ('no dialogue', map_name, stand)
    return ' '.join(joined.split())


def main():
    g = StoryGame()
    g.flag('FLAG_POX_STORY_STARTER', True)
    g.flag('FLAG_ADVENTURE_STARTED', True)
    g.flag('FLAG_POX_TRIGGERS_ENABLED', True)
    g.flag('FLAG_BADGE01_GET', True)
    g.flag('FLAG_BADGE02_GET', True)

    def state(tower, badge):
        g.flag('FLAG_POX_STORY_BURNED_TOWER', tower)
        g.flag('FLAG_BADGE03_GET', badge)

    seen = {}
    # Before the Burned Tower beat.
    state(False, False)
    t = talk(g, CITY, (20, 15), K.KEY_LEFT)
    assert 'BURNED TOWER' in t and 'LEAGUE' not in t, t
    seen['tower_door_before'] = t
    t = talk(g, CITY, (19, 23), K.KEY_UP)
    assert 'MORTY went below' in t, t
    seen['lamps_before'] = t
    t = talk(g, CITY, (36, 42), K.KEY_UP)
    assert 'Nobody has found' in t and 'pulled' not in t, t
    seen['bell_before'] = t
    t = talk(g, CITY, (52, 50), K.KEY_UP)
    assert 'heartbeat' not in t and 'ledger' in t, t
    seen['carpenter_before'] = t
    t = talk(g, CITY, (53, 42), K.KEY_RIGHT)
    assert 'until MORTY' in t, t
    seen['east_door_before'] = t
    print('ok  pre-tower: tower door, lamps, bell, carpenter, east door', flush=True)

    # After the tower, before badge 3.
    state(True, False)
    t = talk(g, CITY, (20, 15), K.KEY_LEFT)
    assert 'sweep the tower steps' in t and 'LEAGUE' not in t, t
    seen['tower_door_after'] = t
    t = talk(g, CITY, (19, 23), K.KEY_UP)
    assert 'top of the shadows' in t, t
    seen['lamps_after'] = t
    t = talk(g, CITY, (36, 42), K.KEY_UP)
    assert 'pulled the old ceremonial' in t, t
    seen['bell_after'] = t
    t = talk(g, CITY, (52, 50), K.KEY_UP)
    assert 'heartbeat' in t, t
    seen['carpenter_after'] = t
    t = talk(g, CITY, (53, 42), K.KEY_RIGHT)
    assert 'signs your BADGE' in t and 'Door is open' not in t, t
    seen['east_door_after'] = t
    print('ok  post-tower: tower door, lamps, bell, carpenter, east door', flush=True)

    # After badge 3: the lamp-trimmer no longer sends the player to MORTY.
    state(True, True)
    t = talk(g, CITY, (19, 23), K.KEY_UP)
    assert 'trimmed a wick' in t and 'waiting at the top' not in t, t
    seen['lamps_badge'] = t
    t = talk(g, CITY, (20, 15), K.KEY_LEFT)
    assert t == seen['tower_door_after'], t
    print('ok  post-badge: lamp-trimmer variant, tower sweeper unchanged', flush=True)

    # House 2 trade: offer names both species, B declines.
    g.flag('FLAG_POX_ECRUTEAK_RELICANTH_TRADE', False)
    t = talk(g, HOUSE, (2, 4), K.KEY_UP, key=K.KEY_B)
    assert 'RELICANTH' in t.upper() and 'CLAMPERL' in t.upper() and 'rain barrel' in t, t
    assert 'No hurry' in t, t
    seen['trade_offer'] = t
    g.flag('FLAG_POX_ECRUTEAK_RELICANTH_TRADE', True)
    t = talk(g, HOUSE, (2, 4), K.KEY_UP)
    assert 'opened for the first time' in t and 'Trade me' not in t, t
    seen['trade_done'] = t
    t = talk(g, HOUSE, (5, 5), K.KEY_UP)
    assert 'grandmother' in t, t
    print('ok  House 2 RELICANTH trade: offer, decline, completed state', flush=True)

    texts = list(seen.values())
    dupes = {k for k, v in seen.items() if texts.count(v) > 1 and k != 'tower_door_after'}
    assert not dupes, dupes
    print('ok  every observed Ecruteak line is distinct', flush=True)


if __name__ == '__main__':
    main()
