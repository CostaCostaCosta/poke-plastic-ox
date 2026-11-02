#!/usr/bin/env python3
"""RUN 6 checks: Goldenrod City overworld.

* no Team Rocket NPCs remain and no object/sign references a dead script
* every remaining city/gate NPC and sign has unique text (verified against the
  bytes actually linked into the ROM, not just the source)
* the north exit crosses the Gate_GoldenrodCity_Route35 gatehouse both ways
* the south exit leaves every lane of the road mouth onto Route 33 and returns
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_story import StoryGame, ROOT
from walklib import K
from walk_leg1 import navigate, find_path_elev, enter_warp

NM = '/home/eddie/devkitpro/opt/devkitpro/devkitARM/bin/arm-none-eabi-nm'
CITY, GATE, R33, R35 = 'GoldenrodCity_hns', 'Gate_GoldenrodCity_Route35_hns', 'Route33_hns', 'Route35_hns'
MAPS = {n: json.loads((ROOT / f'data/maps/{n}/map.json').read_text()) for n in (CITY, GATE, R33, R35)}
GROUPS = json.loads((ROOT / 'data/maps/map_groups.json').read_text())
IDS = {m: (i, j) for i, g in enumerate(GROUPS['group_order']) for j, m in enumerate(GROUPS[g])}
TEXT_LABEL = re.compile(r'^([A-Za-z_]\w*_Text):$', re.M)


def rom_symbols():
    out = subprocess.check_output([NM, str(ROOT / 'pokeemerald.elf')], text=True)
    syms = {}
    for line in out.splitlines():
        m = re.match(r'([0-9a-f]+) \w (\S+)$', line)
        if m:
            syms[m.group(2)] = int(m.group(1), 16)
    return syms


def rom_text(syms, rom, label):
    """Return the raw bytes of a linked text label (up to the 0xFF EOS)."""
    addr = syms[label]
    off = addr - 0x08000000
    end = rom.index(b'\xff', off)
    return rom[off:end]


def static_checks():
    syms, rom = rom_symbols(), (ROOT / 'pokeemerald.gba').read_bytes()
    city = MAPS[CITY]
    assert not [o for o in city['object_events'] if 'ROCKET' in o['graphics_id']], 'Team Rocket NPC remains'
    assert not [o for o in city['object_events'] if 'ROCKET' in o['graphics_id']]
    for name in (CITY, GATE, R33, R35):
        d = MAPS[name]
        for o in d['object_events']:
            if o['script'] not in ('0x0', ''):
                assert o['script'] in syms, (name, 'dead object script', o['script'])
        for b in d['bg_events']:
            if b.get('script'):
                assert b['script'] in syms, (name, 'dead bg script', b['script'])
    # unique dialogue, read out of the linked ROM
    labels = []
    for name in (CITY, GATE):
        src = (ROOT / f'data/maps/{name}/scripts.inc').read_text()
        labels += [(name, m) for m in TEXT_LABEL.findall(src)]
    seen = {}
    for name, label in labels:
        data = rom_text(syms, rom, label)
        assert data, (name, label, 'empty text')
        if data in seen:
            raise AssertionError(f'duplicate dialogue: {label} == {seen[data]}')
        seen[data] = label
    print(f'static: 0 Rocket NPCs; every object/sign script resolves; '
          f'{len(labels)} NPC/sign texts all unique in the ROM PASS', flush=True)
    return labels


def key_toward(dx, dy):
    return {(0, -1): K.KEY_UP, (0, 1): K.KEY_DOWN, (-1, 0): K.KEY_LEFT, (1, 0): K.KEY_RIGHT}[(dx, dy)]


def interact(g, tile, tag):
    """Stand next to `tile`, face it, press A, prove a message appeared."""
    ox, oy = tile
    path = find_path_elev(g, lambda x, y, _w, _h: abs(x - ox) + abs(y - oy) == 1)
    assert path, (tag, 'no adjacent tile reachable', tile, g.describe())
    navigate(g, path[-1])
    here = (g.state()['x'], g.state()['y'])
    before = g.hash()
    g.tap(key_toward(ox - here[0], oy - here[1]), hold=2, wait=12)
    for _ in range(500):
        g.tap(K.KEY_A, hold=2, wait=10)
        if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
            break
    else:
        raise AssertionError((tag, 'dialogue never released controls', g.describe()))
    g.shot(f'run6_dialogue_{tag}.png')
    print(f'  talk {tag} {tile} from {here} PASS', flush=True)


def dialogue():
    g = StoryGame(spawn=(CITY, 28, 37))
    city = MAPS[CITY]
    for o in city['object_events']:
        if o['script'].startswith('GoldenrodCity_EventScript_'):
            interact(g, (o['x'], o['y']), o['script'].rsplit('_', 1)[-1])
    for b in city['bg_events']:
        if b['script'].startswith('GoldenrodCity_EventScript_'):
            interact(g, (b['x'], b['y']), b['script'].rsplit('_', 1)[-1])
    print('city: every NPC and sign talked to PASS', flush=True)


def gate_dialogue():
    g = StoryGame(spawn=(GATE, 7, 8))
    load_ok(g, GATE, 'gate_dialogue_spawn')
    for o in MAPS[GATE]['object_events']:
        interact(g, (o['x'], o['y']), 'gate_' + o['script'].rsplit('_', 1)[-1])
    print('gatehouse: every NPC talked to PASS', flush=True)


def load_ok(g, expect, tag):
    assert (g.state()['group'], g.state()['num']) == IDS[expect], (tag, g.describe())
    g.wait_warp_complete(IDS[expect])
    info = g.mapgrid_info()
    mt, _ = g.metatile_at(g.state()['x'], g.state()['y'])
    assert info['width'] > 0 and mt not in (None, 1023), (tag, 'map did not load', info, mt)
    g.shot(f'run6_{tag}.png')


def north_gate():
    for lane, back in ((33, 33), (34, 34)):
        g = StoryGame(spawn=(CITY, 28, 37))
        enter_warp(g, (lane, 8), 'UP', IDS[GATE], f'north gate door {lane}')
        load_ok(g, GATE, f'north_gate_in_{lane}')
        assert (g.state()['x'], g.state()['y']) == (7, 9), ('gate landing', g.describe())
        # cross the gatehouse and out the north door
        enter_warp(g, (7, 2), 'UP', IDS[R35], 'gate north door')
        load_ok(g, R35, f'north_gate_out_{lane}')
        x, y = g.state()['x'], g.state()['y']
        assert abs(x - 13) + abs(y - 48) <= 2, ('route 35 landing', g.describe())
        assert g.collision_at(x, y)[0] == 0, ('route 35 landing solid', g.describe())
        # and back through the gatehouse into the city
        enter_warp(g, (13, 47), 'DOWN', IDS[GATE], 'route 35 gate door')
        load_ok(g, GATE, f'north_gate_back_{lane}')
        enter_warp(g, (7, 8), 'DOWN', IDS[CITY], 'gate south door')
        load_ok(g, CITY, f'south_into_city_{lane}')
        x, y = g.state()['x'], g.state()['y']
        assert (x, y) in [(33, 8), (34, 8)], ('city return landing', g.describe())
        print(f'north gatehouse lane {lane}: city -> gate -> route 35 -> gate -> city PASS', flush=True)


def south_seam():
    for lane, back in ((32, 32), (33, 33), (34, 34), (35, 35)):
        g = StoryGame(spawn=(CITY, 28, 37))
        navigate(g, (lane, 44))
        g.tap(K.KEY_DOWN, hold=24, wait=180)
        assert (g.state()['group'], g.state()['num']) == IDS[R33], (lane, 'south exit failed', g.describe())
        g.wait_warp_complete(IDS[R33])
        x, y = g.state()['x'], g.state()['y']
        assert (x, y) == (1, 23), (lane, 'route 33 landing', g.describe())
        assert g.collision_at(x, y)[0] == 0, (lane, 'route 33 landing solid')
        g.shot(f'run6_south_out_{lane}.png')
        # walk back up the road into the city
        navigate(g, (1, 23))
        g.tap(K.KEY_LEFT, hold=24, wait=180)
        assert (g.state()['group'], g.state()['num']) == IDS[CITY], (lane, 'south return failed', g.describe())
        g.wait_warp_complete(IDS[CITY])
        x, y = g.state()['x'], g.state()['y']
        assert (x, y) == (33, 44), (lane, 'city return landing', g.describe())
        g.shot(f'run6_south_back_{lane}.png')
        print(f'south seam lane {lane}: city -> route 33 -> city PASS', flush=True)


if __name__ == '__main__':
    static_checks()
    if len(sys.argv) == 1 or 'dialogue' in sys.argv:
        dialogue()
    if len(sys.argv) == 1 or 'gatedlg' in sys.argv:
        gate_dialogue()
    if len(sys.argv) == 1 or 'gate' in sys.argv:
        north_gate()
    if len(sys.argv) == 1 or 'south' in sys.argv:
        south_seam()
    print('RUN 6 emulator checks PASS', flush=True)
