#!/usr/bin/env python3
"""FireRed floor parity, every directed warp, continuous path, and fossil state."""
import json
import re
import sys
from pathlib import Path
from test_story import StoryGame, ROOT
from walklib import K, DIRKEY
sys.path.insert(0, str(ROOT/'plastic_ox/alpha'))
from region_geometry import Geometry
from mt_moon import FLOORS, BASE
sys.path.insert(0, str(ROOT/'plastic_ox/agent'))
from apply_trainer_teams_v2 import expected_party_size, ROSTERS

GROUPS = json.loads((ROOT/'data/maps/map_groups.json').read_text())
IDS = {n:(i,j) for i,k in enumerate(GROUPS['group_order']) for j,n in enumerate(GROUPS[k])}
MAPS = {n:json.loads((ROOT/f'data/maps/{n}/map.json').read_text()) for n in FLOORS+['Route33_hns','Route44_hns']}
BYID = {d['id']:n for n,d in MAPS.items()}
TRAINERS = json.loads((BASE/'trainers.json').read_text())
SPECIES_IDS = {name: int(value) for name, value in re.findall(
    r'(SPECIES_\w+)\s*=\s*(\d+)', (ROOT/'include/constants/species.h').read_text())}


def source_test():
    import hashlib
    manifest=json.loads((BASE/'source_manifest.json').read_text())
    for floor,source in manifest['floors'].items():
        name=f'MtMoon_{floor}_Frlg';d=MAPS[name]
        for filename,digest in source['layout_sha256'].items():
            assert hashlib.sha256((ROOT/f'data/layouts/{name}/{filename}').read_bytes()).hexdigest()==digest
        for i,(actual,original) in enumerate(zip(d['warp_events'],source['warp_events'])):
            if (floor,i) in [('1F',3),('B1F',7)]:
                assert [actual[k] for k in ['x','y','elevation']]==[original[k] for k in ['x','y','elevation']]
            else:assert actual==original,(floor,i)
        assert len(d['warp_events'])==len(source['warp_events'])
        assert [[o['x'],o['y'],o['script']] for o in d['object_events']]==source['object_positions']
        assert [[o['x'],o['y'],o['type']] for o in d['bg_events']]==source['bg_positions']
    from mt_moon import install
    changes={}
    install(lambda p:(ROOT/p).read_text(),lambda p,s:changes.update({p:s}) if (ROOT/p).read_text()!=s else None)
    assert not changes,list(changes)
    print('FireRed geometry, all warp/object/item coordinates, regeneration stability PASS',flush=True)


def assert_map(g, name):
    s=g.state()
    assert (s['group'],s['num'])==IDS[name], (name,s)
    return s


def setup():
    g=StoryGame()
    g.flag('FLAG_BADGE01_GET',True)
    for tid in range(857,926): g.flag(0x4A0+tid-857,True)
    g.setvar(0x40F9,1)
    return g


def warp_tests():
    g=setup()
    for name in FLOORS:
        geom=Geometry(name)
        for index,w in enumerate(MAPS[name]['warp_events']):
            dest=BYID[w['dest_map']]; landing=MAPS[dest]['warp_events'][int(w['dest_warp_id'])]
            assert landing['dest_map']==MAPS[name]['id']
            assert int(landing['dest_warp_id'])==index
            attempts=[]
            for direction,dx,dy in [('UP',0,-1),('DOWN',0,1),('LEFT',-1,0),('RIGHT',1,0)]:
                x,y=w['x']-dx,w['y']-dy
                if not geom.passable(x,y):continue
                g.warp(name,x,y)
                g.tap(DIRKEY[direction],hold=24,wait=180)
                s=g.state()
                if (s['group'],s['num'])!=IDS[dest]:
                    attempts.append((direction,s));continue
                g.frame(120)
                s=assert_map(g,dest)
                assert abs(s['x']-landing['x'])+abs(s['y']-landing['y'])<=1,(name,index,s)
                assert g.collision_at(s['x'],s['y'])[0]==0
                g.shot(f'moon_{name}_{index}.png')
                print('warp PASS',name,index,dest,(s['x'],s['y']),flush=True)
                break
            else:raise AssertionError((name,index,attempts))
    g.warp('Route44_hns',67,13)
    g.tap(K.KEY_RIGHT,hold=24,wait=180)
    s=assert_map(g,'MtMoon_1F_Frlg');assert (s['x'],s['y'])==(18,36),s
    g.warp('Route33_hns',27,18)
    g.tap(K.KEY_UP,hold=24,wait=180)
    assert_map(g,'MtMoon_B1F_Frlg')
    print('external approaches PASS',flush=True)




def dismiss(g, limit=500):
    for _ in range(limit):
        g.tap(K.KEY_A,hold=2,wait=10)
        if g.u8(g.syms['sGlobalScriptContextStatus'])==2:
            g.frame(120)
            return
    raise AssertionError(('field script hung',g.state()))


def finish_battle(g, outcome=1):
    # Exercise the real finish handler; the battle outcome is a test fixture.
    g.frame(240)
    g.write(g.syms['gBattleOutcome'],outcome)
    g.write(g.syms['gCurrentActionFuncId'],11)
    g.write(g.syms['gBattleMainFunc'],g.syms['HandleEndTurn_FinishBattle']|1,4)
    g.frame(240)
    dismiss(g)
    # The engine retains the last battle type after returning to the field.
    g.write(g.syms['gBattleTypeFlags'],0,4)


def wait_battle(g, trainer):
    for _ in range(300):
        g.tap(K.KEY_A,hold=2,wait=10)
        if g.u32(g.syms['gBattleTypeFlags'])&8:break
    else:raise AssertionError(('battle never started',trainer,g.state()))
    assert g.u16(g.syms['gTrainerBattleParameter']+2)==TRAINERS[trainer]
    g.frame(240)
    count = g.u8(g.syms['gPartiesCount'] + 1)
    assert count == expected_party_size(trainer), (trainer, count)
    stride = g.sizes['gParties'] // 24
    enemy = g.syms['gParties'] + 6 * stride
    actual = [g.box_species(enemy + i * stride) for i in range(count)]
    expected = [SPECIES_IDS[species] for species, level in ROSTERS[trainer][1]]
    assert actual == expected, (trainer, actual, expected)
    levels = [g.u8(enemy + i * stride + stride - 16) for i in range(count)]
    assert all(authored <= actual_level <= 20
               for (_, authored), actual_level in zip(ROSTERS[trainer][1], levels)), (trainer, levels)
    g.shot('moon_battle_'+trainer+'.png')


def fossil_tests():
    for fossil,x in [('Dome',13),('Helix',14)]:
        g=StoryGame();g.run('Pox_Squirtle')
        # Cross the original Miguel trigger from below.
        g.warp('MtMoon_B2F_Frlg',14,12)
        g.tap(K.KEY_UP,hold=16,wait=30)
        wait_battle(g,'TRAINER_PLASTIC_OX_MOON_SUPER_NERD_MIGUEL')
        assert g.var(0x40F9)==0
        assert not g.flag('FLAG_POX_STORY_MTMOON')
        finish_battle(g)
        assert g.var(0x40F9)==1 and g.flag('FLAG_POX_STORY_MTMOON')
        # Approach each original fossil object, exercising Yes and its movement.
        g.warp('MtMoon_B2F_Frlg',x,8)
        g.tap(K.KEY_UP,hold=2,wait=12)
        g.tap(K.KEY_A,hold=2,wait=12)
        dismiss(g)
        assert g.var(0x40F9)==2,(fossil,g.var(0x40F9))
        assert g.flag('FLAG_POX_MOON_HIDE_DOME_FOSSIL')
        assert item_count(g,885 if fossil=='Dome' else 886)==1
        from test_gen2_trees import quantity
        assert quantity(g,885 if fossil=='Dome' else 886,index=4)==1
        assert item_count(g,886 if fossil=='Dome' else 885)==0
        g.shot('moon_fossil_'+fossil+'.png')
        g.warp('MtMoon_B1F_Frlg',40,4)
        g.warp('MtMoon_B2F_Frlg',14,10)
        assert g.var(0x40F9)==2 and g.flag('FLAG_POX_MOON_HIDE_DOME_FOSSIL')
        from test_region_walk import navigate
        navigate(g,lambda a,b:(a,b)==(5,11))
        g.tap(K.KEY_UP,hold=24,wait=180)
        assert_map(g,'MtMoon_B1F_Frlg')
        g.shot('moon_fossil_revisit_'+fossil+'.png')
        print(fossil,'battle, choice, persistence and exit PASS',flush=True)
    g=StoryGame();g.run('Pox_Squirtle')
    g.warp('MtMoon_B2F_Frlg',12,23)
    g.tap(K.KEY_UP,hold=16,wait=30)
    wait_battle(g,'TRAINER_PLASTIC_OX_MOON_TEAM_ROCKET_GRUNT')
    finish_battle(g)
    assert not g.flag('FLAG_POX_STORY_MTMOON')
    print('Rocket battle and independent completion PASS',flush=True)


def continuous_test():
    from test_region_walk import navigate, cross
    g=setup();g.setvar(0x40F9,2);g.flag('FLAG_POX_STORY_MTMOON',True)
    g.warp('Route44_hns',67,13)
    g.tap(K.KEY_RIGHT,hold=24,wait=180)
    # Include the isolated branch, the second branch, then the main progression.
    for name,index in [('MtMoon_1F_Frlg',2),('MtMoon_B1F_Frlg',5),
                       ('MtMoon_B2F_Frlg',2),('MtMoon_B1F_Frlg',2),
                       ('MtMoon_1F_Frlg',1),('MtMoon_B1F_Frlg',4),
                       ('MtMoon_B2F_Frlg',1),('MtMoon_B1F_Frlg',1),
                       ('MtMoon_1F_Frlg',0),('MtMoon_B1F_Frlg',3),
                       ('MtMoon_B2F_Frlg',3),('MtMoon_B1F_Frlg',7)]:
        assert_map(g,name);w=MAPS[name]['warp_events'][index]
        navigate(g,lambda x,y:abs(x-w['x'])+abs(y-w['y'])==1)
        s=g.state()
        direction=next(k for k,dx,dy in [('N',0,-1),('S',0,1),('E',1,0),('W',-1,0)] if (s['x']+dx,s['y']+dy)==(w['x'],w['y']))
        cross(g,direction,BYID[w['dest_map']])
        print('continuous PASS',name,index,flush=True)
    assert_map(g,'Route33_hns')
    navigate(g,lambda x,y:(x,y)==(1,22))
    cross(g,'W','GoldenrodCity_hns')
    g.shot('moon_arrive_goldenrod.png')
    print('continuous full dungeon, side branches, Route 33 to Goldenrod PASS',flush=True)


def item_count(g, item):
    from test_gen2_trees import quantity
    return sum(quantity(g,item,index=i) for i in range(5))


def full_bag_test():
    g=setup()
    g.warp('MtMoon_B2F_Frlg',13,8)
    # No fossil can be awarded before Miguel is defeated.
    g.setvar(0x40F9,0)
    g.tap(K.KEY_UP,hold=2,wait=12);g.tap(K.KEY_A,hold=2,wait=12)
    dismiss(g)
    assert not g.flag('FLAG_POX_MOON_HIDE_DOME_FOSSIL')
    assert item_count(g,885)==0
    g.setvar(0x40F9,1)
    # Fill both candidate pockets; restore their exact RAM contents after failure.
    saved=[]
    for i in [0,4]:
        addr=g.syms['gBagPockets']+i*(g.sizes['gBagPockets']//5)
        ptr,count=g.u32(addr),g.u8(addr+4)
        key=next(g.u16(ptr+4*j+2) for j in range(count) if g.u16(ptr+4*j)==0)
        for j in range(count):
            p=ptr+4*j;saved.append((p,g.u32(p)))
            g.write(p,1,2);g.write(p+2,999^key,2)
    g.tap(K.KEY_A,hold=2,wait=12);dismiss(g)
    assert g.var(0x40F9)==1 and not g.flag('FLAG_POX_MOON_HIDE_DOME_FOSSIL')
    for p,value in saved:g.write(p,value,4)
    g.tap(K.KEY_A,hold=2,wait=12);dismiss(g)
    assert g.var(0x40F9)==2 and item_count(g,885)==1
    # A repeated direct script cannot award the fossil again.
    g.run('MtMoon_B2F_EventScript_DomeFossil')
    assert item_count(g,885)==1
    print('fossil prerequisite, full bag, retry, no duplicate reward PASS',flush=True)



def legacy_save_test():
    import struct
    from test_qol import opcode, begin_code
    g=StoryGame()
    group,num=IDS['MtMoon_Cave_hns']
    begin_code(g,opcode(g,'warp')+bytes([group,num,255])+struct.pack('<HH',10,11)+opcode(g,'waitstate')+opcode(g,'end'))
    g.frame(600)
    assert_map(g,'MtMoon_1F_Frlg')
    assert g.u8(g.syms['sGlobalScriptContextStatus'])==2
    print('retired cave save relocation PASS',flush=True)


if __name__=='__main__':
    source_test()
    if '--story-only' not in sys.argv:warp_tests()
    fossil_tests()
    full_bag_test()
    continuous_test()
    legacy_save_test()

