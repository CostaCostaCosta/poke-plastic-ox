"""Canonical cave-free endgame overlay; applied after the v7 region generator.

Binary geometry is the northern 51 rows of HNS Route26 (see league/README.md).
Only this module's maps, scripts, encounters and party blocks are replaced.
"""
import json
import re
import textwrap
from pathlib import Path

BASE = Path(__file__).with_suffix('')
MEMBERS = ['Wallace', 'Steven', 'LeagueLance', 'Blue', 'Bill']
FLAGS = ['FLAG_POX_LEAGUE_' + n.upper() for n in MEMBERS]
BADGES = [f'FLAG_BADGE{i:02}_GET' for i in range(1, 9)]


def install(read, put):
    def load(n): return json.loads(read(f'data/maps/{n}/map.json'))
    def save(n, d): put(f'data/maps/{n}/map.json', json.dumps(d, indent=2)+'\n')
    def obj(s, x, y, gfx='MAN_3', flag='0', **kw):
        return dict(graphics_id='OBJ_EVENT_GFX_'+gfx, x=x, y=y, elevation=0,
                    movement_type='MOVEMENT_TYPE_FACE_DOWN', movement_range_x=0,
                    movement_range_y=0, trainer_type='TRAINER_TYPE_NONE',
                    trainer_sight_or_berry_tree_id='0', script='PoxLeague_'+s, flag=flag, **kw)
    def trigger(s,x,y):
        return dict(type='trigger',x=x,y=y,elevation=0,var='VAR_TEMP_0',var_value=0,script='PoxLeague_'+s)
    def warp(x,y,dest,index):
        return dict(x=x,y=y,elevation=0,dest_map=dest,dest_warp_id=str(index))
    scripts = []
    def emit(s): scripts.append(s)
    def text(n,s):
        pages=[]
        # One textbox page per paragraph; longer paragraphs scroll (\l)
        # rather than breaking the page mid-sentence.
        for paragraph in s.split('|'):
            lines=textwrap.wrap(paragraph,32)
            pages.append(''.join(l if i==0 else ('\\n' if i==1 else '\\l')+l for i,l in enumerate(lines)))
        emit(f'PoxLeague_Text_{n}::\n\t.string "'+ '\\p'.join(pages)+'$"')
    def checks(flags,target='Denied'):
        return ''.join(f'\tgoto_if_unset {f}, PoxLeague_{target}\n' for f in flags)
    def talk(n,s,cleared=None):
        # cleared: what the speaker says once FLAG_SYS_GAME_CLEAR is set.
        branch=f'\tgoto_if_set FLAG_SYS_GAME_CLEAR, PoxLeague_{n}Cleared\n' if cleared else ''
        emit(f'PoxLeague_{n}::\n\tlock\n\tfaceplayer\n{branch}\tmsgbox PoxLeague_Text_{n}, MSGBOX_DEFAULT\n\trelease\n\tend')
        text(n,s)
        if cleared:
            emit(f'PoxLeague_{n}Cleared::\n\tmsgbox PoxLeague_Text_{n}Cleared, MSGBOX_DEFAULT\n\trelease\n\tend')
            text(n+'Cleared',cleared)
    def portal(n,dest,x,y,flags=()):
        emit(f'PoxLeague_{n}::\n\tlockall\n'+checks(flags, 'GateDenied' if n=='Checkpoint' else 'Denied')+f'\twarp {dest}, {x}, {y}\n\twaitstate\n\treleaseall\n\tend')

    # Eight-badge checkpoint covers the entire existing western gate throat.
    city=load('EcruteakCity_hns')
    city['coord_events']=[e for e in city['coord_events'] if 'ecruteak_league' not in e.get('script','') and not e.get('script','').startswith('PoxLeague_')]
    city['coord_events'] += [trigger('Checkpoint',8,y) for y in range(34,38)]
    for field in ['object_events','bg_events']:
        city[field]=[e for e in city[field] if 'ecruteak_league' not in e.get('script','') and not e.get('script','').startswith('PoxLeague_')]
    city['object_events'].append(obj('GateGuide',11,34,'BLACK_BELT'))
    city['warp_events']=[w for w in city['warp_events'] if not (w['x']==8 and 34<=w['y']<=37)]
    save('EcruteakCity_hns',city)
    portal('Checkpoint','MAP_PLASTIC_OX_VICTORY_ROAD',27,48,BADGES)
    talk('GateGuide','Eight BADGES. That is the whole list, and the gate counts them, not me.|Beyond this gate is VICTORY ROAD. Then INDIGO PLATEAU.|No field moves, no shortcuts. The road is the test.')
    emit('PoxLeague_Denied::\n\tmsgbox PoxLeague_Text_Denied, MSGBOX_DEFAULT\n\treleaseall\n\tend')
    emit('PoxLeague_GateDenied::\n\tmsgbox PoxLeague_Text_Denied, MSGBOX_DEFAULT\n\tapplymovement LOCALID_PLAYER, Common_Movement_WalkRight\n\twaitmovement 0\n\treleaseall\n\tend')
    text('Denied','The gate is not open to you yet. Eight BADGES. The list is on the wall if you want to count them.')

    route=load('PlasticOx_VictoryRoad')
    route.update(layout='LAYOUT_PLASTIC_OX_VICTORY_ROAD',map_type='MAP_TYPE_ROUTE',music='MUS_RG_VICTORY_ROAD',allow_running=True,allow_cycling=True,allow_escaping=False,show_map_name=True,region_map_section='MAPSEC_VICTORY_ROAD',connections=[],warp_events=[],object_events=[],coord_events=[],bg_events=[])
    # Keep arrivals one step off their portal, avoiding immediate return loops.
    route['coord_events'] += [trigger('Return',x,50) for x in range(25,29)]
    route['coord_events'] += [trigger('Summit',x,1) for x in range(13,16)]
    portal('Return',city['id'],9,35)
    portal('Summit','MAP_INDIGO_PLATEAU_HNS',12,18,BADGES)
    trainers=[('VICTORYROAD','ACE',26,43,'FACE_LEFT',2),('RIDGE_RAIN','MARINA',24,33,'FACE_RIGHT',4),('RIDGE_SAND','DARIUS',26,25,'FACE_LEFT',2),('RIDGE_STALL','HELEN',9,26,'FACE_RIGHT',0),('RIDGE_OFFENSE','REX',22,13,'FACE_LEFT',2),('RIDGE_BALANCE','SAGE',13,5,'FACE_RIGHT',2)]
    # Each ridge trainer keeps their own defeat and after-battle lines.
    ROUTE_DEFEAT={'VICTORYROAD':'Fair enough. You would have walked past me anyway.','RIDGE_RAIN':'The storm passed you right by.','RIDGE_SAND':'Not a single careless switch. Impressive.','RIDGE_STALL':'You found a purpose for every turn, too.','RIDGE_OFFENSE':'My sweeper never got its free turn!','RIDGE_BALANCE':'You found it. My weakness was you.'}
    ROUTE_AFTER={'VICTORYROAD':'We got here early, liked the wind, and stayed. Five more of us up the ridge. None of them will go easy on you.',
                 'RIDGE_RAIN':'It rains on this side most afternoons. If your team only works in the sun, take the terraces and think about it.',
                 'RIDGE_SAND':'You never switched into a hit you did not need to take. That is the whole lesson. I just add sand.',
                 'RIDGE_STALL':'Nobody learns anything from a straight line. The long way up shows you what your team does when it is tired.',
                 'RIDGE_OFFENSE':'Past here the wind comes off the west side hard. It will not touch your battles, but hold on to your hat.',
                 'RIDGE_BALANCE':'Past me it is a door, a lobby, and five TRAINERS better than me. Try to arrive with something left.'}
    intros=['Six of us train up here, and not one works for the LEAGUE. I am the welcome. Show me your team!', 'Rain changes the pace. Can you change with it?', 'Sand wears down every careless switch.', 'You came up the quiet side. Good. A patient defense gives every turn a purpose.', 'One free turn is all a sweeper needs.', 'Every team has a weakness. Can you find mine?']
    for (tid,name,x,y,direction,sight),intro in zip(trainers,intros):
        o=obj(tid,x,y,'COOLTRAINER_F' if name in ['MARINA','HELEN'] else 'COOLTRAINER_M')
        o.update(trainer_type='TRAINER_TYPE_NORMAL',trainer_sight_or_berry_tree_id=str(sight),movement_type='MOVEMENT_TYPE_'+direction)
        route['object_events'].append(o)
        emit(f'PoxLeague_{tid}::\n\ttrainerbattle_single TRAINER_PLASTIC_OX_{tid}, PoxLeague_Text_{tid}, PoxLeague_Text_{tid}Defeat\n\tmsgbox PoxLeague_Text_{tid}After, MSGBOX_AUTOCLOSE\n\tend')
        text(tid,intro)
        text(tid+'Defeat',ROUTE_DEFEAT[tid])
        text(tid+'After',ROUTE_AFTER[tid])
    # Optional side trail rewards, persistent and bag-full safe.
    for i,(x,y,item) in enumerate([(9,34,'LEFTOVERS'),(15,28,'MAX_ELIXIR'),(20,11,'RARE_CANDY')]):
        flag=f'FLAG_POX_LEAGUE_REWARD_{i}'
        route['object_events'].append(obj(f'Item{i}',x,y,'ITEM_BALL',flag))
        emit(f'PoxLeague_Item{i}::\n\tlock\n\tfinditem ITEM_{item}\n\trelease\n\tend')
    talk('TrailSign','VICTORY ROAD|North: INDIGO PLATEAU. South: ECRUTEAK checkpoint.|The western terraces are optional. The eastern ridge is the direct climb.')
    route['object_events'].append(obj('TrailSign',28,47,'SIGN'))
    # Retain the two native Route 26 houses as optional, working rest stops.
    for i,(x,y) in enumerate([(24,11),(9,31)]):
        name='PlasticOx_LeagueRestHouse'+str(i+1)
        house=load('House_GenericA_hns')
        house.update(id='MAP_PLASTIC_OX_LEAGUE_REST_HOUSE'+str(i+1),name=name,
                     region='REGION_HOENN',region_map_section='MAPSEC_VICTORY_ROAD',
                     connections=[],coord_events=[],bg_events=[],
                     object_events=[obj('RestKeeper' if i else 'RestAdvice',4,4,'WOMAN_3')],
                     # (4,8) is the house's south-arrow carpet; row 9 has no warp tile.
                     warp_events=[warp(4,8,route['id'],i)])
        save(name,house)
        put(f'data/maps/{name}/scripts.inc',name+'_MapScripts::\n\t.byte 0\n')
        route['warp_events'].append(warp(x,y,house['id'],0))
    emit('PoxLeague_RestKeeper::\n\tlock\n\tfaceplayer\n\tcall Common_EventScript_OutOfCenterPartyHeal\n\tmsgbox PoxLeague_Text_RestKeeper, MSGBOX_DEFAULT\n\trelease\n\tend')
    text('RestKeeper','Boots off. There is a bench, there is tea, and there is no hurry.|The mountain is not going anywhere, and neither is the LEAGUE.')
    talk('RestAdvice','No beds here, sorry. The rest hut with the kettle is down on the western terraces.|One thing before the summit: a team that switches freely controls the battle, and hazards make every switch cost something.')
    save('PlasticOx_VictoryRoad',route)
    put('data/maps/PlasticOx_VictoryRoad/scripts.inc','PlasticOx_VictoryRoad_MapScripts::\n\t.byte 0\n')

    plateau=load('IndigoPlateau_hns')
    for field in ['object_events','coord_events','bg_events']:
        plateau[field]=[e for e in plateau[field] if 'victory_indigo' not in e.get('script','') and not e.get('script','').startswith('PoxLeague_')]
    plateau['coord_events'] += [trigger('Downhill',x,19) for x in range(10,15)]
    plateau['object_events'].append(obj('Shortcut',15,9,'WOMAN_3'))
    save('IndigoPlateau_hns',plateau)
    portal('Downhill',route['id'],14,2)
    emit('PoxLeague_Shortcut::\n\tlock\n\tfaceplayer\n\tmsgbox PoxLeague_Text_Shortcut, MSGBOX_YESNO\n\tgoto_if_eq VAR_RESULT, NO, PoxLeague_Release\n\twarp MAP_ECRUTEAK_CITY_HNS, 9, 35\n\twaitstate\n\trelease\n\tend')
    text('Shortcut','Downhill express to ECRUTEAK. Last descent is at dark, and the wind is picking up from the west.|Walk off the south edge instead and you are back on VICTORY ROAD, on foot.|Want a ride down?')

    lobby=load('IndigoPlateau_PokemonCenter_hns')
    lobby['object_events']=[obj('Nurse',19,10,'NURSE',local_id='LOCALID_POX_LEAGUE_NURSE'),obj('Shop',10,10,'MART_EMPLOYEE'),obj('Entry',32,3,'BLACK_BELT'),obj('Advice',29,10,'COOLTRAINER_M'),obj('Welcome',7,15,'WOMAN_3')]
    lobby['warp_events']=[warp(19,16,plateau['id'],0)]
    lobby['coord_events']=[trigger('Entry',x,2) for x in range(30,34)]
    save('IndigoPlateau_PokemonCenter_hns',lobby)
    reset=''.join(f'\tclearflag {f}\n\tcleartrainerflag TRAINER_PLASTIC_OX_{n.upper()}\n' for n,f in zip(MEMBERS,FLAGS))
    emit('PoxLeague_Reset::\n'+reset+'\treturn')
    emit('PoxLeague_LobbyLoad::\n\tsetrespawn HEAL_LOCATION_POX_INDIGO\n\tcall PoxLeague_Reset\n\tend')
    put('data/maps/IndigoPlateau_PokemonCenter_hns/scripts.inc','IndigoPlateau_PokemonCenter_hns_MapScripts::\n\tmap_script MAP_SCRIPT_ON_TRANSITION, PoxLeague_LobbyLoad\n\t.byte 0\n')
    emit('PoxLeague_Nurse::\n\tlock\n\tfaceplayer\n\tsetrespawn HEAL_LOCATION_POX_INDIGO\n\tcall Common_EventScript_OutOfCenterPartyHeal\n\tmsgbox PoxLeague_Text_Nurse, MSGBOX_DEFAULT\n\trelease\n\tend')
    text('Nurse','Your team is fully rested. I have patched up everyone in this queue today. Good luck in there.')
    emit('PoxLeague_Shop::\n\tlock\n\tfaceplayer\n\tmessage gText_HowMayIServeYou\n\twaitmessage\n\tpokemart PoxLeague_Stock\n\tmsgbox gText_PleaseComeAgain, MSGBOX_DEFAULT\n\trelease\n\tend\n\t.align 2\nPoxLeague_Stock:\n\t.2byte ITEM_FULL_RESTORE\n\t.2byte ITEM_MAX_POTION\n\t.2byte ITEM_HYPER_POTION\n\t.2byte ITEM_REVIVE\n\t.2byte ITEM_FULL_HEAL\n\t.2byte ITEM_ETHER\n\t.2byte ITEM_MAX_REPEL\n\t.2byte ITEM_ULTRA_BALL\n\t.2byte ITEM_NONE')
    talk('Advice','WALLACE keeps a tempo. STEVEN keeps cover. LANCE commits. BLUE watches you do all of it.|Four examiners, four questions. Nobody out here has seen the room after that.','I lost to WALLACE again. Still. I have the lobby chair warmed up for you whenever you want another run.')
    talk('Welcome','The PC is beside the healing counter, and the shop is on the left. The official in the northeast signs you in.|Bag items work between matches. Inside, the doors only open forward, and a loss starts the challenge again from here.','We are closing up soon, CHAMPION. You know the rules by now; the official will sign you in again if you want.')
    emit('PoxLeague_Entry::\n\tlockall\n'+checks(BADGES)+'\tgoto_if_set FLAG_SYS_GAME_CLEAR, PoxLeague_EntryCleared\n\tmsgbox PoxLeague_Text_Entry, MSGBOX_YESNO\nPoxLeague_EntryAnswer::\n\tgoto_if_eq VAR_RESULT, NO, PoxLeague_Release\n\tsetrespawn HEAL_LOCATION_POX_INDIGO\n\tcall PoxLeague_Reset\n\twarp MAP_PLASTIC_OX_WALLACE_ROOM, 6, 11\n\twaitstate\n\treleaseall\n\tend')
    text('Entry','Eight BADGES verified. Four matches, then the CHAMPION. Your bag goes in with you; nothing else does.|If you fall, the book opens again and we start from the top. That is the rule, not a punishment.|Shall I sign you in?')
    emit('PoxLeague_EntryCleared::\n\tmsgbox PoxLeague_Text_EntryCleared, MSGBOX_YESNO\n\tgoto PoxLeague_EntryAnswer')
    text('EntryCleared','Your name is already in the HALL book. The challenge still runs in full: four matches, then the CHAMPION.|Shall I sign you in again?')
    emit('PoxLeague_Release::\n\treleaseall\n\tend')

    speeches=[
        'WALLACE: A battle has a beat. I will keep it, and you will have to break it.',
        'STEVEN: Six strong POKéMON are not a team until each one covers the others.|I will keep my cover up. Find the turn where I have to step out from behind it.',
        'LANCE: I will not talk long. When the opening comes, commit to it. So will I.',
        'BLUE: STEVEN kept his wall up. LANCE never let you breathe. I watched both.|I am going to do neither, and you will have to notice which. Let\'s go!',
        'CHAMPION BILL would like to battle.'
    ]
    E4_AFTER = {
        'Wallace': 'WALLACE: The next room is yours. Let your team catch its breath first.',
        'Steven': 'STEVEN: Go on. The door ahead opened the moment you won.',
        'LeagueLance': 'LANCE: One room left before the CHAMPION. Steady yourself.',
        'Blue': 'BLUE: Go on, the CHAMPION is waiting. Don\'t make me regret losing.',
    }
    DEFEAT_LINES = {
        'Wallace': 'WALLACE: You found the rhythm before I did. It is yours now.',
        'Steven': 'STEVEN: You covered every seam. I could not find the gap.',
        'LeagueLance': 'LANCE: You committed first. That was the whole difference.',
        'Blue': "BLUE: I adapted. You still won. I'll remember that.",
        'Bill': "BILL: ...Ha. That's it, then. You won, fair and square.",
    }
    for i,n in enumerate(MEMBERS):
        room=load('PlasticOx_'+n+'Room')
        room['object_events']=[obj(n,6,5,'LANCE' if n=='LeagueLance' else n.upper())]
        room['coord_events']=[];room['bg_events']=[];room['connections']=[]
        room['allow_running']=True
        room['warp_events']=[] if i==4 else [warp(6,2,load('PlasticOx_'+MEMBERS[i+1]+'Room')['id'],0)]
        # Destination warp 0 is not used for room landings: the open door has a
        # coordinate script so rooms can retain their original, stable map IDs.
        room['warp_events']=[]
        room['coord_events']=[trigger(n+'Next',6,2)] if i<4 else []
        save('PlasticOx_'+n+'Room',room)
        put(f'data/maps/PlasticOx_{n}Room/scripts.inc',f'PlasticOx_{n}Room_MapScripts::\n\tmap_script MAP_SCRIPT_ON_LOAD, PoxLeague_{n}Load\n\t.byte 0\n')
        emit(f'PoxLeague_{n}Load::\n\tcall PokemonLeague_EliteFour_EventScript_CloseDoor\n\tcall_if_set {FLAGS[i]}, PoxLeague_{n}Open\n\tend')
        champion='Champion' if i==4 else ''
        emit(f'PoxLeague_{n}Open::\n\tsetmetatile 6, 1, METATILE_EliteFour_OpenDoor{champion}_Frame, FALSE\n\tsetmetatile 6, 2, METATILE_EliteFour_OpenDoor{champion}_Opening, FALSE\n\treturn')
        prereq=BADGES+FLAGS[:i]
        emit(f'PoxLeague_{n}::\n\tlock\n\tfaceplayer\n'+checks(prereq)+f'\tgoto_if_set {FLAGS[i]}, PoxLeague_{n}After\n\tplaybgm '+('MUS_ENCOUNTER_CHAMPION' if i==4 else 'MUS_ENCOUNTER_ELITE_FOUR')+f', FALSE\n\tmsgbox PoxLeague_Text_{n}, MSGBOX_DEFAULT\n\ttrainerbattle_no_intro TRAINER_PLASTIC_OX_{n.upper()}, PoxLeague_Text_{n}Defeat\nPoxLeague_{n}Won::\n\tsetflag {FLAGS[i]}\n\tcall PoxLeague_{n}Open\n\tspecial DrawWholeMapView\nPoxLeague_{n}After::\n'+('\tgoto_if_set FLAG_SYS_GAME_CLEAR, PoxLeague_BillAgain\n' if i==4 else '')+f'\tmsgbox PoxLeague_Text_{n}After, MSGBOX_DEFAULT\n'+('PoxLeague_BillToHall::\n' if i==4 else '')+ ('\twarp MAP_PLASTIC_OX_HALL_OF_FAME, 7, 12\n\twaitstate\n' if i==4 else '')+'\treleaseall\n\tend')
        text(n,speeches[i]);text(n+'Defeat',DEFEAT_LINES.get(n,'That was a battle to remember!'))
        text(n+'After',E4_AFTER.get(n,'The next room is yours. Take a moment to prepare.') if i<4 else 'BILL: I owe you an explanation. I built the foundations of the transfer network, and the tools that learn from battles.|The system was meant to improve training conditions. Then it began moving ground I never touched. I never asked for that, but I made it possible.|I thought better predictions would make me a better TRAINER. You learned from places, people, and your POKéMON instead.|That journey is yours. Come on, CHAMPION. Let us put it on record.')
        if i<4: portal(n+'Next',load('PlasticOx_'+MEMBERS[i+1]+'Room')['id'],6,11,prereq+[FLAGS[i]])

    # A rematch win skips the confession; the player has already heard it.
    emit('PoxLeague_BillAgain::\n\tmsgbox PoxLeague_Text_BillAgain, MSGBOX_DEFAULT\n\tgoto PoxLeague_BillToHall')
    text('BillAgain',"BILL: You again, and my team on the floor again. I should be taking notes. Come on, the HALL is this way.")

    hof=load('EverGrandeCity_HallOfFame')
    hof.update(id='MAP_PLASTIC_OX_HALL_OF_FAME',name='PlasticOx_HallOfFame',region_map_section='MAPSEC_INDIGO_PLATEAU',object_events=[obj('HallGuide',6,7,'MAN_3')],warp_events=[],coord_events=[],bg_events=[])
    save('PlasticOx_HallOfFame',hof)
    put('data/maps/PlasticOx_HallOfFame/scripts.inc','PlasticOx_HallOfFame_MapScripts::\n\tmap_script MAP_SCRIPT_ON_FRAME_TABLE, PoxLeague_HallTable\n\t.byte 0\nPoxLeague_HallTable::\n\tmap_script_2 VAR_TEMP_1, 0, PoxLeague_Hall\n\t.2byte 0\n')
    emit('PoxLeague_Hall::\n\tlockall\n'+checks(BADGES+FLAGS)+'\tsetvar VAR_TEMP_1, 1\n\tclearflag FLAG_POX_RED_RESTING\n\tapplymovement LOCALID_PLAYER, Common_Movement_WalkUp4\n\twaitmovement 0\n\tmsgbox PoxLeague_Text_Hall, MSGBOX_DEFAULT\n\tclosemessage\n\tdofieldeffect FLDEFF_HALL_OF_FAME_RECORD\n\twaitfieldeffect FLDEFF_HALL_OF_FAME_RECORD\n\tsetrespawn HEAL_LOCATION_POX_INDIGO\n\tfadescreenspeed FADE_TO_BLACK, 24\n\tspecial GameClear\n\tend')
    talk('HallGuide','I write the names exactly as they stand. No titles, no speeches. That is the whole ceremony.')
    text('Hall','REGISTRAR: Every POKéMON beside you goes into the book exactly as it stands today.|Welcome to the HALL OF FAME, CHAMPION. The ferry south of LAVENDER will take you on from here.')

    groups=json.loads(read('data/maps/map_groups.json'))
    for name in ['PlasticOx_HallOfFame','PlasticOx_LeagueRestHouse1','PlasticOx_LeagueRestHouse2']:
        if name not in groups['gMapGroup_PlasticOxStory']: groups['gMapGroup_PlasticOxStory'].append(name)
    put('data/maps/map_groups.json',json.dumps(groups,indent=2)+'\n')
    put('data/scripts/plastic_ox_league.inc','@ Generated by plastic_ox/alpha/league.py\n\n'+'\n\n'.join(scripts)+'\n')
    path='data/event_scripts.s'; s=read(path)
    for p in ['data/scripts/plastic_ox_league.inc','data/maps/PlasticOx_HallOfFame/scripts.inc','data/maps/PlasticOx_LeagueRestHouse1/scripts.inc','data/maps/PlasticOx_LeagueRestHouse2/scripts.inc']:
        line=f'\t.include "{p}"\n'
        if line not in s: s+=line
    put(path,s)
    # Remove obsolete cave portals and legacy shortcuts (including callable
    # prototype scripts) so old saves cannot bypass the ordered challenge.
    for n in ['VictoryRoad_1F']:
        d=load(n)
        for field in ['coord_events','object_events','bg_events']:
            d[field]=[e for e in d[field] if not any(t in e.get('script','') for t in ['ecruteak_league','victory_indigo'])]
        save(n,d)
    p='data/scripts/plastic_ox_region.inc'; s=read(p)
    for old,new in [('ecruteak_league_a','Checkpoint'),('ecruteak_league_b','Return'),('victory_indigo_a','Summit'),('victory_indigo_b','Downhill')]:
        s=re.sub(r'^PoxRegion_'+old+r'::\n.*?(?=^\w+::|\Z)', 'PoxRegion_'+old+'::\n\tgoto PoxLeague_'+new+'\n\n',s,flags=re.S|re.M)
    put(p,s)
    p='data/scripts/plastic_ox_story.inc'; s=read(p)
    for n in MEMBERS:
        for suffix,target in [('',n),('_Won',n),('Advance',n+'Next' if n!='Bill' else 'Bill')]:
            label='Pox_'+n+suffix
            s=re.sub(r'^'+label+r'::\n.*?(?=^\w+::|\Z)',label+'::\n\tgoto PoxLeague_'+target+'\n\n',s,flags=re.S|re.M)
    s=re.sub(r'^Pox_LeagueEntry::\n.*?(?=^\w+::|\Z)','Pox_LeagueEntry::\n\tgoto PoxLeague_Entry\n\n',s,flags=re.S|re.M)
    put(p,s)
    p='plastic_ox/alpha/region_manifest.json';d=json.loads(read(p))
    updates={
        'ecruteak_league_a':('EcruteakCity_hns','PlasticOx_VictoryRoad',[8,34],[9,34],'W',[27,48],BADGES),
        'ecruteak_league_b':('PlasticOx_VictoryRoad','EcruteakCity_hns',[27,49],[27,48],'S',[9,35],[]),
        'victory_indigo_a':('PlasticOx_VictoryRoad','IndigoPlateau_hns',[14,1],[14,2],'N',[12,18],BADGES),
        'victory_indigo_b':('IndigoPlateau_hns','PlasticOx_VictoryRoad',[12,19],[12,18],'S',[14,2],[]),
    }
    for e in d['transitions']:
        if e['id'] in updates:
            source,destination,tile,approach,direction,landing,requires=updates[e['id']]
            e.update(source=source,destination=destination,tile=tile,approach=approach,direction=direction,landing=landing,requires=requires,label='Victory Road' if destination=='PlasticOx_VictoryRoad' else destination)
    put(p,json.dumps(d,indent=2)+'\n')
    # Route pickups use the extended SaveBlock3 range after the intro flag.
    p='include/constants/plastic_ox_flags.h';s=read(p)
    for i in range(3):
        if f'#define FLAG_POX_LEAGUE_REWARD_{i} ' not in s:
            s=s.replace('#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H',f'#define FLAG_POX_LEAGUE_REWARD_{i} 0x{0xB15+i:X}\n#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H')
    s=re.sub(r'(#define FLAG_POX_LEAGUE_REWARD_)([0-2]) [^\n]+', lambda m:m[1]+m[2]+' (POX_EVENT_FLAGS_START + '+str(21+int(m[2]))+')',s)
    put(p,s)
    p='src/data/heal_locations.json';d=json.loads(read(p))
    d['heal_locations']=[h for h in d['heal_locations'] if h['id']!='HEAL_LOCATION_POX_INDIGO']
    d['heal_locations'].append(dict(id='HEAL_LOCATION_POX_INDIGO',map=plateau['id'],x=11,y=7,respawn_map=lobby['id'],respawn_npc='LOCALID_POX_LEAGUE_NURSE',respawn_x=19,respawn_y=12))
    put(p,json.dumps(d,indent=2)+'\n')
    p='src/data/trainers.party';s=read(p)
    authored=(BASE/'trainers.party').read_text()
    for block in re.split(r'(?=^=== )',authored,flags=re.M):
        if not block.strip(): continue
        tid=re.match(r'=== (\w+) ===',block)[1]
        pattern=r'^=== '+tid+r' ===\n.*?(?=^=== |\Z)'
        if re.search(pattern,s,flags=re.S|re.M):
            s=re.sub(pattern,lambda _:block.strip()+'\n\n',s,flags=re.S|re.M)
        else: s=s.rstrip()+'\n\n'+block.strip()+'\n'
    put(p,s.rstrip()+'\n')
    p='include/constants/opponents.h';s=read(p)
    for i,(tid,*_) in enumerate(trainers[1:]):
        if f'#define TRAINER_PLASTIC_OX_{tid} ' not in s:
            s=s.replace('// End Plastic Ox story trainers.',f'#define TRAINER_PLASTIC_OX_{tid} {940+i}\n// End Plastic Ox story trainers.')
    for c in ['TRAINERS_COUNT_EMERALD','MAX_TRAINERS_COUNT_EMERALD']:
        s=re.sub(r'(#define '+c+r'\s+)(\d+)',lambda m:m[1]+str(max(945,int(m[2]))),s)
    put(p,s)
    p='src/data/wild_encounters.json';d=json.loads(read(p)); encounters=d['wild_encounter_groups'][0]['encounters']
    encounters[:]=[e for e in encounters if e['map']!=route['id']]
    species=['DODRIO','SANDSLASH','TAUROS','DONPHAN','SKARMORY','HERACROSS','MEDICHAM','BRELOOM','GIRAFARIG','DITTO','BAGON','BELDUM']
    encounters.append(dict(map=route['id'],base_label='gPoxVictoryRoadOutdoor',land_mons=dict(encounter_rate=12,mons=[dict(min_level=52,max_level=56,species='SPECIES_'+sp) for sp in species])))
    put(p,json.dumps(d,indent=2)+'\n')


if __name__=='__main__':
    install(lambda p:Path(p).read_text(),lambda p,s:(Path(p).parent.mkdir(parents=True,exist_ok=True),Path(p).write_text(s)))
