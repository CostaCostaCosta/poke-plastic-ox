"""Physical v7 graph, applied last by build_story.py.

Text outputs are emitted through the story generator's apply_patch workflow.
Ports are selected from source geometry once and saved in region_ports.json;
subsequent regeneration uses those measured/reviewed coordinates verbatim.
"""
import copy
import json
import re
from pathlib import Path
from region_geometry import Geometry, DIRECTIONS

ROOT = Path(__file__).resolve().parents[2]
SPACE = ['FLAG_POX_STORY_SPACE_CENTER']
FUJI = ['FLAG_POX_STORY_FUJI']
MANSION = ['FLAG_POX_STORY_MANSION']
BADGES = [f'FLAG_BADGE{i:02}_GET' for i in range(1,9)]

# name: exploration anchor; the source component containing it owns the ports.
ANCHORS = {
    'PalletTown_Frlg':(13,10), 'Route101':(10,10), 'OldaleTown':(10,10),
    'Route29_hns':(60,20), 'CherrygroveCity_hns':(47,8), 'Route2_Frlg':(6,75),
    'IlexForest_hns':(22,62),
    'RustboroCity':(27,20), 'Route24_hns':(10,20), 'Route25_hns':(5,23),
    'Route44_hns':(1,15), 'MtMoon_Cave_hns':(10,11), 'Route33_hns':(27,18),
    'GoldenrodCity_hns':(28,37), 'Route35_hns':(15,47), 'NationalPark_Normal_hns':(39,24),
    'Route36_hns':(16,21), 'Route37_hns':(16,39), 'EcruteakCity_hns':(39,48),
    'Route119':(18,138), 'FortreeCity':(8,8), 'Route110':(15,95),
    'LavenderTown_hns':(9,7), 'Route8_Frlg':(60,20), 'Route7_hns':(4,25),
    'Route103':(10,10), 'Route21_North_Frlg':(12,10),
    'Route21_South_Frlg':(12,10), 'CinnabarIsland_Frlg':(12,10),
    'MossdeepCity':(28,17),
    'Route19_Frlg':(12,8), 'SaffronCity_hns':(16,23), 'Route5_hns':(25,35),
    'Route115':(27,38), 'MeteorFalls_1F_1R':(6,38), 'BlackthornCity_hns':(27,49),
    'Route45_hns':(15,5), 'Route46_hns':(20,12), 'VictoryRoad_1F':(15,39),
    'IndigoPlateau_hns':(11,7), 'PlasticOx_Harbor':(11,13),
    'PlasticOx_Route20West':(50,12), 'PlasticOx_Route20East':(15,12),
    'BattleFrontier_OutsideWest':(26,66),
}
WATER = {'Route103','Route19_Frlg','Route21_North_Frlg','Route21_South_Frlg',
         'Route115','MossdeepCity','CinnabarIsland_Frlg',
         'PlasticOx_Route20West','PlasticOx_Route20East'}

# Only these authored portals have a reviewed outdoor throat wide enough to
# warrant adjacent coordinate triggers. Cave mouths, facilities, one-tile
# shortcuts, and gated/object-blocked mouths retain their canonical center
# trigger. The geometry/occupancy checks below still veto an individual lane.
LANE_PORTALS = {
    'rustboro_route44','route33_goldenrod','goldenrod_route35','route35_park',
    'park_route36','route37_ecruteak','route119_fortree','route36_shortcut',
    'route110_lavender','lavender_route8','route8_saffron','route7_saffron',
    'route7_route103','oldale_route103','route103_cinnabar','cinnabar_sea',
    'sea_mossdeep','mossdeep_route19','route19_saffron','saffron_route5',
    'route5_route115','blackthorn_route45','route45_route46',
    'lavender_harbor','harbor_frontier',
}

# These transitions are visually self-explanatory roads.  Extra object signs
# narrowed their approaches and duplicated nearby native wayfinding.
SIGNLESS_TRAILS = {'rustboro_route44'}

# Explicit source/destination port targets. A target may name a compass edge;
# coordinates denote a native gate plaza, cave mouth, or dock.
TRAILS = [
    ('rustboro_route44','RustboroCity',(39,10),'Route44_hns',(0,13),[]),
    ('route44_moon','Route44_hns',(68,13),'MtMoon_Cave_hns',(4,11),[]),
    ('moon_route33','MtMoon_Cave_hns',(46,30),'Route33_hns',(27,18),['FLAG_POX_STORY_MTMOON']),
    ('route33_goldenrod','Route33_hns','W','GoldenrodCity_hns','S',[]),
    ('goldenrod_route35','GoldenrodCity_hns',(33,8),'Route35_hns','S',[]),
    ('route35_park','Route35_hns',(17,5),'NationalPark_Normal_hns',(24,51),[]),
    ('park_route36','NationalPark_Normal_hns',(39,20),'Route36_hns',(16,21),[]),
    ('route37_ecruteak','Route37_hns','N','EcruteakCity_hns','S',[]),
    ('ecruteak_route119','EcruteakCity_hns','E','Route119','S',['FLAG_BADGE03_GET']),
    ('route119_fortree','Route119',(39,8),'FortreeCity','W',['FLAG_POX_STORY_WEATHER']),
    ('fortree_route110','FortreeCity','E','Route110','N',['FLAG_BADGE04_GET']),
    ('route36_shortcut','Route36_hns','E','Route110',(1,67),['FLAG_POX_REACHED_FORTREE']),
    ('route110_lavender','Route110','S','LavenderTown_hns','N',['FLAG_BADGE04_GET']),
    ('lavender_route8','LavenderTown_hns','W','Route8_Frlg','E',FUJI),
    ('route8_saffron','Route8_Frlg',(8,20),'SaffronCity_hns','E',SPACE),
    ('route7_saffron','Route7_hns','E','SaffronCity_hns','W',SPACE),
    ('route7_route103','Route7_hns','W','Route103','E',FUJI),
    ('oldale_route103','OldaleTown','N','Route103',(10,20),FUJI),
    ('route103_cinnabar','Route103',(10,15),'CinnabarIsland_Frlg',(12,12),FUJI),
    ('cinnabar_sea','CinnabarIsland_Frlg','E','PlasticOx_Route20West','W',MANSION),
    ('sea_mossdeep','PlasticOx_Route20East','E','MossdeepCity','W',MANSION),
    ('mossdeep_route19','MossdeepCity','N','Route19_Frlg','S',[]),
    ('route19_saffron','Route19_Frlg','N','SaffronCity_hns','S',SPACE),
    ('saffron_route5','SaffronCity_hns','N','Route5_hns','S',SPACE),
    ('route5_route115','Route5_hns','N','Route115','S',SPACE),
    ('meteor_blackthorn','MeteorFalls_1F_1R',(26,18),'BlackthornCity_hns',(30,10),SPACE),
    ('blackthorn_route45','BlackthornCity_hns','S','Route45_hns','N',SPACE),
    ('route45_route46','Route45_hns','S','Route46_hns','N',SPACE),
    ('ecruteak_league','EcruteakCity_hns','W','VictoryRoad_1F',(15,39),BADGES),
    ('victory_indigo','VictoryRoad_1F',(39,6),'IndigoPlateau_hns','S',BADGES),
    ('lavender_harbor','LavenderTown_hns','S','PlasticOx_Harbor',(11,13),['FLAG_SYS_GAME_CLEAR']),
    ('harbor_frontier','PlasticOx_Harbor',(19,14),'BattleFrontier_OutsideWest',(26,66),['FLAG_SYS_GAME_CLEAR']),
]


def apply_region(read, put):
    def load(name):
        return json.loads(read(f'data/maps/{name}/map.json'))
    def save(name, data):
        indent=4 if name in {'DarkCave_SouthSide_hns','Gate_AzaleaTown_IlexForest_hns'} else 2
        put(f'data/maps/{name}/map.json',json.dumps(data,indent=indent)+'\n')
    def mid(name):
        return load(name)['id']

    # Preserve groups/room IDs; the harbor uses a native, recognizable terminal.
    if not read('data/maps/PlasticOx_Harbor/map.json'):
        harbor=copy.deepcopy(load('SlateportCity_Harbor'))
        harbor.update(id='MAP_PLASTIC_OX_HARBOR',name='PlasticOx_Harbor',connections=[],warp_events=[],coord_events=[],bg_events=[],object_events=[])
        save('PlasticOx_Harbor',harbor)
    groups=json.loads(read('data/maps/map_groups.json'))
    if 'PlasticOx_Harbor' not in groups['gMapGroup_PlasticOxV7']:
        groups['gMapGroup_PlasticOxV7'].append('PlasticOx_Harbor')
    put('data/maps/map_groups.json',json.dumps(groups,indent=2)+'\n')

    # Remove only obsolete outdoor connections; keep the proven opening seams
    # and native north/south joins that agree with v7.
    keep = {
        'PalletTown_Frlg':{'MAP_ROUTE101'},
        'Route21_North_Frlg':{'MAP_ROUTE21_SOUTH'},
        'Route21_South_Frlg':{'MAP_ROUTE21_NORTH','MAP_CINNABAR_ISLAND'},
        'CinnabarIsland_Frlg':{'MAP_ROUTE21_SOUTH'},
        'Route101':{'MAP_PALLET_TOWN','MAP_OLDALE_TOWN'},
        'OldaleTown':{'MAP_ROUTE101','MAP_ROUTE29_HNS'},
        'Route29_hns':{'MAP_OLDALE_TOWN','MAP_CHERRYGROVE_CITY_HNS'},
        'CherrygroveCity_hns':{'MAP_ROUTE29_HNS','MAP_ROUTE2'},
        'Route2_Frlg':{'MAP_CHERRYGROVE_CITY_HNS','MAP_RUSTBORO_CITY'},
        'RustboroCity':{'MAP_ROUTE2','MAP_ROUTE24_HNS'},
        'Route24_hns':{'MAP_RUSTBORO_CITY','MAP_ROUTE25_HNS'},
        'Route25_hns':{'MAP_ROUTE24_HNS'},
        'Route36_hns':{'MAP_ROUTE37_HNS'}, 'Route37_hns':{'MAP_ROUTE36_HNS','MAP_ECRUTEAK_CITY_HNS'},
        'EcruteakCity_hns':{'MAP_ROUTE37_HNS'},
        'BattleFrontier_OutsideWest':{'MAP_BATTLE_FRONTIER_OUTSIDE_EAST'},
    }
    retired={'Route2_hns','Route3_hns','Route4_hns','Route14_hns','Route16_hns','Route26_hns','Route34_hns','Route38_hns','Route41_hns','Route6_hns'}
    retired.update({'Route1_Frlg','Route31_hns','Route104','Gate_AzaleaTown_IlexForest_hns','CinnabarIsland_hns'})
    active=set(ANCHORS)
    extra_frlg=['UndergroundPath_EastEntrance_Frlg','UndergroundPath_WestEntrance_Frlg','UndergroundPath_EastWestTunnel_Frlg']+[f'SeafoamIslands_{floor}_Frlg' for floor in ['1F','B1F','B2F','B3F','B4F']]
    story_frlg=['PokemonMansion_1F_Frlg','MtMoon_1F_Frlg','MtMoon_B1F_Frlg','MtMoon_B2F_Frlg']
    route2_rooms=['Route2_ViridianForest_NorthEntrance_Frlg','Route2_ViridianForest_SouthEntrance_Frlg','Route2_House_Frlg','Route2_EastBuilding_Frlg']
    extra_frlg += route2_rooms
    for name in extra_frlg:
        d=load(name);d['region']='REGION_HOENN'
        d['object_events']=[o for o in d.get('object_events',[]) if not o.get('script','').startswith('PoxRegion_')]
        d['bg_events']=[o for o in d.get('bg_events',[]) if not o.get('script','').startswith('PoxRegion_')]
        save(name,d)
    layouts=json.loads(read('data/layouts/layouts.json'))
    for name in ['MtMoon_1F_Frlg','MtMoon_B1F_Frlg','MtMoon_B2F_Frlg']:
        d=load(name);d['region']='REGION_HOENN'
        save(name,d)
    needed={load(n)['layout'] for n in active | set(extra_frlg) | set(story_frlg)}
    needed.update(['LAYOUT_SEAFOAM_ISLANDS_B3F_CURRENT_STOPPED','LAYOUT_SEAFOAM_ISLANDS_B4F_CURRENT_STOPPED'])
    for layout in layouts['layouts']:
        if layout['id'] in needed and layout.get('layout_version')=='frlg':
            layout['include_in_versions']=sorted(set(layout.get('include_in_versions',[])) | {'emerald'})
    put('data/layouts/layouts.json',json.dumps(layouts,indent=2)+'\n')
    for name in sorted(active | retired):
        raw=read(f'data/maps/{name}/map.json')
        if not raw:
            continue
        d=json.loads(raw)
        d['connections']=[c for c in d.get('connections') or [] if c['map'] in keep.get(name,set())]
        if name in retired:
            d['warp_events']=[]
            d['coord_events']=[]
            for field in ['object_events','bg_events']:
                d[field]=[o for o in d.get(field,[]) if not o.get('script','').startswith('PoxRegion_')]
            script_path=f'data/maps/{name}/scripts.inc'
            old=read(script_path)
            put(script_path,re.sub(r'\A.*?\t.byte 0',name+'_MapScripts::\n\t.byte 0',old,count=1,flags=re.S))
        if name in active:
            d['region']='REGION_HOENN'
            d['object_events']=[o for o in d.get('object_events',[]) if not o.get('script','').startswith('PoxRegion_') or not o.get('script','').endswith('_Sign')]
            d['bg_events']=[o for o in d.get('bg_events',[]) if not o.get('script','').startswith('PoxRegion_') or not o.get('script','').endswith('_Sign')]
            # Remove source-world quest triggers; authored Pallet starter gate survives.
            d['coord_events']=[c for c in d.get('coord_events',[]) if c.get('script')=='Pox_StarterGate']
            if name == 'IlexForest_hns':
                # Imported HNS NPC sprites reset Emerald as they enter the
                # camera; retain the NPCs with equivalent native graphics.
                native_gfx = {
                    'OBJ_EVENT_GFX_PICNICKER_HNS':'OBJ_EVENT_GFX_PICNICKER',
                    'OBJ_EVENT_GFX_FAT_MAN_HNS':'OBJ_EVENT_GFX_FAT_MAN',
                    'OBJ_EVENT_GFX_BUG_CATCHER_HNS':'OBJ_EVENT_GFX_BUG_CATCHER',
                    'OBJ_EVENT_GFX_KIMONO_HNS':'OBJ_EVENT_GFX_WOMAN_3',
                }
                for o in d.get('object_events',[]):
                    o['graphics_id']=native_gfx.get(o.get('graphics_id'),o.get('graphics_id'))
            for o in d.get('object_events',[]):
                if name.endswith('_hns') and o.get('trainer_type')=='TRAINER_TYPE_NORMAL':
                    local_script=read(f'data/maps/{name}/scripts.inc')
                    label=o['script']
                    if label+'::' in local_script and not re.search(re.escape(label)+r'::\s*trainerbattle',local_script):
                        # Earlier imports retained trainer sight metadata on
                        # dialogue-only placeholder scripts. Sight detection
                        # treats their text as trainer data and crashes.
                        o['trainer_type']='TRAINER_TYPE_NONE'
                if 'WANDER' in o.get('movement_type',''):
                    o['movement_type']='MOVEMENT_TYPE_FACE_DOWN'
                if o.get('script')=='0x0' or any(x in o.get('script','') for x in ['Wally','Cozmo','Kecleon','BridgeAqua']):
                    o['flag']='FLAG_POX_HIDE_UNUSED_ACTOR'
            if name in ['Route33_hns','Route44_hns','Route45_hns']:
                geometry=Geometry(name,d)
                d['object_events']=[o for o in d['object_events'] if 0<=o['x']<geometry.w and 0<=o['y']<geometry.h]
        save(name,d)

    # Restore stable camera connections, including Cherrygrove's Route 2 trail
    # and the native FRLG coastal chain south of Route 21. Pallet's edge is
    # intentionally handled by water-tile triggers: a native connection accepts
    # walking across every overlapping tile and therefore cannot enforce Surf.
    coastal_connections = {
        'CherrygroveCity_hns': [
            {'map':'MAP_ROUTE29_HNS','offset':-6,'direction':'right'},
            {'map':'MAP_ROUTE2','offset':25,'direction':'up'},
        ],
        'Route2_Frlg': [
            {'map':'MAP_RUSTBORO_CITY','offset':-6,'direction':'up'},
            {'map':'MAP_CHERRYGROVE_CITY_HNS','offset':-25,'direction':'down'},
        ],
        'RustboroCity': [
            {'map':'MAP_ROUTE2','offset':6,'direction':'down'},
            {'map':'MAP_ROUTE24_HNS','offset':3,'direction':'up'},
        ],
        'Route24_hns': [
            {'map':'MAP_ROUTE25_HNS','offset':0,'direction':'up'},
            {'map':'MAP_RUSTBORO_CITY','offset':-3,'direction':'down'},
        ],
        'Route25_hns': [
            {'map':'MAP_ROUTE24_HNS','offset':0,'direction':'down'},
        ],
        'PalletTown_Frlg': [
            {'map':'MAP_ROUTE101','offset':2,'direction':'up'},
        ],
        'Route21_North_Frlg': [
            {'map':'MAP_ROUTE21_SOUTH','offset':0,'direction':'down'},
        ],
        'Route21_South_Frlg': [
            {'map':'MAP_ROUTE21_NORTH','offset':0,'direction':'up'},
            {'map':'MAP_CINNABAR_ISLAND','offset':0,'direction':'down'},
        ],
        'CinnabarIsland_Frlg': [
            {'map':'MAP_ROUTE21_SOUTH','offset':0,'direction':'up'},
        ],
    }
    for name, connections in coastal_connections.items():
        d=load(name);d['connections']=connections;save(name,d)
    # Wayfinding belongs beside the four-lane entrance, not on the bridge.
    d=load('RustboroCity')
    d['bg_events']=[b for b in d.get('bg_events',[]) if b.get('script') != 'RustboroCity_EventScript_TunnelSign']
    d['object_events']=[o for o in d['object_events'] if o.get('script') != 'PoxRustboroNorthSign']
    d['object_events'].append(dict(graphics_id='OBJ_EVENT_GFX_SIGN',x=23,y=6,elevation=3,
        movement_type='MOVEMENT_TYPE_NONE',movement_range_x=0,movement_range_y=0,
        trainer_type='TRAINER_TYPE_NONE',trainer_sight_or_berry_tree_id='0',
        script='PoxRustboroNorthSign',flag='0'))
    save('RustboroCity',d)
    d=load('Route44_hns')
    d['bg_events']=[b for b in d.get('bg_events',[])
                    if (b.get('x'),b.get('y')) not in {(5,17),(66,13)}]
    save('Route44_hns',d)
    d=load('PalletTown_Frlg')
    d['coord_events'] += [dict(type='trigger',x=x,y=19,elevation=0,var='VAR_TEMP_0',var_value=0,script='PalletTown_SurfToRoute21') for x in range(7,11)]
    save('PalletTown_Frlg',d)
    d=load('Route21_North_Frlg')
    d['coord_events'] = [dict(type='trigger',x=x,y=0,elevation=0,var='VAR_TEMP_0',var_value=0,script='Route21_North_SurfToPallet') for x in range(7,11)]
    save('Route21_North_Frlg',d)

    # Explicit warp closures prevent original-world doors/caves from becoming
    # alternate routes. Preserve local homes, shops, and intentional dungeons.
    remove_dest={
        'Route104':{'MAP_PETALBURG_WOODS','MAP_ROUTE104_MR_BRINEYS_HOUSE'},
        'RustboroCity':{'MAP_RUSTBORO_CITY'}, 'GoldenrodCity_hns':{'MAP_ROUTE4_HNS'},
        'MtMoon_Cave_hns':{'MAP_ROUTE3_HNS','MAP_ROUTE4_HNS'},
        'Route103':{'MAP_ALTERING_CAVE'},
        'Route115':{'MAP_TERRA_CAVE_ENTRANCE'},
        'MeteorFalls_1F_1R':{'MAP_ROUTE114'},
        'VictoryRoad_1F':{'MAP_EVER_GRANDE_CITY'},
    }
    # Keep warp indices of retained floors/interiors stable; an obsolete
    # external warp is retargeted to a local landing instead of compacting IDs.
    for name, destinations in remove_dest.items():
        d=load(name)
        for w in d['warp_events']:
            if w['dest_map'] in destinations:
                w['dest_map']=mid(name)
                w['dest_warp_id']=str(d['warp_events'].index(w))
        # Regional mouths are replaced with explicit trail triggers below.
        if name in ('RustboroCity','GoldenrodCity_hns','MtMoon_Cave_hns','Route103'):
            d['warp_events']=[w for w in d['warp_events'] if w['dest_map'] != mid(name)]
        save(name,d)

    # Local Cottage entry and return; no Fortree service remains.
    d=load('Route25_BillsHouse_hns')
    d['object_events']=[o for o in d['object_events'] if o['script']!='Pox_CottageExit']
    d['warp_events']=[dict(x=7,y=9,elevation=0,dest_map=mid('Route25_hns'),dest_warp_id='0')]
    save('Route25_BillsHouse_hns',d)

    # The native east-west Underground is independent of Saffron's surface gates.
    d=load('Route8_Frlg')
    d['warp_events']=[d['warp_events'][0]]
    d['warp_events'][0]['dest_warp_id']='1'
    save('Route8_Frlg',d)
    d=load('Route7_hns')
    # Existing HNS tunnel doorway is (4,20); choose an approachable trail door
    # below if its behavior is not an ordinary FRLG door.
    d['warp_events']=[]
    save('Route7_hns',d)
    for name in ['UndergroundPath_EastEntrance_Frlg','UndergroundPath_WestEntrance_Frlg','UndergroundPath_EastWestTunnel_Frlg']:
        d=load(name);d['region']='REGION_HOENN';d['coord_events']=[]
        save(name,d)

    # External Seafoam exits lead to distinct coastal maps: there is no
    # overworld edge joining the two sea halves around the dungeon.
    sea=load('SeafoamIslands_1F_Frlg')
    sea['warp_events'][3].update(dest_map=mid('PlasticOx_Route20West'),dest_warp_id='0')
    sea['warp_events'][4].update(dest_map=mid('PlasticOx_Route20East'),dest_warp_id='0')
    save('SeafoamIslands_1F_Frlg',sea)

    # Select ports once. Pinning coordinates keeps actor/flag edits from moving roads.
    path='plastic_ox/alpha/region_ports.json'
    ports=json.loads(read(path)) if read(path) else {}
    ports={k:v for k,v in ports.items() if not k.startswith(('cherry_route1','route1_route31','ilex_route104',
                                                             'lavender_route8','route8_saffron','route2_rustboro',
                                                             'route24_route25'))}
    reserved={}
    for key,a,at,b,bt,requirements in TRAILS:
        for suffix,name in [('_a',a),('_b',b)]:
            if key+suffix in ports:
                p=ports[key+suffix]
                reserved.setdefault(name,[]).extend([tuple(p['tile']),tuple(p['approach'])])
    records=[]
    scripts=['PoxRegion_TrailHint::\n\tmsgbox PoxRegion_TrailText, MSGBOX_SIGN\n\tend',
             'PoxRegion_TrailText::\n\t.string "Follow the marked trails to the\\nnext town.$"',
             'PoxRegion_ClosedText::\n\t.string "This passage is still closed.\\nReturn after your next objective.$"']
    scripts.append('PoxRustboroNorthSign::\n\tmsgbox PoxRustboroNorthSign_Text, MSGBOX_SIGN\n\tend\nPoxRustboroNorthSign_Text::\n\t.string "ROUTE 24 - NORTH\\nBILL\'S COTTAGE via ROUTE 25$"')
    sign_text = {
        'route7_route103_b': 'ROUTE 7\\nKeep to the marked passage.$',
        'route103_cinnabar_a': 'CINNABAR ISLAND\\nFollow the passage south.$'
    }
    # FRLG trainer IDs aren't part of Emerald's trainer table. Keep these
    # people and their authored dialogue without invoking unrelated trainers.
    for name in ['Route8_Frlg','Route19_Frlg','Route21_North_Frlg','Route21_South_Frlg']:
        d=load(name)
        dialogue_sources=read(f'data/maps/{name}/scripts.inc')
        if name.startswith('Route21_'):
            dialogue_sources+='\n'+read('data/maps/Route21_North_Frlg/scripts.inc')+'\n'+read('data/maps/Route21_South_Frlg/scripts.inc')
        for obj in d['object_events']:
            if '_EventScript_' in obj.get('script',''):
                label=obj['script']
                dialogue=label.replace('_EventScript_','_Text_')+'PostBattle'
                if dialogue+'::' in dialogue_sources:
                    obj['trainer_type']='TRAINER_TYPE_NONE'
                    scripts.append(f'{label}::\n\tmsgbox {dialogue}, MSGBOX_NPC\n\tend')
        save(name,d)
    for floor,item,label in [('1F','ICE_HEAL','IceHeal'),('B1F','WATER_STONE','WaterStone'),('B1F','REVIVE','Revive'),('B2F','BIG_PEARL','BigPearl'),('B4F','ULTRA_BALL','UltraBall')]:
        scripts.append(f'SeafoamIslands_{floor}_EventScript_Item{label}::\n\tfinditem ITEM_{item}\n\tend')
    scripts.append('PoxRegion_RemoveStaticMon::\n\tremoveobject VAR_LAST_TALKED\n\trelease\n\tend\nPoxRegion_MonFlewAway::\n\tremoveobject VAR_LAST_TALKED\n\tmsgbox PoxRegion_MonFlewAwayText, MSGBOX_DEFAULT\n\trelease\n\tend\nPoxRegion_MonFlewAwayText::\n\t.string "The POKéMON flew away!$"')

    # FRLG's hidden-item constants are zero-valued compatibility shims in
    # Emerald. Give these ten retained pickups unique real alpha item flags.
    item_number=46
    header=read('include/constants/plastic_ox_flags.h')
    for name in ['Route8_Frlg','UndergroundPath_EastWestTunnel_Frlg','SeafoamIslands_B3F_Frlg','SeafoamIslands_B4F_Frlg']:
        d=load(name)
        for item in d.get('bg_events',[]):
            if item.get('type')!='hidden_item':
                continue
            flag=f'FLAG_POX_HIDDEN_V7_{item_number}'
            item['flag']=flag
            if f'#define {flag} ' not in header:
                header=header.replace('#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H',f'#define {flag} (POX_HIDDEN_ITEMS_BASE + {item_number})\n#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H')
            item_number+=1
        save(name,d)
    d=load('Route21_North_Frlg')
    for item in d.get('bg_events',[]):
        if item.get('type')=='hidden_item':
            item['flag']='FLAG_POX_HIDDEN_V7_60'
    save('Route21_North_Frlg',d)
    if '#define FLAG_POX_HIDDEN_V7_60 ' not in header:
        header=header.replace('#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H','#define FLAG_POX_HIDDEN_V7_60 0x493\n#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H')
    # Native FRLG flag/var aliases are zero in Emerald. Reserve independent
    # persistent state for the retained boulder puzzle, pickups and Articuno.
    native_flags=['FLAG_STOPPED_SEAFOAM_B3F_CURRENT','FLAG_STOPPED_SEAFOAM_B4F_CURRENT']
    native_flags += [f'FLAG_HIDE_SEAFOAM_{floor}_BOULDER_{i}' for floor,count in [('1F',2),('B1F',2),('B2F',2),('B3F',6),('B4F',2)] for i in range(1,count+1)]
    native_flags += ['FLAG_FOUGHT_ARTICUNO','FLAG_HIDE_ARTICUNO']
    native_flags += [f'FLAG_HIDE_SEAFOAM_ISLANDS_{item}' for item in ['1F_ICE_HEAL','B1F_REVIVE','B1F_WATER_STONE','B2F_BIG_PEARL','B4F_ULTRA_BALL']]
    allocations=list(range(0x03C,0x050))+[0x0E9,0x1AA,0x27E]
    replacements={flag:flag.replace('FLAG_','FLAG_POX_',1) for flag in native_flags}
    for flag,value in zip(native_flags,allocations,strict=True):
        new=replacements[flag]
        if f'#define {new} ' not in header:
            header=header.replace('#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H',f'#define {new} 0x{value:03X}\n#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H')
    replacements['VAR_MAP_SCENE_SEAFOAM_ISLANDS_B4F']='VAR_POX_SEAFOAM_STATE'
    replacements.update(EventScript_RemoveStaticMon='PoxRegion_RemoveStaticMon',EventScript_MonFlewAway='PoxRegion_MonFlewAway')
    if '#define VAR_POX_SEAFOAM_STATE ' not in header:
        header=header.replace('#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H','#define VAR_POX_SEAFOAM_STATE 0x40FD\n#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H')
    def remap(text):
        return re.sub(r'\b(?:'+ '|'.join(replacements)+r')\b',lambda m:replacements[m[0]],text)
    for name in extra_frlg+['Route20_Frlg']:
        for filename in ['map.json','scripts.inc']:
            native_path=f'data/maps/{name}/{filename}'
            put(native_path,remap(read(native_path)))
    put('include/constants/plastic_ox_flags.h',header)

    def port(key,name,target,anchor=None):
        if key in ports:
            g=Geometry(name,load(name))
            component=g.component(anchor or ANCHORS[name],name in WATER)
            if not all(tuple(ports[key][field]) in component and max(ports[key][field]) <= 127 for field in ['tile','approach']):
                # Migrate previously selected native door-behavior tiles;
                # those cause forced exit steps and aren't stable landings.
                del ports[key]
        if key not in ports:
            g=Geometry(name,load(name))
            if isinstance(target,str):
                target={'N':(g.w//2,0),'S':(g.w//2,g.h-1),'W':(0,g.h//2),'E':(g.w-1,g.h//2)}[target]
            ports[key]=g.port(target,anchor or ANCHORS[name],name in WATER,reserved.get(name,[]))
        p=ports[key]
        reserved.setdefault(name,[]).extend([tuple(p['tile']),tuple(p['approach'])])
        return p

    def endpoint(key,name,p,destination,landing,requirements,label):
        script='PoxRegion_'+key
        reserved.setdefault(name,[])
        d=load(name)
        # A portal often represents a visible plaza/road throat rather than a
        # one-cell doorway.  Cover only the immediately adjacent lanes that
        # have the same approach geometry.  The hard width cap keeps a broad
        # walkable plaza from becoming an invisible whole-map teleport, while
        # the occupancy checks protect signs, NPCs, warps, and other portals.
        g=Geometry(name,d)
        water=name in WATER
        dx,dy=DIRECTIONS[p['direction']]
        px,py=-dy,dx
        occupied={(o['x'],o['y']) for o in d.get('object_events',[])}
        occupied |= {(w['x'],w['y']) for w in d.get('warp_events',[])}
        physical_occupied=set(occupied)
        occupied |= set(reserved[name])
        # port() reserves its own canonical pair so another endpoint cannot
        # select it; that reservation must not suppress this endpoint's
        # canonical trigger.
        occupied.discard(tuple(p['tile']))
        occupied.discard(tuple(p['approach']))
        # Return-mouth helper endpoints (for example Underground Path) are
        # intentionally not regional anchors; their approach is the only
        # required component seed.
        component=g.component(ANCHORS.get(name,p['approach']),water)
        trigger_tiles=[]
        lanes=(0,-1,1) if key[:-2] in LANE_PORTALS else (0,)
        # An object/warp on the canonical mouth is an intentional physical
        # gate (Route 44/Mt. Moon and similar blockers). Never route around it
        # through a newly expanded invisible lane.
        canonical_blocked=(tuple(p['tile']) in physical_occupied or
                           tuple(p['approach']) in physical_occupied)
        for lane in lanes:
            tx,ty=p['tile'][0]+px*lane,p['tile'][1]+py*lane
            ax,ay=tx-dx,ty-dy
            if lane != 0 and canonical_blocked:
                continue
            if lane != 0 and ((tx,ty) in occupied or (ax,ay) in occupied):
                continue
            if (tx,ty) not in component or (ax,ay) not in component:
                continue
            if not g.passable(tx,ty,water) or not g.passable(ax,ay,water):
                continue
            trigger_tiles.append((tx,ty))
        # Keep the central lane first for deterministic generated output.
        trigger_tiles.sort(key=lambda t: (abs((t[0]-p['tile'][0])*px+(t[1]-p['tile'][1])*py), t[1], t[0]))
        # Remove stale copies before adding the current geometry-derived set.
        d['coord_events']=[c for c in d.get('coord_events',[]) if c.get('script') != script]
        d['coord_events'] += [dict(type='trigger',x=x,y=y,elevation=0,var='VAR_POX_PORTAL_GATE',var_value=0,script=script)
                              for x,y in trigger_tiles]
        save(name,d)
        body=f'{script}::\n\tlockall\n\tgoto_if_unset FLAG_POX_TRIGGERS_ENABLED, {script}_Open\n'
        for flag in requirements:
            body+=f'\tgoto_if_unset {flag}, {script}_Closed\n'
        body+=f'{script}_Open::\n\twarp {mid(destination)}, {landing[0]}, {landing[1]}\n\twaitstate\n\treleaseall\n\tend\n'
        # Rejection returns to the adjacent approach, never across the gate.
        body+=f'{script}_Closed::\n\tmsgbox PoxRegion_ClosedText, MSGBOX_DEFAULT\n\twarp {mid(name)}, {p["approach"][0]}, {p["approach"][1]}\n\twaitstate\n\treleaseall\n\tend'
        scripts.append(body)
        records.append(dict(id=key,source=name,destination=destination,**p,landing=landing,requires=requirements,label=label))
        # A visible sign next to the approach identifies every authored trail.
        g=Geometry(name,load(name));x,y=p['approach']
        occupied={(o['x'],o['y']) for o in load(name).get('object_events',[])}
        candidates=[] if name in extra_frlg or key[:-2] in SIGNLESS_TRAILS else [(x+dx,y+dy) for dx,dy in DIRECTIONS.values() if g.passable(x+dx,y+dy,False) and (x+dx,y+dy) not in reserved[name] and (x+dx,y+dy) not in occupied and sum(g.passable(x+dx+ddx,y+dy+ddy,False) for ddx,ddy in DIRECTIONS.values())>=3]
        trigger_tiles={(c['x'],c['y']) for c in d['coord_events']}
        candidates=[c for c in candidates if tuple(p['approach']) in g.component(ANCHORS.get(name,p['approach']),name in WATER,occupied | trigger_tiles | {c})]
        if candidates:
            sx,sy=candidates[0];d=load(name)
            d['bg_events']=[b for b in d.get('bg_events',[]) if b.get('script') != script+'_Sign']
            d['bg_events'].append(dict(type='sign',x=sx,y=sy,elevation=0,player_facing_dir='BG_EVENT_PLAYER_FACING_ANY',script=script+'_Sign'))
            d['object_events'].append(dict(graphics_id='OBJ_EVENT_GFX_SIGN',x=sx,y=sy,elevation=0,movement_type='MOVEMENT_TYPE_NONE',movement_range_x=0,movement_range_y=0,trainer_type='TRAINER_TYPE_NONE',trainer_sight_or_berry_tree_id='0',script=script+'_Sign',flag='0'))
            save(name,d)
            text=sign_text.get(key, f'{label[:30]}\\nMarked passage ahead.$')
            scripts.append(f'{script}_Sign::\n\tmsgbox {script}_Text, MSGBOX_SIGN\n\tend\n{script}_Text::\n\t.string "{text}"')

    for key,a,at,b,bt,requirements in TRAILS:
        overrides={('route2_rustboro','Route2_Frlg'):((6,0),(6,5)),
                   ('route110_lavender','Route110'):((17,5),(17,0)),
                   ('route103_cinnabar','Route103'):((75,15),(78,11))}
        pa_target,pa_anchor=overrides.get((key,a),(at,None))
        pa=port(key+'_a',a,pa_target,pa_anchor)
        pb=port(key+'_b',b,bt)
        endpoint(key+'_a',a,pa,b,pb['approach'],requirements,b.replace('_hns','').replace('_Frlg','').replace('PlasticOx_',''))
        # Native ledges plus no reverse transition preserve the downhill return.
        if key!='route45_route46':
            endpoint(key+'_b',b,pb,a,pa['approach'],requirements,a.replace('_hns','').replace('_Frlg','').replace('PlasticOx_',''))

    # A badge-hidden object on the Route 44 portal tile physically blocks the
    # Mt. Moon transition from every adjacent approach while
    # preserving the portal itself for old saves that already have the badge.
    d=load('Route44_hns')
    if not any(o.get('script') == 'PoxRoute44_MtMoonGate' for o in d['object_events']):
        d['object_events'].append(dict(graphics_id='OBJ_EVENT_GFX_HIKER',x=68,y=13,elevation=0,
            movement_type='MOVEMENT_TYPE_FACE_LEFT',movement_range_x=0,movement_range_y=0,
            trainer_type='TRAINER_TYPE_NONE',trainer_sight_or_berry_tree_id='0',
            script='PoxRoute44_MtMoonGate',flag='FLAG_BADGE01_GET'))
    save('Route44_hns',d)

    # PU acquisitions retain their dedicated script implementations while this
    # generator owns stable, reachable placements and physical door routing.
    # Authored trainers and pickups live in the HNS upper cave. Imported FRLG
    # floors supply geometry and encounters, not the incompatible Kanto quest.
    active.update({'MtMoon_1F_Frlg','MtMoon_B1F_Frlg','MtMoon_B2F_Frlg'})
    for name in ['MtMoon_1F_Frlg','MtMoon_B1F_Frlg','MtMoon_B2F_Frlg']:
        d=load(name)
        d['coord_events']=[]
        d['bg_events']=[]
        d['object_events']=[]
        save(name,d)
        put(f'data/maps/{name}/scripts.inc', f'{name}_MapScripts::\n\t.byte 0\n')
    for name, index, script, gfx in [
        ('Route33_hns', 1, 'POX_PU_MailRecipient', 'OBJ_EVENT_GFX_HIKER'),
        ('Route35_hns', 6, 'POX_PU_MailGuard', 'OBJ_EVENT_GFX_MAN_3'),
        ('NationalPark_Normal_hns', 1, 'PlasticOxContest_EventScript_Attendant', 'OBJ_EVENT_GFX_GAMEBOY_KID'),
    ]:
        d=load(name)
        d['object_events'][index].update(script=script,graphics_id=gfx,flag='0',
            trainer_type='TRAINER_TYPE_NONE',movement_type='MOVEMENT_TYPE_FACE_DOWN')
        save(name,d)
    for number, target in [(1,(13,10)),(2,(44,29))]:
        name='MtMoon_Cave_hns'; d=load(name); label=f'POX_PU_MoonStone{number}'
        d['object_events']=[o for o in d['object_events'] if o.get('script') != label]
        g=Geometry(name,d)
        reserved_tiles={(o['x'],o['y']) for o in d['object_events']} | {(c['x'],c['y']) for c in d['coord_events']}
        x,y=min(g.component(ANCHORS[name])-reserved_tiles,key=lambda p:(abs(p[0]-target[0])+abs(p[1]-target[1]),p))
        d['object_events'].append(dict(graphics_id='OBJ_EVENT_GFX_ITEM_BALL',x=x,y=y,elevation=3,
            movement_type='MOVEMENT_TYPE_NONE',movement_range_x=0,movement_range_y=0,
            trainer_type='TRAINER_TYPE_NONE',trainer_sight_or_berry_tree_id='0',script=label,
            flag=f'FLAG_POX_MTMOON_MOON_STONE_{number}'))
        save(name,d)
    d=load('GoldenrodCity_hns')
    d['warp_events']=[w for w in d['warp_events'] if w['dest_map'] != mid('MauvilleCity_GameCorner')]
    corner_warp=len(d['warp_events'])
    d['warp_events'].append(dict(x=21,y=38,elevation=0,dest_map=mid('MauvilleCity_GameCorner'),dest_warp_id='0'))
    save('GoldenrodCity_hns',d)
    # Headbutt populations hang on visible, already-solid trees at the edge of
    # each area's connected walkable component. A facing trigger lets the
    for name, x, y in [('IlexForest_hns',39,7),('Route33_hns',8,17),('Route35_hns',14,4),
                       ('NationalPark_Normal_hns',40,22),('Route36_hns',39,2)]:
        d=load(name)
        d['bg_events']=[b for b in d.get('bg_events',[]) if b.get('script') != 'PlasticOx_EventScript_HeadbuttTree']
        d['bg_events'].append(dict(type='sign',x=x,y=y,elevation=0,
            player_facing_dir='BG_EVENT_PLAYER_FACING_ANY',
            script='PlasticOx_EventScript_HeadbuttTree'))
        save(name,d)
    d=load('MauvilleCity_GameCorner')
    d['object_events'][3]['script']='POX_PU_CoinPrizes'
    for w in d['warp_events']:
        w.update(dest_map=mid('GoldenrodCity_hns'),dest_warp_id=str(corner_warp))
    save('MauvilleCity_GameCorner',d)
    # This native one-tile path is an articulation point between the park
    # arrival and every north-seam tile. One real object closes the route.
    d=load('Route36_hns')
    d['object_events']=[o for o in d['object_events'] if o.get('script') != 'Pox_Sudowoodo']
    d['object_events'].append(dict(graphics_id='OBJ_EVENT_GFX_SUDOWOODO',x=39,y=20,elevation=3,
        movement_type='MOVEMENT_TYPE_NONE',movement_range_x=0,movement_range_y=0,
        trainer_type='TRAINER_TYPE_NONE',trainer_sight_or_berry_tree_id='0',
        script='Pox_Sudowoodo',flag='FLAG_POX_SUDOWOODO_CLEARED'))
    save('Route36_hns',d)
    # Route 44's gate handler and dialogue are authored in its local scripts.

    # HNS Route7 lacks the FRLG tunnel mouth; a marked stair passage uses the
    # existing tunnel entrance room rather than skipping the tunnel.
    p=port('underground_west','Route7_hns',(4,20))
    endpoint('underground_west','Route7_hns',p,'UndergroundPath_WestEntrance_Frlg',[6,6],[], 'Underground Path')
    # Return through the room's three exit tiles using coordinate triggers;
    # remove those native warp events to avoid the absent HNS door index.
    d=load('UndergroundPath_WestEntrance_Frlg')
    for w in d['warp_events'][:3]:
        w.update(dest_map=mid('UndergroundPath_WestEntrance_Frlg'),dest_warp_id='0')
    save('UndergroundPath_WestEntrance_Frlg',d)
    for x in [5,6,7]:
        q={'tile':[x,7],'approach':[x,6],'direction':'S'}
        endpoint('underground_return_'+str(x),'UndergroundPath_WestEntrance_Frlg',q,'Route7_hns',p['approach'],[], 'Route 7')

    # Route 2 retains its native gatehouses, local buildings and cave mouth.
    # Ilex's north threshold uses a dedicated, visually identical north-arrow
    # metatile installed by agent/fix_ilex_north_gate.py. Keep this a native
    # reciprocal door warp rather than an invisible coordinate-script portal.
    south,north=route2_rooms[1],route2_rooms[0]
    d=load('Route2_Frlg')
    d['object_events']=[o for o in d['object_events'] if o.get('type')!='clone']
    d['warp_events'][3].update(dest_map=mid('DarkCave_SouthSide_hns'),dest_warp_id='0')
    for o in d['object_events']:
        if o.get('script')=='Route2_EventScript_ItemEther':
            o.update(script='PoxRoute2_Ether',flag='FLAG_POX_ROUTE2_ETHER')
        if o.get('script')=='Route2_EventScript_ItemParalyzeHeal':
            o.update(script='PoxRoute2_ParalyzeHeal',flag='FLAG_POX_ROUTE2_PARALYZE_HEAL')
    save('Route2_Frlg',d)
    d=load('DarkCave_SouthSide_hns');d['warp_events'][0].update(dest_map=mid('Route2_Frlg'),dest_warp_id='3');save('DarkCave_SouthSide_hns',d)
    d=load(south);d['warp_events'][3].update(dest_map=mid('IlexForest_hns'),dest_warp_id='0');save(south,d)
    d=load(north)
    for w in d['warp_events'][:3]:w.update(dest_map=mid('IlexForest_hns'),dest_warp_id='1')
    save(north,d)
    d=load('IlexForest_hns')
    d['warp_events']=[dict(x=22,y=63,elevation=0,dest_map=mid(south),dest_warp_id='3'),dict(x=20,y=15,elevation=0,dest_map=mid(north),dest_warp_id='1')]
    d['coord_events']=[e for e in d.get('coord_events',[]) if e.get('script') != 'PoxRegion_ilex_route2_north']
    d['object_events']=[e for e in d.get('object_events',[]) if e.get('script') != 'PoxRegion_ilex_route2_north_Sign']
    d['bg_events']=[e for e in d.get('bg_events',[]) if e.get('script') != 'PoxRegion_ilex_route2_north_Sign']
    save('IlexForest_hns',d)
    scripts.extend(['PoxRoute2_Ether::\n\tfinditem ITEM_ETHER\n\tend','PoxRoute2_ParalyzeHeal::\n\tfinditem ITEM_PARALYZE_HEAL\n\tend'])
    # Route 2 and Rustboro share a real north/south camera seam. Before Ilex is
    # complete, a visible ranger occupies the one-tile trail; the normal object
    # flag rule removes him once the objective is complete.
    d=load('Route2_Frlg')
    if not any(o.get('script') == 'PoxRoute2_RustboroGate' for o in d['object_events']):
        d['object_events'].append(dict(graphics_id='OBJ_EVENT_GFX_HIKER',x=8,y=0,elevation=3,
            movement_type='MOVEMENT_TYPE_FACE_DOWN',movement_range_x=0,movement_range_y=0,
            trainer_type='TRAINER_TYPE_NONE',trainer_sight_or_berry_tree_id='0',
            script='PoxRoute2_RustboroGate',flag='FLAG_POX_STORY_ILEX'))
    save('Route2_Frlg',d)
    scripts.append('PoxRoute2_RustboroGate::\n\tmsgbox PoxRoute2_RustboroGate_Text, MSGBOX_NPC\n\tend\n'
                   'PoxRoute2_RustboroGate_Text::\n\t.string "RUSTBORO will have to wait.\\nTake the ILEX FOREST trail first.\\pWatch those roots in the woods.\\nThey nearly tripped me twice!$"')
    # Gatehouse and trade-house actors and scripts are authored in local maps;
    # do not replace the house trade or the gate guards with shared dialogue.
    # The imported HNS trade house has one real animated door at (4, 8), not
    # the three-tile FRLG exit strip. Keep the exterior and interior indices
    # reciprocal so entering and leaving cannot strand the player.
    d=load('Route2_Frlg')
    d['warp_events'][4]['dest_warp_id']='0'
    save('Route2_Frlg',d)
    d=load('Route2_House_Frlg')
    d['warp_events']=[
        dict(x=4,y=7,elevation=0,dest_map=mid('Route2_House_Frlg'),dest_warp_id='0'),
        dict(x=4,y=8,elevation=0,dest_map=mid('Route2_Frlg'),dest_warp_id='4'),
    ]
    save('Route2_House_Frlg',d)
    scripts.append('PoxRoute2_Local::\n\tmsgbox PoxRoute2_LocalText, MSGBOX_NPC\n\tend\nPoxRoute2_LocalText::\n\t.string "I keep losing at this game.\\nThe other kid picks ALAKAZAM!\\pDo you think a real POKéMON\\nbattle would be easier?$"')
    header=read('include/constants/plastic_ox_flags.h')
    for name,index in [('ETHER',58),('PARALYZE_HEAL',59)]:
        flag='FLAG_POX_ROUTE2_'+name
        if '#define '+flag+' ' not in header:
            header=header.replace('#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H',f'#define {flag} (POX_HIDDEN_ITEMS_BASE + {index})\n#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H')
    put('include/constants/plastic_ox_flags.h',header)
    encounters=json.loads(read('src/data/wild_encounters.json'))
    for group in encounters['wild_encounter_groups']:
        for entry in group.get('encounters',[]):
            if entry.get('map')=='MAP_ROUTE31_HNS':
                entry['map']='MAP_ROUTE2'
    put('src/data/wild_encounters.json',json.dumps(encounters,indent=2)+'\n')
    put(path,json.dumps(ports,indent=2)+'\n')
    put('plastic_ox/alpha/region_manifest.json',json.dumps({'version':7,'donor_revision':'44f50eedefe58691b0444973e4138e9190d8fafc','transitions':records,'native_seams':{n:sorted(v) for n,v in keep.items()}},indent=2)+'\n')
    # Native local callbacks remain for puzzles; outdoor story callbacks are
    # replaced by explicit v7 arrival state to prevent source-region quests.
    for name in sorted(active):
        p=f'data/maps/{name}/scripts.inc'
        old=read(p)
        callback='PoxRegion_Arrival_'+name
        header=f'{name}_MapScripts::\n\tmap_script MAP_SCRIPT_ON_TRANSITION, {callback}\n\t.byte 0'
        if name=='CinnabarIsland_Frlg':
            old=header+'\n\nCinnabarIsland_EventScript_IslandSign::\n\tmsgbox CinnabarIsland_Text_IslandSign, MSGBOX_SIGN\n\tend\nCinnabarIsland_Text_IslandSign::\n\t.string "CINNABAR ISLAND\\nThe Fiery Town of Burning Desire$"\n\nCinnabarIsland_EventScript_PokemonLabSign::\n\tmsgbox CinnabarIsland_Text_PokemonLabSign, MSGBOX_SIGN\n\tend\nCinnabarIsland_Text_PokemonLabSign::\n\t.string "POKéMON LAB$"\n\nCinnabarIsland_EventScript_GymSign::\n\tmsgbox CinnabarIsland_Text_GymSign, MSGBOX_SIGN\n\tend\nCinnabarIsland_Text_GymSign::\n\t.string "CINNABAR ISLAND POKéMON GYM$"\n'
        elif old:
            old=re.sub(r'\A.*?\t.byte 0',lambda _:header,old,count=1,flags=re.S)
        else:
            old=header+'\n'
        put(p,old)
        body=callback+'::\n'
        if name=='FortreeCity':
            body+='\tsetflag FLAG_HIDE_FORTREE_CITY_KECLEON\n\tsetflag FLAG_KECLEON_FLED_FORTREE\n\tgoto_if_unset FLAG_POX_TRIGGERS_ENABLED, '+callback+'_Reached\n\tgoto_if_unset FLAG_POX_STORY_WEATHER, '+callback+'_End\n'+callback+'_Reached::\n\tsetflag FLAG_POX_REACHED_FORTREE\n'
        if name=='Route119':
            body+='\tsetflag FLAG_HIDE_ROUTE_119_TEAM_AQUA\n\tsetflag FLAG_HIDE_ROUTE_119_RIVAL\n\tsetflag FLAG_HIDE_ROUTE_119_RIVAL_ON_BIKE\n'
        if name.startswith('PlasticOx_Route20'):
            body+='\tcall_if_unset FLAG_STOPPED_SEAFOAM_B3F_CURRENT, Route20_EventScript_ResetSeafoamBouldersForB3F\n\tcall_if_unset FLAG_STOPPED_SEAFOAM_B4F_CURRENT, Route20_EventScript_ResetSeafoamBouldersForB4F\n'
        body+=callback+'_End::\n\tend'
        scripts.append(body)
    put('data/scripts/plastic_ox_region.inc',remap('@ Generated by plastic_ox/alpha/region_v7.py\n\n'+'\n\n'.join(scripts)+'\n'))
    s=read('data/event_scripts.s')
    marker='@ Plastic Ox v7 FRLG modules (Emerald inclusion).'
    if marker not in s:
        s+='\n'+marker+'\n.if !IS_FRLG\n'+''.join(f'\t.include "data/maps/{n}/scripts.inc"\n' for n in ['Route1_Frlg','Route8_Frlg','Route19_Frlg','Route20_Frlg','Route21_North_Frlg','Route21_South_Frlg','CinnabarIsland_Frlg']+extra_frlg)+'.endif\n'
    s=s.replace('.if GAME_VERSION == VERSION_EMERALD','.if !IS_FRLG')
    mansion_common='.if !IS_FRLG\n\t.include "data/scripts/pokemon_mansion.inc"\n.endif\n'
    if mansion_common not in s:
        s+='\n'+mansion_common
    for name in ['Route2_Frlg','Route21_North_Frlg','Route21_South_Frlg','CinnabarIsland_Frlg']+story_frlg+route2_rooms:
        line=f'\t.include "data/maps/{name}/scripts.inc"\n'
        if line not in s[s.index(marker):]:
            s+='\n.if !IS_FRLG\n'+line+'.endif\n'
    for p in ['data/scripts/plastic_ox_region.inc','data/maps/PlasticOx_Harbor/scripts.inc','data/maps/PlasticOx_Route20West/scripts.inc','data/maps/PlasticOx_Route20East/scripts.inc']:
        line=f'\t.include "{p}"\n'
        if line not in s:
            s+=line
    put('data/event_scripts.s',s)
    from trees import install as install_fruit_trees
    install_fruit_trees()
