#!/usr/bin/env python3
"""Playtest restored Johto trainers, daily Sitrus harvest, and the city seam."""
import json
import struct
import sys
from test_story import ROOT, StoryGame
from test_camera_seam import check_view
from test_opening_trainers import start_battle, expected_party_size
from test_sudowoodo_v1 import bag, const, POCKET_BERRIES
from test_national_park import call, set_weekday, IDS, finish_dialogue
from test_qol import opcode
from test_training_kit import run_code
from walk_demo import cross_connection
from walk_leg1 import navigate
from walklib import K

sys.path.insert(0, str(ROOT / 'plastic_ox/alpha'))
from region_geometry import Geometry

NEW = json.loads((ROOT / 'plastic_ox/alpha/johto_outdoors/trainers.json').read_text())
CASES = [
    ('Route36_hns', 24, 28, K.KEY_UP, 'TRAINER_PLASTIC_OX_PU_ROUTE36'),
    ('Route36_hns', 31, 27, K.KEY_UP, 'TRAINER_PLASTIC_OX_JOHTO_ALAN'),
    ('Route37_hns', 13, 31, K.KEY_UP, 'TRAINER_PLASTIC_OX_JOHTO_ANN_ANNE'),
    ('Route37_hns', 14, 31, K.KEY_UP, 'TRAINER_PLASTIC_OX_JOHTO_ANN_ANNE'),
    ('Route37_hns', 28, 31, K.KEY_UP, 'TRAINER_PLASTIC_OX_JOHTO_GREG'),
    ('NationalPark_Normal_hns', 11, 30, K.KEY_UP, 'TRAINER_PLASTIC_OX_JOHTO_BEVERLY'),
    ('NationalPark_Normal_hns', 25, 34, K.KEY_UP, 'TRAINER_PLASTIC_OX_JOHTO_JACK'),
    ('NationalPark_Normal_hns', 11, 16, K.KEY_UP, 'TRAINER_PLASTIC_OX_JOHTO_KRISE'),
    ('NationalPark_Normal_hns', 25, 13, K.KEY_UP, 'TRAINER_PLASTIC_OX_PU_PARK'),
]


def static():
    flags = [data['flag'] for data in NEW.values()]
    assert len(set(flags)) == 6
    for name, count in [('Route36_hns', 2), ('Route37_hns', 3), ('NationalPark_Normal_hns', 4)]:
        geom = Geometry(name)
        trainers = [o for o in geom.data['object_events'] if o['trainer_type'] == 'TRAINER_TYPE_NORMAL']
        assert len(trainers) == count, (name, trainers)
        assert all(geom.passable(o['x'], o['y']) for o in trainers)
    route, city = Geometry('Route37_hns'), Geometry('EcruteakCity_hns')
    assert [x for x in range(route.w) if route.passable(x, 0)] == [16,17,18,19]
    assert [x for x in range(city.w) if city.passable(x, city.h - 1)] == [32,33,34,35]
    for x in range(16,20):
        assert (x,0) in route.component((18,39))
        assert (x+16,60) in city.component((33,48))
        assert route.tile(x,0)[1] == city.tile(x+16,60)[1] == 3
    print('Trainer counts, distinct save flags, and reachable aligned road PASS', flush=True)


def trainers():
    # Execute the compiled flag mapping, including the newly reserved slots.
    g = StoryGame()
    for trainer, data in NEW.items():
        run_code(g, opcode(g, 'settrainerflag') + struct.pack('<H', data['id']))
        assert g.flag(data['flag']), trainer
        run_code(g, opcode(g, 'cleartrainerflag') + struct.pack('<H', data['id']))
        assert not g.flag(data['flag']), trainer
    print('Compiled trainer victory mappings use six independent persistent flags PASS', flush=True)
    for name,x,y,key,trainer in CASES:
        g = StoryGame()
        g.run('Pox_Squirtle')
        start_battle(g,name,x,y,key,trainer)
        assert g.u8(g.syms['gPartiesCount'] + 1) == expected_party_size(trainer), trainer
        g.shot('johto_' + trainer.removeprefix('TRAINER_PLASTIC_OX_').lower() + '.png')
        print(trainer, 'sight battle and expected party size PASS', flush=True)
    g = StoryGame()
    g.run('Pox_Squirtle')
    g.flag(NEW['TRAINER_PLASTIC_OX_JOHTO_ANN_ANNE']['flag'], True)
    for script in ('Route37_EventScript_Ann','Route37_EventScript_Anne'):
        g.warp('Route37_hns',18,32)
        g.run(script)
        assert not g.u32(g.syms['gBattleTypeFlags']) & 8
    print('Both twins honor their shared victory flag PASS', flush=True)
    for name,x,y,key,trainer in CASES[-4:]:
        g = StoryGame()
        flag = NEW[trainer]['flag'] if trainer in NEW else 0x4A0 + g.const(trainer) - 857
        g.flag(flag, True)
        g.warp(name,x,y)
        g.tap(key,hold=18,wait=100)
        assert g.u8(g.syms['sGlobalScriptContextStatus']) == 2, trainer
        assert not g.u32(g.syms['gBattleTypeFlags']) & 8, trainer
    print('Defeated park trainers leave passing visitors alone PASS', flush=True)


def seam():
    g = StoryGame()
    for enabled in (True, False):
        g.flag('FLAG_POX_TRIGGERS_ENABLED', enabled)
        for x in range(16,20):
            g.warp('Route37_hns',x,1)
            g.walk('UP',target=(x,0))
            cross_connection(g,'UP',IDS['EcruteakCity_hns'],f'johto_north_{x}_{enabled}')
            assert (g.state()['x'],g.state()['y']) == (x+16,60),g.state()
            check_view(g,f'johto_city_{x}_{enabled}')
            cross_connection(g,'DOWN',IDS['Route37_hns'],f'johto_south_{x}_{enabled}')
            assert (g.state()['x'],g.state()['y']) == (x,0),g.state()
            check_view(g,f'johto_route_{x}_{enabled}')
    g.flag('FLAG_POX_TRIGGERS_ENABLED',True)
    g.warp('Route37_hns',19,12)
    g.walk('UP',target=(19,11))
    assert (g.state()['group'],g.state()['num']) == IDS['Route37_hns']
    navigate(g,(17,0))
    cross_connection(g,'UP',IDS['EcruteakCity_hns'],'johto_full_entrance')
    navigate(g,(33,48))
    g.shot('johto_ecruteak_arch.png')
    navigate(g,(33,60))
    cross_connection(g,'DOWN',IDS['Route37_hns'],'johto_full_return')
    navigate(g,(17,13))
    g.shot('johto_route37_entrance.png')
    for x in (15,20):
        g.warp('Route37_hns',17,1)
        assert g.collision_at(x,0)[0] != 0
    print('Four lanes both ways, both trigger modes, clean redraws, full arch walk, old teleport removed PASS',flush=True)


def berries():
    g = StoryGame()
    item = const('ITEM_SITRUS_BERRY','items.h')
    g.flag('FLAG_SYS_CLOCK_SET',True)
    g.warp('Route37_hns',33,25)
    before = bag(g,item,POCKET_BERRIES)
    g.tap(K.KEY_UP,hold=2,wait=10)
    g.tap(K.KEY_A,hold=2,wait=20)
    finish_dialogue(g)
    assert bag(g,item,POCKET_BERRIES) == before + 5
    assert g.flag('FLAG_POX_DAILY_R37_SITRUS')
    assert not g.flag('FLAG_POX_DAILY_R46_SITRUS')
    g.run('PlasticOx_BerryTree_Route37Sitrus')
    assert bag(g,item,POCKET_BERRIES) == before + 5
    call(g,'ClearDailyFlags')
    assert not g.flag('FLAG_POX_DAILY_R37_SITRUS')
    g.run('PlasticOx_BerryTree_Route37Sitrus')
    assert bag(g,item,POCKET_BERRIES) == before + 10
    g.shot('johto_route37_sitrus_tree.png')
    print('Real tree interaction: five Sitrus, once daily, independent Route 46 flag, real daily reset PASS',flush=True)


def contest():
    g=StoryGame()
    g.run('Pox_Squirtle')
    g.flag('FLAG_SYS_CLOCK_SET',True)
    set_weekday(g,2)
    g.warp('Gate_NationalPark_hns',3,3)
    g.tap(K.KEY_UP,hold=2,wait=12)
    g.tap(K.KEY_A,hold=2,wait=30)
    finish_dialogue(g)
    assert g.u8(g.syms['sRunning'])
    for trainer in ('NationalPark_EventScript_Beverly','NationalPark_EventScript_Jack','NationalPark_EventScript_Krise','Pox_PU_PARK'):
        g.run(trainer)
        assert not g.u32(g.syms['gBattleTypeFlags']) & 8
    navigate(g,(25,33))
    navigate(g,(25,31))
    g.frame(40)
    assert (g.state()['x'],g.state()['y']) == (25,31)
    assert g.u8(g.syms['sGlobalScriptContextStatus']) == 2
    print('Contest suppresses park sight battles and trainer interactions PASS',flush=True)


if __name__ == '__main__':
    static()
    seam()
    berries()
    trainers()
    contest()
