#!/usr/bin/env python3
"""Continuous D-pad walks through v7 route legs, with one setup warp per leg.

Story completion and HM knowledge are test fixtures, not simulated victories.
After setup, map changes use ordinary player movement only.
"""
import argparse
from collections import deque
import json
import re
import struct
import sys
from pathlib import Path

from test_story import StoryGame,ROOT
from walklib import K
from walk_demo import object_tiles, step_toward
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'alpha'))
from region_geometry import Geometry

KEYS={'N':K.KEY_UP,'S':K.KEY_DOWN,'E':K.KEY_RIGHT,'W':K.KEY_LEFT}
DELTAS={'N':(0,-1),'S':(0,1),'E':(1,0),'W':(-1,0)}
BEHAVIORS=[m[1] for line in (ROOT/'include/constants/metatile_behaviors.h').read_text().splitlines() if (m:=re.match(r'\s*(MB_\w+)\s*,',line))]
GROUPS=json.loads((ROOT/'data/maps/map_groups.json').read_text())
IDS={n:(i,j) for i,k in enumerate(GROUPS['group_order']) for j,n in enumerate(GROUPS[k])}
MAPS={n:json.loads((ROOT/f'data/maps/{n}/map.json').read_text()) for n in IDS}
BYID={d['id']:n for n,d in MAPS.items()}
GEOMETRY={n:Geometry(n,MAPS[n]) for n in IDS}
PORTS={p['id']:p for p in json.loads((ROOT/'plastic_ox/alpha/region_manifest.json').read_text())['transitions']}
LEGS={
 'route2':('CherrygroveCity_hns',(33,1),[
     ('seam','N','Route2_Frlg'),('warp',2),('warp',3),'ilex_route2_north',('warp',3),
     ('seam','N','RustboroCity'),('seam','S','Route2_Frlg'),('warp',0),('warp',1),('warp',0),('warp',1),('seam','S','CherrygroveCity_hns')]),
 'early':('PalletTown_Frlg',(13,10),[
     ('seam','N','Route101'),('seam','N','OldaleTown'),('seam','W','Route29_hns'),('seam','W','CherrygroveCity_hns'),
     'cherry_route2_a',('warp',2),('warp',3),'ilex_route2_north',('warp',3),('seam','N','RustboroCity'),
     'rustboro_cottage_a',('seam','N','Route25_hns'),('warp',0),('warp',0),('seam','S','Route24_hns'),'rustboro_cottage_b',
     'rustboro_route44_a','route44_moon_a','moon_route33_a','route33_goldenrod_a']),
 'central':('GoldenrodCity_hns',(28,37),['goldenrod_route35_a','route35_park_a','park_route36_a',
     ('seam','N','Route37_hns'),'route37_ecruteak_a','ecruteak_route119_a','route119_fortree_a','fortree_route110_a','route110_lavender_a']),
 'underground':('LavenderTown_hns',(9,7),['lavender_route8_a',('warp',0),('warp',3),('warp',1),'underground_return_6','route7_route103_a','route103_cinnabar_a']),
 'coast':('PalletTown_Frlg',(12,18),[('surfwarp','S','Route21_North_Frlg',(7,18)),('seam','S','Route21_South_Frlg'),
     ('seam','S','CinnabarIsland_Frlg')]),
 'north':('MossdeepCity',(28,17),['mossdeep_route19_a','route19_saffron_a','saffron_route5_a','route5_route115_a',('warp',0),'meteor_blackthorn_a','blackthorn_route45_a','route45_route46_a',('warp',2),('warp',0)]),
 'postgame':('LavenderTown_hns',(9,7),['lavender_harbor_a','harbor_frontier_a','harbor_frontier_b','lavender_harbor_b']),
}


def current(g):
    s=g.state()
    return next(n for n,i in IDS.items() if i==(s['group'],s['num']))


def water(behavior):
    return any(k in behavior for k in ['WATER','OCEAN','POND','SEAWEED']) and not any(k in behavior for k in ['BRIDGE','WATERFALL','SHALLOW'])


def pathfind(g,goal,avoid):
    s=g.state(); info=g.mapheader_info(); sx,sy=s['x'],s['y']
    start=(sx,sy,g.collision_at(sx,sy)[1]); previous={start:None}; queue=deque([start]); occupied=object_tiles(g)
    while queue:
        x,y,e=queue.popleft()
        if goal(x,y):
            result=[]; p=(x,y,e)
            while p is not None:
                result.append(p[:2]);p=previous[p]
            return result[::-1]
        for direction,(dx,dy) in DELTAS.items():
            xx,yy=x+dx,y+dy
            if not (0<=xx<info['w'] and 0<=yy<info['h']):continue
            c,ee=g.collision_at(xx,yy); b=BEHAVIORS[g.behavior_at(xx,yy)[0]]
            if b=='MB_JUMP_'+{'N':'NORTH','S':'SOUTH','E':'EAST','W':'WEST'}[direction]:
                xx+=dx;yy+=dy
                if not(0<=xx<info['w'] and 0<=yy<info['h']):continue
                c,ee=g.collision_at(xx,yy);b=BEHAVIORS[g.behavior_at(xx,yy)[0]]
            if c or (xx,yy) in occupied or (xx,yy) in avoid:continue
            if any(t in b for t in ['DOOR','WARP','LADDER','HOLE','SECRET_BASE','WATERFALL']):continue
            oldb=BEHAVIORS[g.behavior_at(x,y)[0]]
            if water(b) and not g.test_water:continue
            surf_edge=(water(b) and e in (0,1,3)) or (water(oldb) and ee in (0,1,3))
            if e not in (0,15) and ee not in (0,15) and e != ee and not surf_edge:continue
            node=(xx,yy,e if ee==15 else ee)
            if node not in previous:previous[node]=(x,y,e);queue.append(node)
    return None


def navigate(g,goal):
    name=current(g); d=MAPS[name]
    warps=[w for i,w in enumerate(d['warp_events']) if not (name=='IlexForest_hns' and i==1)]
    avoid={(p['x'],p['y']) for p in d['coord_events']+warps if p.get('script') != 'Pox_StarterGate'}
    for _ in range(1500):
        s=g.state()
        assert current(g)==name,('unexpected transition',name,current(g))
        if goal(s['x'],s['y']):return
        path=pathfind(g,goal,avoid)
        assert path and len(path)>1,('no walking path',name,(s['x'],s['y']))
        for nxt in path[1:5]:
            s=g.state(); pos=(s['x'],s['y'])
            try:
                step_toward(g,pos,nxt)
            except AssertionError:
                assert g.u32(g.syms['gBattleTypeFlags']) == 0, 'unexpected battle during traversal'
                s=g.state()
                if (s['x'],s['y']) != pos:
                    break  # Native sideways stair animations can move diagonally.
                if water(BEHAVIORS[g.behavior_at(*nxt)[0]]):
                    print('Surf attempt',name,pos,nxt,flush=True)
                    g.tap(K.KEY_A,hold=2,wait=30)
                    for _ in range(300):
                        g.tap(K.KEY_A,hold=2,wait=12)
                        if g.u8(g.syms['sGlobalScriptContextStatus'])==2:break
                    g.frame(600)
                    s=g.state()
                    assert (s['x'],s['y']) != pos,('Surf did not start',name,pos,nxt)
                else:
                    # Some HNS side stairs only admit a particular approach.
                    # Replan around an edge that the real engine rejected.
                    avoid.add(nxt)
                break
            if current(g)!=name:return
    raise AssertionError(('walk timed out',name,g.state()))


def cross(g,direction,dest):
    for _ in range(8):
        g.tap(KEYS[direction],hold=24,wait=30)
        if current(g)==dest:
            g.frame(240)
            assert current(g)==dest
            return
    raise AssertionError(('crossing failed',dest,g.state()))


def setup(spawn=None):
    g=StoryGame(spawn=spawn);g.run('Pox_Squirtle')
    g.write(g.syms['sWildEncountersDisabled'],1)
    for p in PORTS.values():
        for f in p['requires']:g.flag(f,True)
    for f in range(0x500,0x860):g.flag(f,True)
    g.flag('FLAG_POX_HIDE_UNUSED_ACTOR',True)
    g.flag('FLAG_BADGE07_GET',False);g.flag('FLAG_POX_STORY_SILPH',False)
    table=g.syms['gScriptCmdTable']
    op=next(i for i in range((g.syms['gScriptCmdTableEnd']-table)//4) if g.u32(table+i*4)&~0x02000001==g.syms['ScrCmd_setmonmove']&~1)
    code=b''.join(bytes([op,0,i])+struct.pack('<H',move) for i,move in enumerate([57,70,249,148]))+bytes([2])
    ptr=g.syms['gStringVar4']
    for i,b in enumerate(code):g.write(ptr+i,b)
    g.run(ptr)
    return g


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('leg',choices=LEGS);args=parser.parse_args()
    name,xy,steps=LEGS[args.leg];g=setup((name,*xy));g.test_water=args.leg not in ('early','central','route2')
    if args.leg == 'coast':
        g.flag('FLAG_POX_TRIGGERS_ENABLED',False);g.flag('FLAG_BADGE05_GET',True)
    out=ROOT/'plastic_ox/demo/shots/region_walk';out.mkdir(exist_ok=True)
    for index,step in enumerate(steps):
        print(index,current(g),g.state()['x'],g.state()['y'],'->',step,flush=True)
        try:
            if isinstance(step,str):
                p=PORTS[step];assert current(g)==p['source'];navigate(g,lambda x,y:(x,y)==tuple(p['approach']));cross(g,p['direction'],p['destination'])
            elif step[0]=='seam':
                _,direction,dest=step;info=g.mapheader_info();dx,dy=DELTAS[direction]
                source=current(g); sg,dg=GEOMETRY[source],GEOMETRY[dest]
                connection=next(c for c in MAPS[source]['connections'] if BYID[c['map']]==dest)
                offset=connection['offset']
                def open_seam(x,y):
                    if direction=='N': tx,ty=x-offset,dg.h-1
                    elif direction=='S': tx,ty=x-offset,0
                    elif direction=='W': tx,ty=dg.w-1,y-offset
                    else: tx,ty=0,y-offset
                    edge=(direction=='N' and y==0) or (direction=='S' and y==sg.h-1) or (direction=='W' and x==0) or (direction=='E' and x==sg.w-1)
                    return edge and sg.passable(x,y,g.test_water) and dg.passable(tx,ty,g.test_water)
                navigate(g,open_seam)
                cross(g,direction,dest)
            elif step[0]=='surfwarp':
                _,direction,dest,approach=step
                navigate(g,lambda x,y:(x,y)==approach)
                cross(g,direction,dest)
            else:
                w=MAPS[current(g)]['warp_events'][step[1]];dest=BYID[w['dest_map']]
                behavior=BEHAVIORS[g.behavior_at(w['x'],w['y'])[0]]
                if 'STAIR_WARP' in behavior:
                    dx=1 if 'LEFT' in behavior else -1
                    navigate(g,lambda x,y:(x,y)==(w['x']+dx,w['y']))
                else:
                    navigate(g,lambda x,y:abs(x-w['x'])+abs(y-w['y'])==1)
                s=g.state();direction=next(k for k,(dx,dy) in DELTAS.items() if (s['x']+dx,s['y']+dy)==(w['x'],w['y']))
                cross(g,direction,dest)
        finally:
            g.fb.to_pil().convert('RGB').save(out/f'{args.leg}_{index:02}.png')
    print('PASS continuous '+args.leg+' leg: '+str(len(steps))+' transitions, no intermediate setup warps',flush=True)


if __name__=='__main__':main()
