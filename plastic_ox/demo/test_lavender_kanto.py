#!/usr/bin/env python3
"""Lavender -> Route 8 -> Underground Path -> Route 7, and Saffron's gates.

Walked with the D-pad in a fresh ROM; spawn warps only place the player.

* Lavender Town (0, 9..11) <-> Route 8 (67, 19..21) is a native camera
  connection (region_v7.SEAM_TRAILS, offset -10). Before FLAG_POX_STORY_FUJI
  every lane refuses on Lavender's edge and steps back; after it every lane
  crosses both ways keeping its row.
* Route 8's tunnel hut door (12,18) -> UndergroundPath_EastEntrance -> the
  east-west tunnel -> UndergroundPath_WestEntrance -> Route 7's hut door
  (7,16), and back in through that door.
* Route 7's west road (0, 4..7) leads to Route 103 once FUJI is done.
* Route 7's grass patch is behind a Cut tree: every lane of row 10 blocks,
  and Cut on the tree at (13,10) lets the player into the grass.
* Saffron's gatehouses are arrow doorways into the FRLG gate rooms:
  Route 8 (3,21) <-> Route8_WestEntrance <-> Saffron (62,27) and
  Route 7 (15,12) <-> Route7_EastEntrance <-> Saffron (2,27). The room's
  guard turns the player back until FLAG_POX_STORY_SPACE_CENTER.
* Screenshots of the seam and of the Pokemon Tower's crown above Lavender
  (src/plastic_ox_borders.c) go to plastic_ox/demo/shots/lavender_kanto_*.png.
"""
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_story import StoryGame  # noqa: E402
from test_burned_tower import at  # noqa: E402
from test_sudowoodo_v1 import drain  # noqa: E402
from walk_leg1 import navigate  # noqa: E402
from walklib import K  # noqa: E402
from test_national_park import finish_dialogue  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

SHOTS = Path(__file__).resolve().parent / 'shots'
FUJI = 'FLAG_POX_STORY_FUJI'
SPACE = 'FLAG_POX_STORY_SPACE_CENTER'


def shot(g, name):
    SHOTS.mkdir(exist_ok=True)
    g.fb.to_pil().convert('RGB').save(SHOTS / name)


def pos(g):
    s = g.state()
    return s['x'], s['y']


def walk_until(g, key, name, limit=14):
    for _ in range(limit):
        g.hold(key, 16)
        if at(g, name):
            g.frame(120)
            return
    raise AssertionError(('never reached', name, g.describe()))


def place(g, name, x, y):
    g.warp(name, x, y)
    g.frame(60)


def refuse(g):
    """Let a refusal message and its step back play out."""
    for _ in range(20):
        g.hold(K.KEY_B, 4)
        g.frame(20)
    drain(g)
    g.frame(60)


def lavender_route8(g):
    g.flag(FUJI, False)
    for lane in (9, 10, 11):
        place(g, 'LavenderTown_hns', 1, lane)
        g.hold(K.KEY_LEFT, 60)
        refuse(g)
        assert at(g, 'LavenderTown_hns') and pos(g)[0] >= 1, (lane, g.describe())
    print('ok  Lavender -> Route 8 refuses on every lane before FUJI', flush=True)

    g.flag(FUJI, True)
    for lane in (9, 10, 11):
        place(g, 'LavenderTown_hns', 2, lane)
        walk_until(g, K.KEY_LEFT, 'Route8_Frlg')
        x, y = pos(g)
        assert y == lane + 10 and x >= 65, (lane, g.describe())
        if lane == 10:
            shot(g, 'lavender_kanto_route8_side.png')
        walk_until(g, K.KEY_RIGHT, 'LavenderTown_hns')
        x, y = pos(g)
        assert y == lane and x <= 2, (lane, g.describe())
        if lane == 10:
            shot(g, 'lavender_kanto_lavender_side.png')
    print('ok  Lavender (0,9..11) <-> Route 8 (67,19..21) walks both ways', flush=True)


def underground(g):
    place(g, 'Route8_Frlg', 12, 21)
    navigate(g, (12, 19))
    shot(g, 'lavender_kanto_route8_tunnel_hut.png')
    walk_until(g, K.KEY_UP, 'UndergroundPath_EastEntrance_Frlg')
    # FRLG stair warps fire when walked onto along the way they run.
    navigate(g, (8, 4))
    walk_until(g, K.KEY_LEFT, 'UndergroundPath_EastWestTunnel_Frlg')
    navigate(g, (4, 4))
    walk_until(g, K.KEY_LEFT, 'UndergroundPath_WestEntrance_Frlg')
    navigate(g, (6, 7))
    walk_until(g, K.KEY_DOWN, 'Route7_hns')
    g.hold(K.KEY_DOWN, 16)
    g.frame(30)
    assert pos(g)[0] == 7 and 16 <= pos(g)[1] <= 18, g.describe()
    shot(g, 'lavender_kanto_route7_tunnel_hut.png')
    print('ok  Route 8 hut -> Underground Path -> Route 7 hut door', g.describe(), flush=True)
    navigate(g, (7, 17))
    walk_until(g, K.KEY_UP, 'UndergroundPath_WestEntrance_Frlg')
    print('ok  Route 7 hut door leads back into the Underground Path', flush=True)
    place(g, 'UndergroundPath_EastEntrance_Frlg', 6, 7)
    walk_until(g, K.KEY_DOWN, 'Route8_Frlg')
    g.hold(K.KEY_DOWN, 16)
    g.frame(30)
    assert pos(g)[0] == 12 and 18 <= pos(g)[1] <= 20, g.describe()
    navigate(g, (11, 19))
    g.hold(K.KEY_UP, 32)
    assert pos(g) == (11, 19), ('walked through the hut', g.describe())
    print('ok  Route 8 hut is a building with a door, not a lane', g.describe(), flush=True)


def route7_route103(g):
    g.flag(FUJI, True)
    for lane in (4, 5, 6, 7):
        place(g, 'Route7_hns', 2, lane)
        walk_until(g, K.KEY_LEFT, 'Route103')
    print('ok  Route 7 west road (0,4..7) leads to Route 103', flush=True)


def route7_cut(g):
    """Route 7's grass patch (11..18, 4..9) is fenced off along row 10 except
    for a Cut tree at (13,10) (route7_cut_hedge.py, region_v7.py)."""
    for lane in range(11, 16):
        place(g, 'Route7_hns', lane, 11)
        g.hold(K.KEY_UP, 32)
        assert pos(g) == (lane, 11), ('walked into the grass without Cut', lane, g.describe())
    place(g, 'Route7_hns', 13, 12)
    shot(g, 'lavender_kanto_route7_cut_tree.png')
    navigate(g, (13, 11))
    item = int(re.search(r'ITEM_CUT_KEY\s*=\s*(\d+)',
                         (ROOT / 'include/constants/items.h').read_text())[1])
    ptr = g.syms['gStringVar4']
    code = bytes([0x44]) + struct.pack('<HH', item, 1) + bytes([0x6C, 2])  # additem; end
    for i, b in enumerate(code):
        g.write(ptr + i, b)
    g.run(ptr)
    g.tap(K.KEY_UP, hold=2, wait=12)
    g.tap(K.KEY_A, wait=30)
    finish_dialogue(g)
    navigate(g, (13, 8))
    assert pos(g) == (13, 8), g.describe()
    print('ok  Route 7 grass is fenced off on every lane; Cut opens the tree at (13,10)', flush=True)


def gate(g, outside, arrow, out_key, room, saffron, saffron_arrow, back_key, room_exit):
    ax, ay = arrow
    dx = -1 if out_key == K.KEY_LEFT else 1
    g.flag(SPACE, False)
    place(g, outside, ax - dx, ay)
    walk_until(g, out_key, room)
    entry = pos(g)
    for _ in range(8):
        g.hold(out_key, 16)
        if g.u8(g.syms['sGlobalScriptContextStatus']) != 2:
            break
    refuse(g)
    assert at(g, room), g.describe()
    assert (pos(g)[0] - 6) * dx < 0, ('guard let the player past', g.describe())
    print('ok ', outside, 'gate room guard holds the line before the Space Center', flush=True)
    walk_until(g, back_key, outside)
    assert pos(g) == arrow, g.describe()
    g.hold(back_key, 16)
    print('ok ', room, 'walks back out to', outside, pos(g), flush=True)

    g.flag(SPACE, True)
    place(g, outside, ax - dx, ay)
    walk_until(g, out_key, room)
    assert pos(g) == entry, g.describe()
    walk_until(g, out_key, saffron, limit=20)
    assert pos(g) == saffron_arrow, g.describe()
    g.hold(out_key, 32)
    g.frame(30)
    shot(g, f'lavender_kanto_{room}_saffron.png')
    navigate(g, (saffron_arrow[0] + dx, saffron_arrow[1]))
    walk_until(g, back_key, room)
    navigate(g, room_exit)
    walk_until(g, back_key, outside, limit=20)
    assert pos(g) == arrow, g.describe()
    print('ok ', outside, arrow, '<->', room, '<->', saffron, saffron_arrow, 'both ways', flush=True)


def tower(g):
    for x, y, name in [(16, 0, 'road'), (21, 7, 'door'), (14, 3, 'west')]:
        place(g, 'LavenderTown_hns', x, y)
        shot(g, f'lavender_kanto_tower_{name}.png')
    print('ok  tower crown screenshots written', flush=True)


def main():
    g = StoryGame()
    for f in ('FLAG_POX_STORY_STARTER', 'FLAG_ADVENTURE_STARTED', 'FLAG_POX_TRIGGERS_ENABLED',
              'FLAG_BADGE04_GET', 'FLAG_POX_FUJI_RESCUED'):
        g.flag(f, True)
    g.write(g.syms['sWildEncountersDisabled'], 1)
    tower(g)
    lavender_route8(g)
    underground(g)
    route7_route103(g)
    route7_cut(g)
    gate(g, 'Route8_Frlg', (3, 21), K.KEY_LEFT, 'Route8_WestEntrance_Frlg',
         'SaffronCity_hns', (62, 27), K.KEY_RIGHT, (10, 5))
    gate(g, 'Route7_hns', (15, 12), K.KEY_RIGHT, 'Route7_EastEntrance_Frlg',
         'SaffronCity_hns', (2, 27), K.KEY_LEFT, (2, 5))
    print('PASS: Lavender, Route 8, Underground Path, Route 7 and the Saffron gates', flush=True)


if __name__ == '__main__':
    main()
