#!/usr/bin/env python3
"""Underground tournament acceptance checks on the built ROM.

Battle finish injection exercises normal engine callbacks, not battle AI.
Save checks write only the emulator's in-memory flash.
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'plastic_ox/agent'))
sys.path.insert(0, str(ROOT / 'plastic_ox/alpha'))
from test_trainer_teams_v2 import parse, parse_mon
import pox_progression as P
from region_geometry import Geometry

TUNNEL = 'UndergroundPath_EastWestTunnel_Frlg'
ITEMS = ['CONTEST_PASS', 'ANCIENT_BRAILLE_TABLET', 'NEW_MAUVILLE_KEY', 'RED_ORB']
GATES = ['FLAG_BADGE04_GET', 'FLAG_BADGE05_GET', 'FLAG_BADGE06_GET', 'FLAG_POX_LEAGUE_BILL']
POSITIONS = [36, 39, 42, 33]
PARTIES = ROOT / 'plastic_ox/alpha/tournament/trainers.party'


def static():
    g = Geometry(TUNNEL)
    blocked = {(o['x'], o['y']) for o in g.data['object_events']}
    assert (75, 4) in g.component((4, 4), blocked=blocked)
    assert (4, 4) in g.component((75, 4), blocked=blocked)
    assert not g.data['coord_events']
    tiers = P.load_tiers()
    for tid, block in parse(PARTIES.read_text()).items():
        mons = [parse_mon(c) for c in block.strip().split('\n\n')[1:]]
        assert len(mons) == 6
        stage = int(tid[-1]) if 'TOURNAMENT_' in tid else 2 if 'REGIROCK' in tid else 3
        max_tier = {1: 'UU', 2: 'UUBL', 3: 'OU', 4: 'OU'}[stage]
        level = {1: 42, 2: 50, 3: 55, 4: 75}[stage]
        for m in mons:
            assert P.TIER_ORDER.index(tiers[m['species']]) <= P.TIER_ORDER.index(max_tier), (tid, m)
            assert m['level'] == level
            assert len(set(m['moves'])) == 4 and set(m['moves']) <= P.load_gen3_moves()
            assert sum(m['evs'].values()) <= 510 and max(m['evs'].values()) <= 252
            assert m['ability'] and m['nature'] and m['item']
            if 'TOURNAMENT' in tid:
                assert not m['species'].startswith('SPECIES_REGI')
    # Reapplying the overlay must be byte-identical, with no duplicated actors.
    import tournament
    writes = {}
    tournament.install(lambda p: (ROOT / p).read_text(), lambda p, s: writes.__setitem__(p, s))
    # Installer performs sequential reads/writes of Regi objects; model that too.
    writes = {}
    tournament.install(lambda p: writes.get(p, (ROOT / p).read_text()), lambda p, s: writes.__setitem__(p, s))
    assert all((ROOT / p).read_text() == s for p, s in writes.items()), [p for p,s in writes.items() if (ROOT/p).read_text()!=s]
    print('PASS: bidirectional tunnel, no tile triggers, tiers/levels/ADV moves/EVs, no tournament Regis, idempotent overlay', flush=True)


def runtime():
    from test_league import prepare, finish_battle, settle, trainer_flag, current, save_continue
    from test_cinnabar import save_reload
    from test_sudowoodo_v1 import bag, const, give_item, wait_for_battle, in_battle
    from test_training_kit import run_code
    from test_qol import opcode
    from walklib import K
    from test_national_park import set_weekday, call
    out = Path('/tmp/pox_tournament_shots'); out.mkdir(exist_ok=True)
    def shot(g, name): g.fb.to_pil().convert('RGB').save(out / (name + '.png'))
    g = prepare((TUNNEL, 33, 3))
    for gate in GATES: g.flag(gate, False)
    def at_actor(x):
        g.write(g.syms['gBattleTypeFlags'], 0, 4)
        g.warp(TUNNEL, x, 3); g.frame(150)
        g.tap(K.KEY_UP, hold=2, wait=12); g.tap(K.KEY_A, hold=2, wait=15)
    def start(x):
        at_actor(x)
        for _ in range(400):
            g.tap(K.KEY_A, hold=2, wait=10)
            if g.u32(g.syms["gBattleTypeFlags"]) & 8: break
        else: raise AssertionError(("no battle", g.describe()))
        g.frame(240)
        assert g.u8(g.syms['gPartiesCount']+1) == 6
    def no_battle(x):
        at_actor(x); settle(g)
        assert not in_battle(g)
    # Even with later badges, the prior round is mandatory.
    for gate in GATES: g.flag(gate, True)
    for x in POSITIONS[1:3]: no_battle(x)
    for gate in GATES: g.flag(gate, False)
    no_battle(POSITIONS[0])
    for i, (x, gate, reward) in enumerate(zip(POSITIONS, GATES, ITEMS), 1):
        no_battle(x)
        g.flag(gate, True)
        start(x)
        finish_battle(g, 2); settle(g)
        assert not g.flag('FLAG_POX_TOURNAMENT_REWARD_'+str(i))
        assert not trainer_flag(g, 'TOURNAMENT_'+str(i))
        assert bag(g, const('ITEM_'+reward, 'items.h')) == 0
        start(x)
        assert g.u16(g.syms['gTrainerBattleParameter']+2) == g.const('TRAINER_PLASTIC_OX_TOURNAMENT_'+str(i))
        shot(g, 'round'+str(i))
        finish_battle(g, 1); settle(g)
        item = const('ITEM_'+reward, 'items.h')
        assert g.flag('FLAG_POX_TOURNAMENT_REWARD_'+str(i)) and bag(g, item)==1
        no_battle(x)
        assert bag(g, item)==1
        assert not g.flag('FLAG_POX_STORY_SPACE_CENTER')
        print('PASS: round',i,'gates, battle, reward and revisit',flush=True)
    save_continue(g)
    for i, reward in enumerate(ITEMS,1):
        assert g.flag('FLAG_POX_TOURNAMENT_REWARD_'+str(i))
        assert bag(g,const('ITEM_'+reward,'items.h'))==1
        assert trainer_flag(g,'TOURNAMENT_'+str(i))
    shot(g,'saved_rewards')
    print('PASS: loss does not advance; real save/reset/Continue retains all rewards and victories',flush=True)
    g.flag('FLAG_SYS_CLOCK_SET',True)
    g.flag('FLAG_POX_DAILY_PARK_CONTEST',False)
    set_weekday(g,4)
    assert call(g,'PlasticOxContest_CheckEntry')==0
    assert bag(g,const('ITEM_CONTEST_PASS','items.h'))==1
    print('PASS: tournament-issued permanent pass opens Thursday contest',flush=True)
    # Mr. Stone consumes nothing and exposes a persistent research hook.
    g.warp('RustboroCity_DevonCorp_3F',8,4);g.frame(150)
    g.tap(K.KEY_UP,hold=2,wait=12);g.tap(K.KEY_A,wait=20);settle(g)
    assert g.flag('FLAG_POX_GROUDON_RESEARCH')
    assert bag(g,const('ITEM_RED_ORB','items.h'))==1
    shot(g,'stone')
    print('PASS: Red Orb activates Mr. Stone research without granting Groudon',flush=True)
    return g


def downstream():
    from test_cinnabar import Game, save_reload, finish_trainer
    from test_league import finish_battle, trainer_flag, current
    from test_sudowoodo_v1 import (bag, const, give_item, wait_for_battle,
        in_battle, talk, drain, fight, battle_mon, settle, K, opcode, run_code, POCKET_BALLS, in_overworld)
    from test_region_walk import navigate
    g=Game()
    for p in (ROOT / "include/constants").glob("vars*.h"):
        g.defs.update(dict(re.findall(r"^#define\s+(\w+)\s+([^/\n]+)",p.read_text(),re.M)))
    run_code(g,opcode(g,"callnative")+struct.pack("<I",g.syms["GivePlasticOxPlayerParty"]|1)+opcode(g,"releaseall"))
    run_code(g,opcode(g,"setflag")+struct.pack("<H",0xB7F)+opcode(g,"clearflag")+struct.pack("<H",0xB7F))
    give_item(g,const("ITEM_POKE_BALL","items.h"),20)
    for i in range(1,7):g.flag(f'FLAG_BADGE{i:02}_GET',True)
    out=Path('/tmp/pox_tournament_shots');out.mkdir(exist_ok=True)
    def shot(name):g.fb.to_pil().convert('RGB').save(out/(name+'.png'))
    def setvar(name,value):
        run_code(g,opcode(g,'setvar')+struct.pack('<HH',g.const(name),value))
    def interact(mapname,x,y):
        g.warp(mapname,x,y);g.frame(120)
        result=talk(g,K.KEY_UP)
        return result
    g.warp(TUNNEL,4,4);g.frame(120)
    navigate(g,lambda x,y:(x,y)==(75,4))
    navigate(g,lambda x,y:(x,y)==(4,4))
    shot('tunnel_walk')
    print('PASS: walked the full tunnel in both directions before tournament victories',flush=True)
    # Legacy Basement Key and an already-open vanilla save cannot bypass access.
    give_item(g,const('ITEM_BASEMENT_KEY','items.h'))
    setvar('VAR_NEW_MAUVILLE_STATE',2)
    g.warp('Route110',35,25);g.frame(120)
    g.hold(K.KEY_UP,25);g.frame(180)
    assert current(g)=='NewMauville_Entrance',g.state()
    assert g.var(g.const('VAR_NEW_MAUVILLE_STATE'))==0
    navigate(g,lambda x,y:(x,y)==(4,3))
    g.tap(K.KEY_UP,hold=24,wait=45);assert settle(g)
    assert g.var(g.const('VAR_NEW_MAUVILLE_STATE'))==0
    shot('mauville_locked')
    give_item(g,const('ITEM_NEW_MAUVILLE_KEY','items.h'))
    g.flag('FLAG_BADGE06_GET',False)
    g.warp('NewMauville_Entrance',4,3);g.frame(120)
    g.tap(K.KEY_UP,hold=24,wait=45);assert settle(g)
    assert g.var(g.const('VAR_NEW_MAUVILLE_STATE'))==0
    g.flag('FLAG_BADGE06_GET',True)
    g.warp('NewMauville_Entrance',4,3);g.frame(120)
    g.tap(K.KEY_UP,hold=24,wait=45);assert settle(g)
    shot('door_debug')
    assert g.var(g.const('VAR_NEW_MAUVILLE_STATE'))==1,(g.state(),g.text(),bag(g,const('ITEM_NEW_MAUVILLE_KEY','items.h')),g.flag('FLAG_BADGE06_GET'))
    g.hold(K.KEY_UP,24);g.frame(180)
    assert current(g)=='NewMauville_Inside',g.state()
    shot('mauville_inside')
    print('PASS: Route 110 entrance, legacy key/open-state denial, badge/key requirements and interior entry',flush=True)
    # The sage refuses before the stop switch, even when approached directly.
    assert interact('NewMauville_Inside',31,8)['dialogue']
    assert not in_battle(g) and not trainer_flag(g,'RAIKOU_SAGE')
    # Walk onto the actual generator's red button.
    g.warp('NewMauville_Inside',33,7);g.frame(120)
    g.tap(K.KEY_UP,hold=24,wait=40);assert settle(g)
    assert g.var(g.const('VAR_NEW_MAUVILLE_STATE'))==2
    g.flag('FLAG_BADGE06_GET',False)
    assert interact('NewMauville_Inside',31,8)['dialogue']
    assert not in_battle(g)
    g.flag('FLAG_BADGE06_GET',True)
    assert interact('NewMauville_Inside',31,8)['battle']
    assert wait_for_battle(g)
    assert g.u16(g.syms['gTrainerBattleParameter']+2)==g.const('TRAINER_PLASTIC_OX_RAIKOU_SAGE')
    assert g.u8(g.syms['gPartiesCount']+1)==6
    stride=g.sizes['gParties']//24
    assert g.box_species(g.syms['gParties']+11*stride)==const('SPECIES_RAIKOU','species.h')
    finish_trainer(g,True)
    for _ in range(1200):
        g.tap(K.KEY_A,hold=1,wait=6)
        if in_battle(g) and not (g.u32(g.syms["gBattleTypeFlags"])&8):break
    else:raise AssertionError(("reward did not start",g.text(),trainer_flag(g,"RAIKOU_SAGE")))
    assert wait_for_battle(g)
    assert not (g.u32(g.syms['gBattleTypeFlags'])&8)
    assert battle_mon(g,1)['species']==const('SPECIES_RAIKOU','species.h')
    assert trainer_flag(g,'RAIKOU_SAGE') and not g.flag('FLAG_POX_CAUGHT_RAIKOU')
    shot('raikou_reward')
    fight(g,'run');assert drain(g)
    assert not g.flag('FLAG_POX_CAUGHT_RAIKOU')
    save_reload(g)
    assert trainer_flag(g,'RAIKOU_SAGE')
    assert talk(g,K.KEY_UP)['battle'];assert wait_for_battle(g)
    assert not (g.u32(g.syms['gBattleTypeFlags'])&8)
    ball=const('ITEM_POKE_BALL','items.h');before=bag(g,ball,POCKET_BALLS)
    g.write(g.syms['gActionSelectionCursor'],1)
    g.tap(K.KEY_A,hold=1,wait=60)
    g.write(g.syms['gBagPosition']+5,POCKET_BALLS)
    g.write(g.syms['gBagPosition']+8+2*POCKET_BALLS,0)
    g.frame(60)
    for _ in range(20):
        g.tap(K.KEY_A,hold=2,wait=30)
        if bag(g,ball,POCKET_BALLS)<before:break
    assert bag(g,ball,POCKET_BALLS)==before-1
    for _ in range(2000):
        if in_overworld(g) and g.flag('FLAG_POX_CAUGHT_RAIKOU'):break
        g.tap(K.KEY_B,hold=2,wait=10)
    assert g.u8(g.syms['gBattleOutcome'])==7
    assert drain(g)
    assert g.flag('FLAG_POX_CAUGHT_RAIKOU')
    shot('raikou_caught')
    print('PASS: real stop switch, OU gate, six-member Raikou sage battle, flee/save/retry and guaranteed capture',flush=True)
    # Preserve the original chamber party puzzle; the tablet is an extra gate.
    g.warp('SealedChamber_InnerRoom',10,5);g.frame(120)
    assert talk(g,K.KEY_UP)['dialogue'];assert not g.flag('FLAG_REGI_DOORS_OPENED')
    give_item(g,const('ITEM_ANCIENT_BRAILLE_TABLET','items.h'))
    assert talk(g,K.KEY_UP)['dialogue'];assert not g.flag('FLAG_REGI_DOORS_OPENED')
    g.write(g.syms['gPartiesCount'],0)
    for j in range(g.sizes['gParties']//4):g.write(g.syms['gParties']+j,0)
    for species in ['WAILORD','RELICANTH']:
        run_code(g,opcode(g,'callnative')+struct.pack('<I',g.syms['ScrCmd_createmon']|1)+struct.pack('<BBHHI',0,6,const('SPECIES_'+species,'species.h'),50,0))
    assert talk(g,K.KEY_UP)['dialogue'];assert g.flag('FLAG_REGI_DOORS_OPENED')
    g.flag('FLAG_BADGE06_GET',False)
    for name in ['Regice','Registeel']:
        g.run('PoxTournament_'+name)
        assert not in_battle(g) and not trainer_flag(g,name.upper()+'_SAGE')
    for name,area in [('Regirock','DesertRuins'),('Regice','IslandCave'),('Registeel','AncientTomb')]:
        if name!='Regirock':g.flag('FLAG_BADGE06_GET',True)
        assert interact(area,8,8)['battle'];assert wait_for_battle(g)
        assert g.u16(g.syms['gTrainerBattleParameter']+2)==g.const('TRAINER_PLASTIC_OX_'+name.upper()+'_SAGE')
        finish_trainer(g,False);assert drain(g)
        assert not trainer_flag(g,name.upper()+'_SAGE')
    print('PASS: tablet plus Wailord/Relicanth chamber puzzle, UUBL Regirock and OU-only Regice/Registeel sages',flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--runtime',action='store_true');parser.add_argument('--downstream',action='store_true');args=parser.parse_args()
    static()
    if args.runtime: runtime()
    if args.downstream: downstream()
