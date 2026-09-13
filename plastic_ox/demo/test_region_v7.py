#!/usr/bin/env python3
"""Walk v7 boundary triggers in mGBA; setup warps isolate each crossing.

These are physical boundary tests, not a fresh-save story playthrough.
No transition script is injected: every tested transition starts with a D-pad
step from the manifest's adjacent approach tile.
"""
import argparse
import json
import re
from pathlib import Path

from test_story import StoryGame, ROOT
from walklib import K

KEYS = dict(N=K.KEY_UP, S=K.KEY_DOWN, W=K.KEY_LEFT, E=K.KEY_RIGHT)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', default='')
    parser.add_argument('--only', default='')
    parser.add_argument('--closed', action='store_true', help='Deny each required flag independently')
    parser.add_argument('--warps', action='store_true', help='Test retained native dungeon/door crossings')
    args = parser.parse_args()
    manifest = json.loads((ROOT/'plastic_ox/alpha/region_manifest.json').read_text())
    groups = json.loads((ROOT/'data/maps/map_groups.json').read_text())
    ids = {n: (i,j) for i,k in enumerate(groups['group_order']) for j,n in enumerate(groups[k])}
    out = ROOT/'plastic_ox/demo/shots'/('region_v7'+('_'+args.build if args.build else ''))
    out.mkdir(parents=True, exist_ok=True)
    g = StoryGame(build=args.build)
    g.flag('FLAG_POX_STORY_STARTER', True)
    g.flag('FLAG_ADVENTURE_STARTED', True)
    g.flag('FLAG_POX_HIDE_UNUSED_ACTOR', True)
    for flag in range(0x500, 0x860):
        g.flag(flag, True)
    if args.warps:
        native_warps(g,ids,out,args.only)
        return
    for p in manifest['transitions']:
        for flag in p['requires']:
            g.flag(flag, True)
    # Explicitly prove the northern region doesn't inherit Bruno/Silph gates.
    g.flag('FLAG_BADGE07_GET', False)
    g.flag('FLAG_POX_STORY_SILPH', False)
    results = []
    for p in manifest['transitions']:
        if args.only and args.only not in p['id']:
            continue
        if args.closed:
            assert args.build == 'triggers', 'Closed gates require the trigger ROM'
            for missing in p['requires']:
                for flag in p['requires']:
                    g.flag(flag, True)
                g.warp(p['source'], *p['approach'])
                g.flag(missing, False)
                g.tap(KEYS[p['direction']], hold=24, wait=90)
                for _ in range(300):
                    g.tap(K.KEY_A,hold=2,wait=15)
                    if g.u8(g.syms['sGlobalScriptContextStatus']) == 2:
                        g.frame(180)
                        break
                else:
                    raise AssertionError((p['id'],missing,'closed gate never released controls'))
                s=g.state()
                assert (s['group'],s['num']) == ids[p['source']], (p['id'],missing,s)
                assert [s['x'],s['y']] == p['approach'], (p['id'],missing,s)
                g.flag(missing, True)
                results.append(dict(id=p['id'],missing=missing,passed=True))
                print(p['id']+' denied without '+missing,flush=True)
            continue
        if p['id'].startswith(('ecruteak_league','victory_indigo')):
            g.flag('FLAG_BADGE07_GET', True)
        else:
            g.flag('FLAG_BADGE07_GET', False)
        try:
            g.warp(p['source'], *p['approach'])
            start = g.state()
            g.tap(KEYS[p['direction']], hold=24, wait=90)
            for _ in range(30):
                if (g.state()['group'],g.state()['num']) == ids[p['destination']]:
                    break
                g.tap(K.KEY_A, hold=2, wait=20)
            g.frame(180)
            state = g.state()
            assert (state['group'],state['num']) == ids[p['destination']], (p['id'],start,state)
            assert [state['x'],state['y']] == p['landing'], (p['id'],'landing',state,p['landing'])
            assert g.collision_at(state['x'],state['y'])[0] == 0, (p['id'],'blocked landing')
            result = dict(id=p['id'],passed=True)
        except (AssertionError, KeyError) as e:
            result = dict(id=p['id'],passed=False,error=str(e))
        g.fb.to_pil().convert('RGB').save(out/(p['id']+'.png'))
        results.append(result)
        print(json.dumps(result),flush=True)
    (out/'report.json').write_text(json.dumps(results,indent=2)+'\n')
    failures = [r for r in results if not r['passed']]
    assert results and not failures, f'{len(failures)}/{len(results)} crossings failed'
    print(f'PASS: {len(results)} actual D-pad crossings')


def native_warps(g,ids,out,only):
    maps={name:json.loads((ROOT/f'data/maps/{name}/map.json').read_text()) for name in ids}
    byid={d['id']:n for n,d in maps.items()}
    selected={'Route2_Frlg','IlexForest_hns','Route46_hns','DarkCave_SouthSide_hns',
              'Route2_ViridianForest_NorthEntrance_Frlg','Route2_ViridianForest_SouthEntrance_Frlg',
              'Route2_House_Frlg','Route2_EastBuilding_Frlg','Route25_hns','Route25_BillsHouse_hns',
              'Route115','Route8_Frlg','Route7_hns','PlasticOx_Route20West','PlasticOx_Route20East'}
    selected.update(n for n in maps if n.startswith(('SeafoamIslands_','UndergroundPath_','MeteorFalls_','VictoryRoad_')) and maps[n].get('region','REGION_HOENN') == 'REGION_HOENN')
    # Isolate traversal from native puzzle state. Boulder mechanics are tested
    # separately; this mode must not pretend to solve them by walking ladders.
    for flag in ['FLAG_POX_STOPPED_SEAFOAM_B3F_CURRENT','FLAG_POX_STOPPED_SEAFOAM_B4F_CURRENT']:
        g.flag(flag,True)
    records=[]
    behaviors=[m[1] for line in (ROOT/'include/constants/metatile_behaviors.h').read_text().splitlines() if (m:=re.match(r'\s*(MB_\w+)\s*,',line))]
    for name in sorted(selected):
        if only and only not in name:
            continue
        for index,w in enumerate(maps[name]['warp_events']):
            dest=byid.get(w['dest_map'])
            if dest not in selected or dest == name:
                continue
            landing_only={'IlexForest_hns':{1},'SeafoamIslands_B1F_Frlg':{9,10},'SeafoamIslands_B2F_Frlg':{7,8},'SeafoamIslands_B3F_Frlg':{5,6},'SeafoamIslands_B4F_Frlg':{2,3}}
            if index in landing_only.get(name,set()):
                records.append(dict(source=name,warp=index,destination=dest,passed=True,landing_only=True))
                continue
            attempts=[]
            for direction,dx,dy in [('N',0,-1),('S',0,1),('E',1,0),('W',-1,0)]:
                x,y=w['x']-dx,w['y']-dy
                g.warp(name,x,y)
                behavior=behaviors[g.behavior_at(w['x'],w['y'])[0]]
                if behavior in ['MB_NORMAL','MB_POND_WATER','MB_SURFABLE_WATER','MB_INTERIOR_DEEP_WATER']:
                    # Native boulder/current destination anchors are not exits.
                    records.append(dict(source=name,warp=index,destination=dest,passed=True,landing_only=True))
                    break
                if g.collision_at(x,y)[0]:
                    continue
                g.tap(KEYS[direction],hold=48,wait=300)
                s=g.state()
                if (s['group'],s['num']) == ids[dest]:
                    g.frame(180)
                    s=g.state()
                    assert (s['group'],s['num']) == ids[dest], (name,index,'unstable destination',s)
                    if g.collision_at(s['x'],s['y'])[0]:
                        # Some native stair/door landings are solid to entry
                        # but allow walking out; prove that exit explicitly.
                        for key in KEYS.values():
                            g.tap(key,hold=24,wait=30)
                            t=g.state()
                            if (t['group'],t['num']) == ids[dest] and not g.collision_at(t['x'],t['y'])[0]:
                                break
                        else:
                            records.append(dict(source=name,warp=index,destination=dest,passed=False,error='blocked landing'))
                            print(name+':'+str(index)+' FAIL blocked landing '+str(s),flush=True)
                            break
                    g.fb.to_pil().convert('RGB').save(out/f'warp_{name}_{index}.png')
                    records.append(dict(source=name,warp=index,destination=dest,passed=True))
                    print(name+':'+str(index)+' -> '+dest+' PASS',flush=True)
                    break
                attempts.append(s)
            else:
                records.append(dict(source=name,warp=index,destination=dest,passed=False,attempts=attempts))
                print(name+':'+str(index)+' FAIL '+str(attempts),flush=True)
    (out/'native_warps.json').write_text(json.dumps(records,indent=2)+'\n')
    failures=[r for r in records if not r['passed']]
    assert records and not failures, f'{len(failures)}/{len(records)} native warps failed'
    print(f'PASS: {sum(not r.get("landing_only") for r in records)} native crossings; {sum(bool(r.get("landing_only")) for r in records)} landing-only anchors excluded')


if __name__ == '__main__':
    main()
