#!/usr/bin/env python3
"""Additional League acceptance cases; outcomes use normal finish callbacks."""
import json
import struct
from test_league import (prepare, start_battle, finish_battle, settle, current,
                         trainer_flag, save_continue, shot, MEMBERS, FLAGS, BADGES,
                         ROOT, K, Geometry, navigate)
from test_sudowoodo_v1 import pocket, bag, POCKET_ITEMS


def ordering():
    maps=[(p.parent.name,json.loads(p.read_text())) for p in (ROOT/'data/maps').glob('*/map.json')]
    for order in [('Clair','Bruno'),('Bruno','Clair')]:
        g=prepare(('EcruteakCity_hns',9,35))
        for f in BADGES[-2:]:g.flag(f,False)
        g.flag('FLAG_POX_TRIGGERS_ENABLED',True)
        g.flag('FLAG_POX_STORY_SPACE_CENTER',True)
        g.flag('FLAG_POX_STORY_SILPH',False)
        for i,name in enumerate(order):
            mapname,d=next((n,d) for n,d in maps if any(o.get('script')=='Pox_'+name for o in d.get('object_events',[])))
            o=next(o for o in d['object_events'] if o['script']=='Pox_'+name)
            g.warp(mapname,o['x'],o['y']+1)
            start_battle(g,name,(o['x'],o['y']))
            finish_battle(g,1);settle(g)
            assert g.flag('FLAG_BADGE08_GET' if name=='Clair' else 'FLAG_BADGE07_GET')
            g.write(g.syms['gBattleTypeFlags'],0,4)
            g.warp('EcruteakCity_hns',9,35)
            g.tap(K.KEY_LEFT,hold=16,wait=240);settle(g)
            assert current(g)==('EcruteakCity_hns' if i==0 else 'PlasticOx_VictoryRoad')
        print('PASS: actual '+str(order)+' battles/callbacks, gate denies seventh badge and accepts eighth without Silph',flush=True)


def bag_use():
    g=prepare(('PlasticOx_StevenRoom',6,11));g.flag(FLAGS[0],True)
    mon=g.syms['gParties'];stride=g.sizes['gParties']//24
    g.write(mon+stride-14,1,2)
    slots,count=pocket(g,POCKET_ITEMS)
    xor=next(g.u16(slots+4*j+2) for j in range(count) if g.u16(slots+4*j)==0)
    g.write(slots,28,2);g.write(slots+2,1^xor,2)
    # Open the actual Start menu and choose Bag using its populated action list.
    g.tap(K.KEY_START,wait=60)
    actions=g.syms['sCurrentStartMenuActions'];num=g.u8(g.syms['sNumStartMenuActions'])
    index=next(i for i in range(num) if g.u8(actions+i)==2)
    for _ in range(index):g.tap(K.KEY_DOWN,wait=12)
    g.tap(K.KEY_A,wait=90)
    pos=g.syms['gBagPosition']
    # The fixture has no earlier bag visit: Items, cursor zero is the default.
    assert g.u8(pos+5)==0
    g.tap(K.KEY_A,wait=30);g.tap(K.KEY_A,wait=90);g.tap(K.KEY_A,wait=90)
    for _ in range(10):g.tap(K.KEY_A,wait=12)
    assert g.u16(mon+stride-14)>1,('potion did not heal',g.u16(mon+stride-14))
    assert bag(g,28,POCKET_ITEMS)==0
    shot(g,'between_battles_potion')
    for _ in range(20):g.tap(K.KEY_B,wait=20)
    assert current(g)=='PlasticOx_StevenRoom' and g.flag(FLAGS[0])
    print('PASS: Start → Bag → Potion → party use between League fights consumes one item and heals',flush=True)


def ledges():
    r=Geometry('PlasticOx_VictoryRoad')
    for x,y in [(18,16),(8,36),(24,37)]:
        g=prepare(('PlasticOx_VictoryRoad',x,y-1))
        b=r.tile(x,y)[2];mt=r.blocks[y*r.w+x]&1023
        assert b=='MB_JUMP_SOUTH'
        shot(g,f'ledge_{x}_{y}_approach')
        g.tap(K.KEY_DOWN,hold=8,wait=90)
        assert (g.state()['x'],g.state()['y'])==(x,y+1),g.describe()
        shot(g,f'ledge_{x}_{y}_landing')
        g.tap(K.KEY_UP,hold=16,wait=60)
        assert (g.state()['x'],g.state()['y'])==(x,y+1),g.describe()
        print(f'PASS: ledge ({x},{y}) metatile {mt:#x} {b}, two-tile landing and blocked reverse',flush=True)


def sight():
    route=json.loads((ROOT/'data/maps/PlasticOx_VictoryRoad/map.json').read_text())
    for o in route['object_events']:
        if o['trainer_type']!='TRAINER_TYPE_NORMAL':continue
        tid=o['script'].removeprefix('PoxLeague_');dx=-1 if o['movement_type'].endswith('LEFT') else 1
        g=prepare(('PlasticOx_VictoryRoad',o['x']+dx,o['y']+1))
        g.tap(K.KEY_UP,hold=16,wait=60)
        if int(o['trainer_sight_or_berry_tree_id'])==0:
            g.frame(180);assert not g.u32(g.syms['gBattleTypeFlags'])&8
            print('PASS: '+tid+' remains interaction-only on adjacent sight line',flush=True)
        else:
            for _ in range(400):
                g.tap(K.KEY_A,hold=2,wait=10)
                if g.u32(g.syms['gBattleTypeFlags'])&8:break
            else:raise AssertionError(('sight line did not start fight',tid,g.describe()))
            assert g.u16(g.syms['gTrainerBattleParameter']+2)==g.const('TRAINER_PLASTIC_OX_'+tid)
            print('PASS: '+tid+' sees player walking into authored sight line',flush=True)


def entry_and_doors():
    g=prepare(('IndigoPlateau_PokemonCenter_hns',32,4))
    for f in BADGES:
        g.flag(f,False)
        g.tap(K.KEY_UP,hold=2,wait=12);g.tap(K.KEY_A,wait=20);settle(g)
        assert current(g)=='IndigoPlateau_PokemonCenter_hns',(f,'official bypass')
        g.flag(f,True)
    for i,n in enumerate(MEMBERS):
        g=prepare(('PlasticOx_'+n+'Room',6,11))
        for f in FLAGS[:i]:g.flag(f,True)
        g.tap(K.KEY_DOWN,hold=64,wait=90)
        assert current(g)=='PlasticOx_'+n+'Room',(n,'backtracking warp')
        if i<4:assert g.collision_at(6,2)[0]!=0,(n,'premature forward door')
        if i:
            g.flag(FLAGS[i-1],False)
            navigate(g,lambda x,y:(x,y)==(6,6))
            g.tap(K.KEY_UP,hold=2,wait=12);g.tap(K.KEY_A,wait=20);settle(g)
            assert not g.u32(g.syms['gBattleTypeFlags'])&8,(n,'skipped earlier member')
            g.flag(FLAGS[i-1],True)
        if n=='Bill':
            save_continue(g)
            assert all(g.flag(f) for f in FLAGS[:i]) and not g.flag(FLAGS[i])
    print('PASS: lobby denies all eight missing badges; five rear exits blocked; four closed forward doors; four sequence bypasses denied; Bill pre-battle save survives',flush=True)


def ordinary_game_clear():
    from test_qol import begin_code,opcode
    from test_region_walk import IDS
    for gender,dest in [(0,'LittlerootTown_BrendansHouse_2F'),(1,'LittlerootTown_MaysHouse_2F')]:
        g=prepare(('EcruteakCity_hns',9,35))
        g.write(g.u32(g.syms['gSaveBlock2Ptr'])+8,gender)
        begin_code(g,opcode(g,'callnative')+struct.pack('<I',g.syms['GameClear']|1)+opcode(g,'end'))
        g.frame(30)
        ptr=g.u32(g.syms['gSaveBlock1Ptr'])
        assert (g.u8(ptr+12),g.u8(ptr+13))==IDS[dest]
        assert g.flag('FLAG_SYS_GAME_CLEAR')
    print('PASS: ordinary Emerald GameClear retains both gender-specific Littleroot Continue destinations',flush=True)


if __name__=='__main__':
    ordering();bag_use();ledges();sight();entry_and_doors();ordinary_game_clear()
