#!/usr/bin/env python3
"""Route 110's three exits and the Route 36 sleeper, walked in a fresh ROM.

All three are native camera connections (region_v7.SEAM_TRAILS), so every
lane must cross both ways keeping its row or column, with no fade:

  Fortree City (39, 7..10)   <-> Route 110 (0, 2..5)         badge 4
  Route 36     (65, 18..22)  <-> Route 110 (0, 67..71)       reached Fortree
  Route 110    (15..19, 99)  <-> Lavender Town (12..16, 0)   badge 4

Before its flag each gate refuses on the edge tile and steps the player back.
On Route 36 a hiker sleeps across the eastern road at (43,19); he only
mumbles until the player holds Winona's badge, then wakes and walks off.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_story import StoryGame
from test_burned_tower import at, shot
from test_sudowoodo_v1 import CHARMAP, drain
from walklib import K

# source, edge axis, edge coordinate, lanes, key out, key back, destination,
# lane shift (destination lane = source lane + shift), gate flag
SEAMS = [
    ('FortreeCity', 'x', 39, range(7, 11), K.KEY_RIGHT, K.KEY_LEFT, 'Route110', -5, 'FLAG_BADGE04_GET'),
    ('Route36_hns', 'x', 65, range(18, 23), K.KEY_RIGHT, K.KEY_LEFT, 'Route110', 49, 'FLAG_POX_REACHED_FORTREE'),
    ('Route110', 'y', 99, range(15, 20), K.KEY_DOWN, K.KEY_UP, 'LavenderTown_hns', -3, 'FLAG_BADGE04_GET'),
]


def pos(g):
    s = g.state()
    return s['x'], s['y']


def walk_until(g, key, name, limit=12):
    for _ in range(limit):
        g.hold(key, 16)
        if at(g, name):
            g.frame(120)
            return
    raise AssertionError(('never reached', name, g.describe()))


def talk(g, key):
    """Face `key`, press A and drive the object script to its end."""
    buf = g.syms['gStringVar4']
    g.write(buf, 0xFF)
    g.tap(key, hold=2, wait=16)
    seen = []
    for _ in range(300):
        g.tap(K.KEY_A, hold=2, wait=16)
        text = ''
        for i in range(400):
            b = g.u8(buf + i)
            if b == 0xFF:
                break
            text += CHARMAP.get(b, '?')
        if text and text not in seen:
            seen.append(text)
        if seen and g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            break
    return dict(dialogue=bool(seen), text=seen)


def start(axis, edge, lane, back=1):
    return (edge - back, lane) if axis == 'x' else (lane, edge - back)


def seams(g):
    for source, axis, edge, lanes, out, home, dest, shift, gate in SEAMS:
        g.flag(gate, False)
        for lane in (lanes[0], lanes[-1]):
            g.warp(source, *start(axis, edge, lane)); g.frame(60)
            g.hold(out, 60)
            for _ in range(20):
                g.hold(K.KEY_B, 4); g.frame(20)
            drain(g); g.frame(60)
            assert at(g, source), (source, lane, g.describe())
            here = pos(g)[0] if axis == 'x' else pos(g)[1]
            assert here < edge, (source, lane, g.describe())
        print('ok  closed', source, '->', dest, 'refuses and steps back', flush=True)

        g.flag(gate, True)
        for lane in lanes:
            g.warp(source, *start(axis, edge, lane)); g.frame(60)
            walk_until(g, out, dest)
            there = pos(g)
            across, along = (there[1], there[0]) if axis == 'x' else (there[0], there[1])
            assert across == lane + shift and along <= 2, (source, lane, g.describe())
            if lane == lanes[1]:
                shot(g, f'route110_seam_{source}_to_{dest}.png')
            walk_until(g, home, source)
            back = pos(g)
            across, along = (back[1], back[0]) if axis == 'x' else (back[0], back[1])
            assert across == lane and along >= edge - 2, (source, lane, g.describe())
            if lane == lanes[1]:
                shot(g, f'route110_seam_{dest}_to_{source}.png')
        print('ok ', source, '<->', dest, 'every lane, both ways', flush=True)


def sleeper(g):
    g.flag('FLAG_POX_SUDOWOODO_CLEARED', True)
    g.flag('FLAG_POX_ROUTE36_SLEEPER_MOVED', False)
    g.flag('FLAG_BADGE04_GET', False)
    g.warp('Route36_hns', 42, 19); g.frame(80)
    shot(g, 'route36_sleeper_asleep.png')
    result = talk(g, K.KEY_RIGHT)
    assert result['dialogue'] and 'feather' in ' '.join(result['text']), result
    drain(g); g.frame(30)
    g.hold(K.KEY_RIGHT, 40)
    assert pos(g) == (42, 19) and not g.flag('FLAG_POX_ROUTE36_SLEEPER_MOVED'), g.describe()
    print('ok  sleeper stays put without the Fortree badge:', result['text'][-1][:40], flush=True)

    g.flag('FLAG_BADGE04_GET', True)
    result = talk(g, K.KEY_RIGHT)
    assert result['dialogue'], result
    assert drain(g, 1500), g.describe()
    g.frame(30)
    assert g.flag('FLAG_POX_ROUTE36_SLEEPER_MOVED'), result
    shot(g, 'route36_sleeper_gone.png')
    g.hold(K.KEY_RIGHT, 16 * 6)
    assert at(g, 'Route36_hns') and pos(g)[0] >= 46, g.describe()
    print('ok  sleeper wakes for the Fortree badge and the east road opens', flush=True)

    # From the Route 110 side he leaves west instead of through the player.
    g.flag('FLAG_POX_ROUTE36_SLEEPER_MOVED', False)
    g.warp('Route36_hns', 44, 19); g.frame(80)
    result = talk(g, K.KEY_LEFT)
    assert result['dialogue'] and drain(g, 1500), (result, g.describe())
    g.frame(30)
    assert g.flag('FLAG_POX_ROUTE36_SLEEPER_MOVED') and pos(g) == (44, 19), g.describe()
    g.hold(K.KEY_LEFT, 16 * 3)
    assert pos(g)[0] <= 42, g.describe()
    print('ok  sleeper also clears the road when woken from the east', flush=True)


def main():
    g = StoryGame()
    for f in ('FLAG_POX_STORY_STARTER', 'FLAG_ADVENTURE_STARTED',
              'FLAG_POX_TRIGGERS_ENABLED', 'FLAG_BADGE03_GET', 'FLAG_POX_STORY_WEATHER'):
        g.flag(f, True)
    g.write(g.syms['sWildEncountersDisabled'], 1)
    seams(g)
    sleeper(g)
    print('PASS: Route 110 seams and Route 36 sleeper', flush=True)


if __name__ == '__main__':
    main()
