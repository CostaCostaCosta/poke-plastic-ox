#!/usr/bin/env python3
"""Endgame regressions on the ordinary ROM, using in-memory mGBA saves.

Travel and NPC interaction use D-pad/A inputs. Battle outcomes are injected
through the engine's normal finish handler; these checks prove transitions,
not that a human can beat the competitive teams. --battles also checks actual
party creation, damage persistence, loss/reset, HoF, credits and flash Continue.
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path
from test_story import StoryGame, ROOT
from test_training_kit import run_code
from test_qol import opcode, begin_code
from test_trainer_recovery import secure, item
from walklib import K
from test_region_walk import navigate, current, IDS
sys.path.insert(0,str(ROOT/'plastic_ox/alpha'))
from region_geometry import Geometry
from league import MEMBERS, FLAGS, BADGES

OUT=ROOT/'plastic_ox/demo/shots/league'

class Game(StoryGame):
    def flag(self,name,value=None):
        flag=self.const(name)
        if 0xB00<=flag<0xB80:
            addr=self.u32(self.syms['gSaveBlock3Ptr'])+self.sizes['gSaveblock3']-16+(flag-0xB00)//8
            if value is not None:self.write(addr,(self.u8(addr)&~(1<<(flag%8)))|(bool(value)<<(flag%8)))
            return bool(self.u8(addr)&(1<<(flag%8)))
        return super().flag(name,value)


def shot(g,name):
    OUT.mkdir(parents=True,exist_ok=True)
    g.fb.to_pil().convert('RGB').save(OUT/(name+'.png'))


def settle(g,limit=3600):
    for _ in range(limit//12):
        g.tap(K.KEY_A,hold=2,wait=10)
        if g.u8(g.syms['sGlobalScriptContextStatus'])==2:
            g.frame(120)
            if g.u8(g.syms['sGlobalScriptContextStatus'])==2 and not g.u8(g.syms['sLockFieldControls']) and g.u32(g.syms['gMain']+4)&~1 == g.syms['CB2_Overworld']&~1:
                return
    shot(g,'failure')
    raise AssertionError(('field script did not finish',g.describe()))


def prepare(spawn):
    g=Game();g.test_water=False
    for f in BADGES:g.flag(f,True)
    g.flag('FLAG_POX_STORY_STARTER',True)
    g.flag('FLAG_ADVENTURE_STARTED',True)
    # A single fixture partner; no HM moves are needed for any route walk.
    run_code(g, opcode(g,'callnative')+struct.pack('<I',g.syms['ScrCmd_createmon']|1)+struct.pack('<BBHHI',0,6,376,64,0))
    run_code(g,opcode(g,'setflag')+struct.pack('<H',0xB7F)+opcode(g,'clearflag')+struct.pack('<H',0xB7F))
    g.warp(*spawn)
    return g


def trainer_flag(g,tid,value=None):
    n=g.const('TRAINER_PLASTIC_OX_'+tid)
    f=0xB40+n-938 if n>=938 else 0x4A0+n-857
    return g.flag(f,value)


def static():
    g=Geometry('PlasticOx_VictoryRoad');c=g.component((27,48))
    assert g.layout['layout_version']=='hns' and (14,2) in c
    assert (27,48) in g.component((14,2)), 'return requires a one-way ledge'
    assert g.data['map_type']=='MAP_TYPE_ROUTE' and not g.data['requires_flash']
    for o in g.data['object_events']:
        assert (o['x'],o['y']) in c,o
    assert len([o for o in g.data['object_events'] if o['trainer_type']=='TRAINER_TYPE_NORMAL'])==6
    assert sum(g.tile(x,y)[2]=='MB_TALL_GRASS' for x,y in c)>50
    sys.path.insert(0,str(ROOT/'plastic_ox/agent'))
    from test_trainer_teams_v2 import parse,parse_mon
    from apply_trainer_teams_v2 import ROSTERS
    import pox_progression as P
    blocks=parse((ROOT/'plastic_ox/alpha/league/trainers.party').read_text())
    for tid,b in blocks.items():
        mons=[parse_mon(chunk) for chunk in b.strip().split('\n\n')[1:]]
        assert len(mons)==6,(tid,len(mons))
        if tid in ROSTERS:
            assert [(m['species'],m['level']) for m in mons]==ROSTERS[tid][1],tid
        for m in mons:
            assert len(m['moves'])==4 and len(set(m['moves']))==4
            assert set(m['moves'])<=P.load_gen3_moves(),m
            assert sum(m['evs'].values())<=510 and max(m['evs'].values())<=252
            assert len(m['ivs'])==6 and min(m['ivs'].values())>=30
            assert m['item'] and m['nature'] and m['ability']
    print('PASS: dry bidirectional route, six reachable trainers, canonical rosters/levels, Gen III moves/EVs/IVs',flush=True)


def travel():
    g=prepare(('EcruteakCity_hns',9,35))
    for missing in BADGES:
        g.flag(missing,False)
        g.tap(K.KEY_LEFT,hold=16,wait=30);settle(g)
        assert current(g)=='EcruteakCity_hns' and g.state()['x']==9,(missing,g.describe())
        g.flag(missing,True)
    print('PASS: all eight badges independently required at actual western gate',flush=True)
    # Prove every traversable lane, then take the complete northbound path.
    for y in range(34,38):
        g.warp('EcruteakCity_hns',9,y);g.tap(K.KEY_LEFT,hold=16,wait=240)
        assert current(g)=='PlasticOx_VictoryRoad',(y,g.describe())
    for tid in ['VICTORYROAD','RIDGE_RAIN','RIDGE_SAND','RIDGE_STALL','RIDGE_OFFENSE','RIDGE_BALANCE']:
        trainer_flag(g,tid,True)
    shot(g,'route_entrance')
    for x,y,name in [(26,42,'lower_ridge'),(10,34,'western_reward'),(15,29,'terrace'),(20,12,'upper_reward'),(25,22,'upper_ridge'),(14,2,'summit')]:
        navigate(g,lambda a,b:(a,b)==(x,y));shot(g,name)
        if name in ['western_reward','terrace','upper_reward']:
            i=['western_reward','terrace','upper_reward'].index(name)
            g.tap(K.KEY_LEFT if i==0 else K.KEY_UP,hold=2,wait=12)
            g.tap(K.KEY_A,wait=20);settle(g)
            assert g.flag(f'FLAG_POX_LEAGUE_REWARD_{i}'),('pickup',i)
    g.tap(K.KEY_UP,hold=16,wait=240);assert current(g)=='IndigoPlateau_hns',g.describe()
    shot(g,'plateau')
    navigate(g,lambda x,y:(x,y)==(11,7));g.tap(K.KEY_UP,hold=16,wait=240)
    assert current(g)=='IndigoPlateau_PokemonCenter_hns',g.describe();shot(g,'lobby')
    # Real nurse, shop and PC interactions.
    mon=g.syms['gParties'];stride=g.sizes['gParties']//24
    g.write(mon+stride-14,1,2)
    navigate(g,lambda x,y:(x,y)==(19,12));g.tap(K.KEY_UP,hold=2,wait=12);g.tap(K.KEY_A,wait=20);settle(g)
    mon=g.syms['gParties'];stride=g.sizes['gParties']//24
    assert g.u16(mon+stride-14)==g.u16(mon+stride-12)
    navigate(g,lambda x,y:(x,y)==(24,10));g.tap(K.KEY_UP,hold=2,wait=12);g.tap(K.KEY_A,wait=90)
    shot(g,'pc');assert g.u8(g.syms['sGlobalScriptContextStatus'])!=2
    for _ in range(20):g.tap(K.KEY_B,wait=20)
    assert g.u8(g.syms['sGlobalScriptContextStatus'])==2
    navigate(g,lambda x,y:(x,y)==(10,12));g.tap(K.KEY_UP,hold=2,wait=12);g.tap(K.KEY_A,wait=30)
    for _ in range(8):g.tap(K.KEY_A,wait=20)
    shot(g,'shop')
    for _ in range(12):g.tap(K.KEY_A,wait=20)
    for _ in range(30):g.tap(K.KEY_B,wait=20)
    if g.u8(g.syms['sGlobalScriptContextStatus'])!=2:settle(g)
    # Exit is a fixed warp; it must not reuse the regional dynamic return.
    navigate(g,lambda x,y:(x,y)==(19,15));g.tap(K.KEY_DOWN,hold=32,wait=240)
    assert current(g)=='IndigoPlateau_hns',g.describe()
    navigate(g,lambda x,y:(x,y)==(12,18));g.tap(K.KEY_DOWN,hold=16,wait=240)
    assert current(g)=='PlasticOx_VictoryRoad'
    navigate(g,lambda x,y:(x,y)==(27,48));g.tap(K.KEY_DOWN,hold=16,wait=240)
    assert current(g)=='EcruteakCity_hns'
    print('PASS: full Ecruteak–ridge–Indigo round trip on foot, nurse, PC, shop, fixed lobby exit',flush=True)


def start_battle(g,n,xy=(6,5)):
    # Interact with the visible opponent at their actual authored coordinate.
    navigate(g,lambda x,y:(x,y)==(xy[0],xy[1]+1));g.tap(K.KEY_UP,hold=2,wait=12)
    for _ in range(400):
        g.tap(K.KEY_A,hold=2,wait=10)
        if g.u32(g.syms['gBattleTypeFlags'])&8:break
    else:raise AssertionError('no battle '+n)
    g.frame(240)
    assert g.u8(g.syms['gPartiesCount']+1)==6,(n,'enemy count')
    tid='TRAINER_PLASTIC_OX_'+n.upper()
    assert g.u16(g.syms['gTrainerBattleParameter']+2)==g.const(tid),(n,'wrong trainer')
    sys.path.insert(0,str(ROOT/'plastic_ox/agent'))
    from test_trainer_teams_v2 import parse,parse_mon
    from test_sudowoodo_v1 import const
    blocks=parse((ROOT/'plastic_ox/alpha/league/trainers.party').read_text())
    if tid in blocks:
        mons=[parse_mon(chunk) for chunk in blocks[tid].strip().split('\n\n')[1:]]
        stride=g.sizes['gParties']//24
        for i,m in enumerate(mons):
            enemy=g.syms['gParties']+(6+i)*stride
            assert g.box_species(enemy)==const(m['species'],'species.h'),(n,i,'species')
            highest=max(g.u8(g.syms['gParties']+j*stride+stride-16) for j in range(g.u8(g.syms['gPartiesCount'])))
            assert g.u8(enemy+stride-16)==max(m['level'],highest),(n,i,'scaled level')
            assert g.box_ivs(enemy)==[m['ivs'][k] for k in ['hp','atk','def','spe','spa','spd']],(n,i,'IVs')
            data,offsets=secure(g,enemy)
            moves=struct.unpack_from('<4H',data,offsets[1])
            assert list(moves)==[const(move,'moves.h') for move in m['moves']],(n,i,'moves')
    shot(g,'battle_'+n)


def finish_battle(g,outcome, status=0):
    mon=g.syms['gParties'];stride=g.sizes['gParties']//24
    g.write(mon+stride-14,1 if outcome==1 else 0,2)
    g.write(mon+stride-20,status,4)
    g.write(g.syms['gBattleOutcome'],outcome)
    g.write(g.syms['gCurrentActionFuncId'],11)
    g.write(g.syms['gBattleMainFunc'],g.syms['HandleEndTurn_FinishBattle']|1,4)
    g.frame(240)


def battles():
    g=prepare(('IndigoPlateau_PokemonCenter_hns',19,14))
    g.run('PoxLeague_Entry');assert current(g)=='PlasticOx_WallaceRoom',(g.describe(),[g.flag(f) for f in BADGES])
    # Door must be physically closed before a victory, with no rear warp.
    assert g.collision_at(6,2)[0]!=0
    for i,n in enumerate(MEMBERS):
        assert current(g)=='PlasticOx_'+n+'Room'
        mon=g.syms['gParties'];stride=g.sizes['gParties']//24
        item(g,mon,520)  # Consumed Oran Berry must follow global restoration.
        start_battle(g,n)
        item(g,mon,0)
        def drain(data, offsets):
            data[offsets[1]+8:offsets[1]+12]=bytes([1,2,3,4])
        secure(g,mon,drain)
        finish_battle(g,1,status=16)  # Burn is safe to carry while walking.

        if n=='Bill':break
        settle(g)
        assert g.flag(FLAGS[i]),(n,'victory flag')
        mon=g.syms['gParties'];stride=g.sizes['gParties']//24
        assert g.u16(mon+stride-14)==1,(n,'unexpected autoheal')
        assert g.u32(mon+stride-20)==16,(n,'status healed')
        data,offsets=secure(g,mon)
        assert bytes(data[offsets[1]+8:offsets[1]+12])==bytes([1,2,3,4]),(n,'PP healed')
        assert item(g,mon)==520,(n,'held item not restored')
        assert g.collision_at(6,2)[0]==0,(n,'door stayed closed')
        # The generic walking fixture treats stale battle-type bits as a live
        # battle; after proving the return callback, clear only that test input.
        assert g.u32(g.syms['gMain']+4)&~1 == g.syms['CB2_Overworld']&~1
        g.write(g.syms['gBattleTypeFlags'],0,4)
        # Continue through the opened physical door without healing.
        navigate(g,lambda x,y:(x,y)==(6,3));g.tap(K.KEY_UP,hold=16,wait=240)
    # Bill's normal victory callback must reach the Hall and start GameClear.
    for _ in range(1500):
        g.tap(K.KEY_A,hold=2,wait=10)
        if g.flag('FLAG_SYS_GAME_CLEAR'):break
    else:raise AssertionError('Bill did not reach GameClear')
    assert current(g)=='PlasticOx_HallOfFame'
    ptr=int(g.state()['ptr'],16)
    assert (g.u8(ptr+12),g.u8(ptr+13))==IDS['IndigoPlateau_hns']
    # Let the actual HoF task register the party and save before credits.
    recorded=False
    for tick in range(1800):
        g.tap(K.KEY_A,hold=2,wait=10)
        cb=g.u32(g.syms['gMain']+4)&~1
        if cb==(g.syms['CB2_HallOfFame']&~1) and tick==100:
            shot(g,'hall_of_fame')
        hof=g.u32(g.syms['gHoFSaveBuffer'])
        if hof and (g.u16(hof+8)>>1)==376:recorded=True
        if cb==(g.syms['CB2_Credits']&~1):break
    else:raise AssertionError('credits did not start')
    assert recorded,'party was not registered in Hall of Fame buffer'
    shot(g,'credits');g.frame(120)
    g.core.reset();g.frame(400);g.tap(K.KEY_START,wait=100);g.tap(K.KEY_A,wait=500)
    assert g.u32(g.syms['gMain']+4)&~1 == g.syms['CB2_Overworld']&~1
    assert current(g)=='IndigoPlateau_hns',g.describe()
    assert g.flag('FLAG_SYS_GAME_CLEAR')
    data,offsets=secure(g,g.syms['gParties'])
    assert struct.unpack_from('<I',data,offsets[3]+8)[0]&(1<<15),'Champion ribbon not saved'
    shot(g,'continue')
    g.tap(K.KEY_DOWN,hold=16,wait=30)
    # Use the Champion save's real flag to open the existing ferry gate.
    g.flag('FLAG_POX_TRIGGERS_ENABLED',True)
    from test_region_walk import PORTS
    port=PORTS['lavender_harbor_a']
    g.warp(port['source'],*port['approach'])
    g.tap({'N':K.KEY_UP,'S':K.KEY_DOWN,'E':K.KEY_RIGHT,'W':K.KEY_LEFT}[port['direction']],hold=16,wait=240)
    assert current(g)==port['destination'],'Champion save did not unlock ferry'
    shot(g,'postgame_ferry')
    print('PASS: Wallace→Steven→Lance→Blue→Bill, six opponents each, persistent HP/status/PP, held items, HoF record/ribbon, credits, flash Continue at Indigo and unlocked ferry',flush=True)
    # Lose at each stage. Earlier wins and all trainer flags must be cleared
    # when the nurse receives the blacked-out player.
    name_length=int(re.search(r'#define POKEMON_NAME_LENGTH (\d+)',(ROOT/'include/constants/global.h').read_text())[1])
    turn_offset=8+name_length+1
    opponent_move_offset=0x24+2*(name_length-10)
    for i,n in enumerate(MEMBERS):
        g=prepare(('IndigoPlateau_PokemonCenter_hns',19,14))
        for f in FLAGS[:i]:g.flag(f,True)
        for prev in MEMBERS[:i]:trainer_flag(g,prev.upper(),True)
        g.warp('PlasticOx_'+n+'Room',6,11)
        start_battle(g,n);finish_battle(g,2);settle(g,7200)
        assert current(g)=='IndigoPlateau_PokemonCenter_hns',(n,g.describe())
        assert not any(g.flag(f) for f in FLAGS),(n,'stale sequence flag')
        assert not any(trainer_flag(g,m.upper()) for m in MEMBERS),(n,'stale trainer flag')
        assert not g.flag('FLAG_SYS_GAME_CLEAR')
        g.write(g.syms['gBattleTypeFlags'],0,4)
        navigate(g,lambda x,y:(x,y)==(32,4))
        g.tap(K.KEY_UP,hold=2,wait=12);g.tap(K.KEY_A,wait=20);settle(g)
        assert current(g)=='PlasticOx_WallaceRoom',(g.describe(),[g.flag(f) for f in BADGES])
        print('PASS: loss to '+n+' heals at Indigo, clears challenge and restarts at Wallace',flush=True)



def route_battles():
    route=json.loads((ROOT/'data/maps/PlasticOx_VictoryRoad/map.json').read_text())
    for o in route['object_events']:
        if o['trainer_type']!='TRAINER_TYPE_NORMAL':continue
        tid=o['script'].removeprefix('PoxLeague_')
        g=prepare(('PlasticOx_VictoryRoad',o['x'],o['y']+1))
        start_battle(g,tid,(o['x'],o['y']))
        finish_battle(g,1);settle(g)
        assert trainer_flag(g,tid),(tid,'win not recorded')
        g.write(g.syms['gBattleTypeFlags'],0,4)
        g.warp('PlasticOx_VictoryRoad',o['x'],o['y']+1)
        g.tap(K.KEY_UP,hold=2,wait=12);g.tap(K.KEY_A,wait=20);settle(g)
        assert not g.u32(g.syms['gBattleTypeFlags'])&8,(tid,'unwanted rematch')
        print('PASS: route trainer '+tid+' creates six opponents and retains victory',flush=True)
    g=prepare(('PlasticOx_VictoryRoad',27,47))
    g.write(g.syms['sWildEncountersDisabled'],0)
    for i in range(600):
        g.tap(K.KEY_DOWN if i%2==0 else K.KEY_UP,hold=12,wait=12)
        if g.u32(g.syms['gMain']+4)&~1==g.syms['BattleMainCB2']&~1:break
    else:raise AssertionError('No wild grass encounter')
    g.frame(240)
    stride=g.sizes['gParties']//24;enemy=g.syms['gParties']+6*stride
    assert 52<=g.u8(enemy+stride-16)<=56
    assert g.box_species(enemy) in [85,28,128,232,227,214,308,286,203,132,371,374]
    shot(g,'wild');print('PASS: high-level outdoor wild encounter from the authored table',flush=True)
    g=prepare(('PlasticOx_VictoryRoad',27,48))
    for o in route['object_events']:
        if o['trainer_type']=='TRAINER_TYPE_NORMAL':trainer_flag(g,o['script'].removeprefix('PoxLeague_'),True)
    for i,(x,y) in enumerate([(24,11),(9,31)]):
        for visit in range(2):
            navigate(g,lambda a,b:(a,b)==(x,y+1))
            g.tap(K.KEY_UP,hold=16,wait=240)
            assert current(g)=='PlasticOx_LeagueRestHouse'+str(i+1),g.describe()
            # The native carpet is deliberately excluded by the pathfinder.
            g.tap(K.KEY_UP,hold=32,wait=30)
            assert g.state()['y']<9,('blocked carpet',i,g.describe())
            navigate(g,lambda a,b:(a,b)==(4,5))
            mon=g.syms['gParties'];stride=g.sizes['gParties']//24
            g.write(mon+stride-14,1,2)
            g.tap(K.KEY_UP,hold=2,wait=12);g.tap(K.KEY_A,wait=20);settle(g)
            assert g.u16(mon+stride-14)==(g.u16(mon+stride-12) if i else 1)
            shot(g,'rest_house_'+str(i+1))
            navigate(g,lambda a,b:(a,b)==(4,7))
            g.tap(K.KEY_DOWN,hold=48,wait=240)
            assert current(g)=='PlasticOx_VictoryRoad',g.describe()
    print('PASS: both houses enter, walk, interact, exit and re-enter (8 door crossings); western healer restores HP, advice does not',flush=True)
    g=prepare(('IndigoPlateau_hns',14,9))
    g.tap(K.KEY_RIGHT,hold=2,wait=12);g.tap(K.KEY_A,wait=20);settle(g)
    assert current(g)=='EcruteakCity_hns'
    print('PASS: downhill express returns to Ecruteak',flush=True)


def ai_turns():
    name_length=int(re.search(r'#define POKEMON_NAME_LENGTH (\d+)',(ROOT/'include/constants/global.h').read_text())[1])
    turn_offset=8+name_length+1
    opponent_move_offset=0x24+2*(name_length-10)
    opponents=[(n,'PlasticOx_'+n+'Room',(6,5),FLAGS[:i]) for i,n in enumerate(MEMBERS)]
    route=json.loads((ROOT/'data/maps/PlasticOx_VictoryRoad/map.json').read_text())
    opponents += [(o['script'].removeprefix('PoxLeague_'),'PlasticOx_VictoryRoad',(o['x'],o['y']),[]) for o in route['object_events'] if o['trainer_type']=='TRAINER_TYPE_NORMAL']
    for n,mapname,xy,flags in opponents:
        g=prepare((mapname,xy[0],xy[1]+1))
        for f in flags:g.flag(f,True)
        start_battle(g,n,xy)
        # Drive the actual action/move UI, with the ordinary trainer AI active.
        for _ in range(1200):
            g.tap(K.KEY_A,hold=2,wait=10)
            if g.u8(g.syms['gBattleResults']+turn_offset)>=1 and g.u16(g.syms['gBattleResults']+opponent_move_offset):break
        else:
            shot(g,'ai_failure_'+n)
            raise AssertionError(('No opponent move executed',n))
        shot(g,'ai_'+n)
        assert g.u32(g.syms['gMetamonDecisions'])>0,(n,'policy never ran')
        assert g.u32(g.syms['gMetamonFault'])==0,(n,'policy fault')
        print('PASS: '+n+' executes an actual Metamon-selected move; decisions='+str(g.u32(g.syms['gMetamonDecisions'])),flush=True)


def save_continue(g):
    name=current(g)
    begin_code(g,opcode(g,'callnative')+struct.pack('<I',g.syms['Script_ForceSaveGame']|1)+opcode(g,'waitstate')+opcode(g,'end'))
    settle(g)
    g.core.reset();g.frame(400);g.tap(K.KEY_START,wait=100);g.tap(K.KEY_A,wait=500)
    assert current(g)==name,('Continue',name,g.describe())
    assert g.u32(g.syms['gMain']+4)&~1==g.syms['CB2_Overworld']&~1


def persistence():
    from test_sudowoodo_v1 import pocket,bag,POCKET_ITEMS
    for i,(x,y,key,reward) in enumerate([(10,34,K.KEY_LEFT,472),(15,29,K.KEY_UP,52),(20,12,K.KEY_UP,102)]):
        g=prepare(('PlasticOx_VictoryRoad',x,y))
        flag=f'FLAG_POX_LEAGUE_REWARD_{i}'
        slots,count=pocket(g,POCKET_ITEMS)
        xor=next(g.u16(slots+4*j+2) for j in range(count) if g.u16(slots+4*j)==0)
        saved=[g.u32(slots+4*j) for j in range(count)]
        for j in range(count):
            g.write(slots+4*j,28,2);g.write(slots+4*j+2,999^xor,2)
        g.tap(key,hold=2,wait=12);g.tap(K.KEY_A,wait=20);settle(g)
        assert not g.flag(flag),('full bag consumed reward',i)
        for j,value in enumerate(saved):g.write(slots+4*j,value,4)
        before=bag(g,reward,POCKET_ITEMS)
        g.tap(K.KEY_A,wait=20);settle(g)
        assert g.flag(flag) and bag(g,reward,POCKET_ITEMS)==before+1
        save_continue(g)
        assert g.flag(flag) and bag(g,reward,POCKET_ITEMS)==before+1
        g.tap(key,hold=2,wait=12);g.tap(K.KEY_A,wait=20);settle(g)
        assert bag(g,reward,POCKET_ITEMS)==before+1,('duplicate pickup',i)
        print(f'PASS: reward {i} full bag, retry, flash save/Continue, no repeat collection',flush=True)
    for i,n in enumerate(MEMBERS[:-1]):
        g=prepare(('PlasticOx_'+n+'Room',6,11))
        for f in FLAGS[:i+1]:g.flag(f,True)
        for prev in MEMBERS[:i+1]:trainer_flag(g,prev.upper(),True)
        # Reload the room normally so its saved victory controls the door.
        g.warp('PlasticOx_'+n+'Room',6,11)
        save_continue(g)
        assert all(g.flag(f) for f in FLAGS[:i+1])
        assert all(trainer_flag(g,prev.upper()) for prev in MEMBERS[:i+1])
        assert g.collision_at(6,2)[0]==0,(n,'saved open door')
        navigate(g,lambda x,y:(x,y)==(6,3));g.tap(K.KEY_UP,hold=16,wait=240)
        assert current(g)=='PlasticOx_'+MEMBERS[i+1]+'Room'
        print('PASS: '+n+' flash save/Continue preserves challenge and opens next room',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--static',action='store_true');p.add_argument('--travel',action='store_true');p.add_argument('--battles',action='store_true');p.add_argument('--route',action='store_true');p.add_argument('--ai',action='store_true');p.add_argument('--persistence',action='store_true');a=p.parse_args()
    if a.static:static()
    if a.travel:travel()
    if a.battles:battles()

    if a.route:route_battles()
    if a.ai:ai_turns()

    if a.persistence:persistence()
