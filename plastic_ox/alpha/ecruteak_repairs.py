"""Final Ecruteak event repairs, applied after region and League overlays."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CITY = 'EcruteakCity_hns'
GATE = 'Gate_EcruteakCity_Route38_hns'

def install(read, put):
    def load(n): return json.loads(read(f'data/maps/{n}/map.json'))
    def save(n,d): put(f'data/maps/{n}/map.json',json.dumps(d,indent=2)+'\n')
    def warp(x,y,d,i): return dict(x=x,y=y,elevation=0,dest_map=d,dest_warp_id=str(i))
    city=load(CITY)
    city['coord_events']=[e for e in city['coord_events'] if e['script'] not in ('PoxLeague_Checkpoint','PoxEcruteak_WestEntrance')]
    city['object_events']=[o for o in city['object_events'] if o['script'] not in ('Pox_MortyGuide','PoxLeague_GateGuide')]
    for o in city['object_events']:
        if o.get('local_id')=='LOCALID_ECRUTEK_SILVER': o.update(x=41,y=41)
        if o['graphics_id']=='OBJ_EVENT_GFX_POKE_BALL': o['graphics_id']='OBJ_EVENT_GFX_OLD_MAN_HNS'
        if o['script']=='Pox_DanceGuide':
            o.update(x=36,y=41,script='EcruteakCity_EventScript_Npc2')
        if o['script']=='EcruteakCity_EventScript_KimonoRoadblock':
            if o['graphics_id']=='OBJ_EVENT_GFX_SIGN':
                o.update(graphics_id='OBJ_EVENT_GFX_POLICEMAN',movement_type='MOVEMENT_TYPE_FACE_DOWN',flag='FLAG_BADGE03_GET')
            else: o['script']='EcruteakCity_EventScript_Npc3'
    city['warp_events']=[w for w in city['warp_events'] if not(w['x']==8 and 34<=w['y']<=37)]
    gate_index=len(city['warp_events'])
    for y in range(34,38): city['warp_events'].append(warp(8,y,'MAP_GATE_ECRUTEAK_CITY_ROUTE38_HNS',0))
    city['coord_events'] += [dict(type='trigger',x=8,y=y,elevation=0,var='VAR_TEMP_0',var_value=0,script='PoxEcruteak_WestEntrance') for y in range(34,38)]
    tower_index=next(i for i,w in enumerate(city['warp_events']) if w['dest_map']=='MAP_PLASTIC_OX_BURNED_TOWER')
    tower=load('PlasticOx_BurnedTower');tower['warp_events'][0]['dest_warp_id']=str(tower_index);save('PlasticOx_BurnedTower',tower)
    house=load('EcruteakCity_House2_hns')
    house_index=next(i for i,w in enumerate(city['warp_events']) if w['dest_map']==house['id'])
    house['warp_events']=[warp(4,8,city['id'],house_index),warp(4,7,city['id'],house_index)]
    for w in city['warp_events']:
        if w['dest_map']==house['id']: w['dest_warp_id']='1'
    save('EcruteakCity_House2_hns',house)
    gate=load(GATE)
    gate['warp_events']=[warp(11,5,city['id'],gate_index+1)]
    gate['object_events'][0].update(script='PoxLeague_GateGuide',x=6,y=2)
    gate['coord_events']=[dict(type='trigger',x=4,y=y,elevation=0,var='VAR_TEMP_0',var_value=0,script='PoxLeague_Checkpoint') for y in range(4,7)]
    save(GATE,gate);save(CITY,city)
    p='data/scripts/plastic_ox_league.inc'
    s=read(p).replace('warp MAP_ECRUTEAK_CITY_HNS, 9, 35','warp MAP_GATE_ECRUTEAK_CITY_ROUTE38_HNS, 5, 5')
    put(p,s)
    p=f'data/maps/{CITY}/scripts.inc'
    s=read(p).replace('EAST GATE CLOSED\\nFuture POKéMON LEAGUE site.$','MORTY must approve your passage.\\nEarn ECRUTEAK GYM\'s BADGE first.$')
    if 'PoxEcruteak_WestEntrance::' not in s:
        s += '\nPoxEcruteak_WestEntrance::\n\tlockall\n\twarp MAP_GATE_ECRUTEAK_CITY_ROUTE38_HNS, 10, 5\n\twaitstate\n\treleaseall\n\tend\n'
    put(p,s)
    gym=load('EcruteakCity_Gym_hns')
    gym['object_events'][-1].update(graphics_id='OBJ_EVENT_GFX_MAN_3',script='Pox_Morty')
    save('EcruteakCity_Gym_hns',gym)
    p='plastic_ox/alpha/region_manifest.json'
    manifest=json.loads(read(p))
    for edge in manifest['transitions']:
        if edge['id']=='ecruteak_league_a':
            edge.update(source=GATE,tile=[4,5],approach=[5,5])
        elif edge['id']=='ecruteak_league_b':
            edge.update(destination=GATE,landing=[5,5])
    put(p,json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':
    install(lambda p:(ROOT/p).read_text(),lambda p,s:(ROOT/p).write_text(s))
