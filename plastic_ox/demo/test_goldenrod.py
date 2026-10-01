#!/usr/bin/env python3
"""Goldenrod import: directed warps, live services and selected-slot friendship."""
import json
import hashlib
import sys
from pathlib import Path
from test_story import StoryGame, ROOT
from walklib import K, DIRKEY
sys.path.insert(0,str(ROOT/'plastic_ox/alpha'))
from region_geometry import Geometry
from goldenrod import BASE, install

MANIFEST=json.loads((BASE/'source_manifest.json').read_text())
NAMES=['GoldenrodCity_hns','GoldenrodCity_BillsHouse_hns',*MANIFEST['maps']]
MAPS={n:json.loads((ROOT/f'data/maps/{n}/map.json').read_text()) for n in NAMES}
BYID={d['id']:n for n,d in MAPS.items()}
GROUPS=json.loads((ROOT/'data/maps/map_groups.json').read_text())
IDS={n:(i,j) for i,k in enumerate(GROUPS['group_order']) for j,n in enumerate(GROUPS[k])}


def same_map(g,n):return (g.state()['group'],g.state()['num'])==IDS[n]


def sources():
    changes={}
    def put(p,s):
        if (ROOT/p).read_text()!=s:changes[p]=s
    install(lambda p:(ROOT/p).read_text(),put)
    assert not changes,list(changes)
    for name in NAMES:
        data=MAPS[name]
        if name in MANIFEST['maps']:
            converted=MANIFEST['maps'][name]
            for key,digest in converted['converted_layout_sha256'].items():
                assert hashlib.sha256((ROOT/converted['layout'][key]).read_bytes()).hexdigest()==digest,(name,key)
            assert not data['coord_events']
            assert all('WANDER' not in o['movement_type'] for o in data['object_events'])
        for i,w in enumerate(data['warp_events']):
            if w['dest_map']=='MAP_DYNAMIC':continue
            dest=MAPS[BYID[w['dest_map']]]
            landing=dest['warp_events'][int(w['dest_warp_id'])]
            if '7FNight' not in name:
                assert landing['dest_map'] in [data['id'],'MAP_DYNAMIC'],(name,i,landing)
    city=Geometry('GoldenrodCity_hns')
    blocked={(o['x'],o['y']) for o in city.data['object_events']}
    reachable=city.component((28,37),blocked=blocked)
    assert all((w['x'],w['y']+1) in reachable for w in city.data['warp_events'])
    # New item allocations must stay in persistent unused system slots, outside
    # both trainer flags and the RTC daily-reset range.
    flags=json.loads((BASE/'flags.json').read_text())
    flag_header=(ROOT/'include/constants/flags.h').read_text()
    assert set(flags.values())==set(range(0x900,0x90E))
    for value in flags.values():assert f'FLAG_UNUSED_0x{value:03X}' in flag_header
    print('source geometry, topology, NPC access, item flags, regeneration PASS',flush=True)


def warps():
    g=StoryGame()
    failures=[]
    count=0
    for name in NAMES:
        geom=Geometry(name)
        for index,w in enumerate(MAPS[name]['warp_events']):
            if w['dest_map']=='MAP_DYNAMIC':continue
            dest=BYID[w['dest_map']];landing=MAPS[dest]['warp_events'][int(w['dest_warp_id'])]
            attempts=[]
            for direction,dx,dy in [('UP',0,-1),('DOWN',0,1),('LEFT',-1,0),('RIGHT',1,0)]:
                x,y=w['x']-dx,w['y']-dy
                if not geom.passable(x,y):continue
                g.warp(name,x,y)
                g.tap(DIRKEY[direction],hold=24,wait=180)
                behavior=geom.tile(w['x'],w['y'])[2]
                if same_map(g,name) and behavior.endswith('_ARROW_WARP'):
                    exit_direction=behavior.removeprefix('MB_').removesuffix('_ARROW_WARP')
                    exit_direction={'EAST':'RIGHT','WEST':'LEFT','NORTH':'UP','SOUTH':'DOWN'}[exit_direction]
                    g.tap(DIRKEY[exit_direction],hold=24,wait=180)
                if not same_map(g,dest):attempts.append((direction,g.state()));continue
                g.frame(120)
                s=g.state()
                assert same_map(g,dest),(name,index,s)
                assert abs(s['x']-landing['x'])+abs(s['y']-landing['y'])<=1,(name,index,s)
                
                if g.collision_at(s['x'],s['y'])[0]!=0:
                    failures.append((name,index,'solid landing',s))
                g.shot(f'goldenrod_{name}_{index}.png')
                print('warp PASS',name,index,dest,(s['x'],s['y']),flush=True)
                count+=1
                break
            else:failures.append((name,index,attempts))
    assert not failures,failures
    print(f'{count} directed physical warps PASS',flush=True)




def task(g,name):
    return any(g.u8(g.syms['gTasks']+i*40+4) and
        g.u32(g.syms['gTasks']+i*40)&~1==g.syms[name]&~1 for i in range(16))


def friendship(g,slot,value=None):
    from test_trainer_recovery import secure
    mon=g.syms['gParties']+slot*(g.sizes['gParties']//24)
    def edit(data,offsets):data[offsets[0]+9]=value
    data,offsets=secure(g,mon,edit if value is not None else None)
    return data[offsets[0]+9]


def money(g,value=None):
    key=g.u32(g.u32(g.syms['gSaveBlock2Ptr'])+0xAC)
    addr=g.u32(g.syms['gSaveBlock1Ptr'])+0x490
    if value is not None:g.write(addr,value^key,4)
    return g.u32(addr)^key


def haircuts():
    import struct
    from test_training_kit import run_code, native
    from test_qol import opcode
    g=StoryGame()
    for species in [19,25,133]:
        run_code(g,opcode(g,'callnative')+struct.pack('<I',g.syms['ScrCmd_createmon']|1)+struct.pack('<BBHHI',0,6,species,5,0))
    for label,y,price in [('Older',20,500),('Younger',16,300)]:
        for cancel,poor in [(False,False),(True,False),(False,True)]:
            for i,v in enumerate([20,40,60]):friendship(g,i,v)
            money(g,0 if poor else 2000)
            g.warp('GoldenrodCity_UndergroundTunnel_hns',4,y)
            g.tap(K.KEY_RIGHT,hold=2,wait=10)
            # Use the actual NPC, including interaction across the counter.
            for _ in range(450):
                if task(g,'Task_HandleChooseMonInput'):break
                g.tap(K.KEY_A,hold=2,wait=10)
            else:raise AssertionError((label,'party menu never opened',g.state()))
            g.frame(30)
            if cancel:g.tap(K.KEY_B,hold=2,wait=30)
            else:
                g.tap(K.KEY_DOWN,hold=2,wait=20)
                assert g.u8(g.syms['gPartyMenu']+9)==1,'second party slot not selected'
                g.tap(K.KEY_A,hold=2,wait=40)
            for _ in range(500):
                g.tap(K.KEY_A,hold=2,wait=10)
                if g.u8(g.syms['sGlobalScriptContextStatus'])==2:break
            else:raise AssertionError((label,'haircut did not release controls'))
            result=[friendship(g,i) for i in range(3)]
            assert result==([20,40,60] if cancel or poor else [20,255,60]),(label,cancel,poor,result)
            assert money(g)==(0 if poor else 2000 if cancel else 2000-price),(label,cancel,poor,money(g))
            g.shot(f'goldenrod_haircut_{label}_{cancel}_{poor}.png')
            print('haircut PASS',label,'cancel',cancel,'poor',poor,result,flush=True)
    # Guard invalid indices and eggs, independent of the menu's validation.
    for slot in [3,6,65535]:
        g.write(g.syms['gSpecialVar_0x8004'],slot,2)
        before=bytes(g.u8(g.syms['gParties']+i) for i in range(g.sizes['gParties']))
        native(g,'PoxMaximizeSelectedMonFriendship')
        assert before==bytes(g.u8(g.syms['gParties']+i) for i in range(g.sizes['gParties']))
    print('invalid party selection guard PASS',flush=True)
    friendship(g,1,255)
    g.write(g.syms['gSpecialVar_0x8004'],1,2)
    native(g,'PoxMaximizeSelectedMonFriendship')
    assert [friendship(g,i) for i in range(3)]==[20,255,60]
    run_code(g,opcode(g,'giveegg')+struct.pack('<H',133))
    assert g.count()==4
    before=friendship(g,3)
    g.write(g.syms['gSpecialVar_0x8004'],3,2)
    native(g,'PoxMaximizeSelectedMonFriendship')
    assert friendship(g,3)==before
    money(g,2000)
    g.warp('GoldenrodCity_UndergroundTunnel_hns',4,16)
    g.tap(K.KEY_RIGHT,hold=2,wait=10)
    for _ in range(450):
        if task(g,'Task_HandleChooseMonInput'):break
        g.tap(K.KEY_A,hold=2,wait=10)
    else:raise AssertionError('egg test party menu did not open')
    g.frame(30)
    for _ in range(3):g.tap(K.KEY_DOWN,hold=2,wait=20)
    assert g.u8(g.syms['gPartyMenu']+9)==3
    g.tap(K.KEY_A,hold=2,wait=40)
    for _ in range(500):
        g.tap(K.KEY_A,hold=2,wait=10)
        if g.u8(g.syms['sGlobalScriptContextStatus'])==2:break
    else:raise AssertionError('egg refusal did not release controls')
    assert money(g)==2000 and friendship(g,3)==before
    assert [friendship(g,i) for i in range(3)]==[20,255,60]
    print('egg refusal, egg native guard, already-maximum friendship PASS',flush=True)




def elevator():
    from walk_leg1 import navigate
    g=StoryGame()
    lift='GoldenrodCity_DepartmentStoreElevator_hns'
    for floor in range(1,7):
        name=f'GoldenrodCity_DepartmentStore_{floor}F_hns'
        g.warp(name,9,5)
        g.tap(K.KEY_UP,hold=24,wait=180)
        assert same_map(g,lift),(floor,g.state())
        g.tap(K.KEY_DOWN,hold=24,wait=180)
        assert same_map(g,name),(floor,'cancel return',g.state())
        assert (g.state()['x'],g.state()['y'])==(9,5)
    for choice in range(8):
        g.warp('GoldenrodCity_DepartmentStore_1F_hns',9,5)
        g.tap(K.KEY_UP,hold=24,wait=180)
        navigate(g,(0,3))
        g.tap(K.KEY_UP,hold=2,wait=10)
        for _ in range(200):
            if task(g,'Task_HandleMultichoiceInput'):break
            g.tap(K.KEY_A,hold=2,wait=10)
        else:raise AssertionError('elevator menu never opened')
        g.frame(30)
        for _ in range(choice):g.tap(K.KEY_DOWN,hold=2,wait=10)
        g.tap(K.KEY_A,hold=2,wait=180)
        target='GoldenrodCity_DepartmentStore'+('Basement_hns' if choice==0 else f'_{choice}F_hns')
        assert same_map(g,target),(choice,g.state())
        assert g.collision_at(g.state()['x'],g.state()['y'])[0]==0
        g.shot(f'goldenrod_elevator_{choice}.png')
        print('elevator selection PASS',choice,target,flush=True)
    print('elevator returns to every originating floor PASS',flush=True)


def continuous():
    from walk_leg1 import navigate, enter_warp
    g=StoryGame(spawn=('GoldenrodCity_hns',28,37))
    def cross(name,index,approach,direction,dest):
        assert same_map(g,name),g.state()
        # Avoid other warp tiles while planning an ordinary walking path.
        avoid={(w['x'],w['y']) for i,w in enumerate(MAPS[name]['warp_events']) if i!=index}
        navigate(g,approach,avoid=avoid)
        enter_warp(g,approach,direction,IDS[dest],f'{name}:{index}')
        assert same_map(g,dest),g.state()
    # Full south entrance -> both brothers -> north exit, then back again.
    cross('GoldenrodCity_hns',2,(21,39),'UP','GoldenrodCity_UndergroundEntrance_hns')
    cross('GoldenrodCity_UndergroundEntrance_hns',1,(4,3),'RIGHT','GoldenrodCity_UndergroundTunnel_hns')
    navigate(g,(4,20));g.shot('goldenrod_walk_older.png')
    navigate(g,(4,16));g.shot('goldenrod_walk_younger.png')
    cross('GoldenrodCity_UndergroundTunnel_hns',1,(2,3),'RIGHT','GoldenrodCity_UndergroundEntrance_hns')
    cross('GoldenrodCity_UndergroundEntrance_hns',2,(22,7),'DOWN','GoldenrodCity_hns')
    cross('GoldenrodCity_hns',3,(20,13),'UP','GoldenrodCity_UndergroundEntrance_hns')
    cross('GoldenrodCity_UndergroundEntrance_hns',0,(23,3),'LEFT','GoldenrodCity_UndergroundTunnel_hns')
    cross('GoldenrodCity_UndergroundTunnel_hns',0,(3,33),'LEFT','GoldenrodCity_UndergroundEntrance_hns')
    cross('GoldenrodCity_UndergroundEntrance_hns',3,(5,7),'DOWN','GoldenrodCity_hns')
    print('continuous Underground walk, both entrances and both brothers PASS',flush=True)




def city_tour():
    from walk_leg1 import navigate, enter_warp
    g=StoryGame(spawn=('GoldenrodCity_hns',28,37))
    for index,w in enumerate(MAPS['GoldenrodCity_hns']['warp_events']):
        dest=BYID[w['dest_map']]
        approach=(w['x'],w['y']+1)
        avoid={(v['x'],v['y']) for v in MAPS['GoldenrodCity_hns']['warp_events']}
        navigate(g,approach,avoid=avoid)
        enter_warp(g,approach,'UP',IDS[dest],f'city tour {index}')
        g.tap(K.KEY_DOWN,hold=24,wait=180)
        assert same_map(g,'GoldenrodCity_hns'),(index,g.state())
        assert (g.state()['x'],g.state()['y'])==approach
        print('city door round trip PASS',dest,flush=True)
    print('All 14 city doors continuously reachable with NPCs PASS',flush=True)


if __name__=='__main__':
    sources()
    for name,check in [('warps',warps),('haircuts',haircuts),('elevator',elevator),('walk',continuous),('city',city_tour)]:
        if len(sys.argv)==1 or name in sys.argv:check()
