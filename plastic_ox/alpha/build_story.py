#!/usr/bin/env python3
"""Emit an apply_patch patch for the alpha story's declarative map/script sources.

Run from the repository root. This tool never writes files itself. --check
checks that the checked-in sources match the story manifest below.
Existing layouts are reused, not copied or converted. See STORY_IMPLEMENTATION.md.
"""
import copy
import difflib
import json
from pathlib import Path
import re
import struct
import sys
import textwrap

changes = {}


def read(path):
    return changes.get(path, Path(path).read_text() if Path(path).exists() else "")


def put(path, text):
    changes[path] = text


def load_map(name):
    return json.loads(read(f"data/maps/{name}/map.json"))


def save_map(name, data):
    put(f"data/maps/{name}/map.json", json.dumps(data, indent=2) + "\n")


scripts = []
flags = []
trainers = []
manifest = []
layouts = {l['id']: l for l in json.loads(Path('data/layouts/layouts.json').read_text())['layouts']}


def floor_cell(mapname, x, y, exclude=None):
    """Choose the nearest unoccupied walkable source tile, never a door warp."""
    data = load_map(mapname)
    layout = layouts[data['layout']]
    blocks = struct.unpack('<'+'H'*(layout['width']*layout['height']), Path(layout['blockdata_filepath']).read_bytes())
    occupied = {(o['x'],o['y']) for o in data['object_events'] if o['script'] != exclude}
    occupied |= {(w['x'],w['y']) for w in data['warp_events']}
    cells = [(i%layout['width'],i//layout['width']) for i,b in enumerate(blocks) if not b&0xC00]
    cells = [c for c in cells if c not in occupied]
    return min(cells,key=lambda c:(abs(c[0]-x)+abs(c[1]-y),abs(c[0]-x),c[1],c[0]))


def flag(name):
    name = "FLAG_POX_" + name
    if name not in flags:
        flags.append(name)
    return name


def emit(text):
    scripts.append(text.strip() + "\n")


def speech(name, text):
    pages = []
    for paragraph in text.split("|"):
        lines = textwrap.wrap(paragraph, 32)
        pages.extend("\\n".join(lines[i:i+2]) for i in range(0, len(lines), 2))
    emit(f'{name}::\n\t.string "' + "\\p".join(pages) + '$"')
    return name


def start(name, prerequisites=()):
    emit(f"Pox_{name}::\n\tgoto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End\n\tlockall")
    for required in prerequisites:
        emit(f"\tgoto_if_unset {required}, Pox_NotReady")


def finish():
    emit("\treleaseall\n\tend")


def message(name, text):
    emit(f"\tmsgbox Pox_Text_{name}, MSGBOX_DEFAULT")
    return (f"Pox_Text_{name}", text)


def beat(name, text, completion, prerequisites=(), extra=""):
    start(name, prerequisites)
    emit(f"\tgoto_if_set {completion}, Pox_Done")
    msg = message(name, text)
    emit(extra)
    emit(f"\tsetflag {completion}")
    finish()
    speech(*msg)


def gift(name, text, prerequisites=()):
    done = flag("GIFT_" + name.upper())
    start(name, prerequisites)
    emit(f"\tgoto_if_set {done}, Pox_GiftDone")
    msg = message(name, text)
    emit("\tgivemon SPECIES_EEVEE, 5\n\tgoto_if_eq VAR_RESULT, MON_CANT_GIVE, Pox_NoRoom")
    emit(f"\tsetflag {done}")
    emit("\tmsgbox Pox_Text_GiftReceived, MSGBOX_DEFAULT")
    finish()
    speech(*msg)


def trainer(name, display, team, level, pic="Leader Roxanne", cls="Leader", double=False):
    tid = "TRAINER_PLASTIC_OX_" + name.upper()
    display = display.replace('TATE & LIZA', 'TATE&LIZA')
    pic = pic.replace('Team Aqua M', 'Aqua Grunt M')
    pic = pic.replace('Cool Trainer M', 'Cooltrainer M')
    trainers.append((tid, f"=== {tid} ===\nName: {display}\nClass: {cls}\nPic: {pic}\nGender: Male\nMusic: {'Leader' if cls == 'Leader' else 'Male'}\nDouble Battle: {'Yes' if double else 'No'}\nAI: Basic Trainer / Smart Switching / PP Stall Prevention\n\n" + "\n\n".join(f"{species}\nLevel: {level}\n- " + "\n- ".join(moves) for species, moves in team) + "\n"))
    trainers[-1] = (tid, trainers[-1][1].replace('Music: Leader', 'Music: Male'))
    return tid


def battle(name, display, text, team, level, completion, prerequisites=(), extra="", pic="Leader Roxanne", cls="Leader", double=False, repeat="Pox_Done"):
    tid = trainer(name, display, team, level, pic, cls, double)
    start(name, prerequisites)
    emit(f"\tgoto_if_set {completion}, {repeat}")
    if double:
        emit('\tsetvar VAR_0x8004, PARTY_SIZE\n\tspecialvar VAR_RESULT, CountPartyAliveNonEggMons_IgnoreVar0x8004Slot\n\tgoto_if_lt VAR_RESULT, 2, Pox_TwoMons')
        emit(f"\ttrainerbattle_double {tid}, Pox_Text_{name}, Pox_Text_Defeat, Pox_Text_TwoMons, Pox_{name}_Won")
    else:
        emit(f"\ttrainerbattle_single {tid}, Pox_Text_{name}, Pox_Text_Defeat, Pox_{name}_Won")
    # Trainer defeat flag survives an interrupted reward script. Talking again
    # must resume the reward, not fall through into dialogue data.
    emit(f"\tgoto Pox_{name}_Won\nPox_{name}_Won::\n\tsetflag {completion}")
    emit(extra)
    finish()
    speech(f"Pox_Text_{name}", text)


def npc(script, x, y, gfx="OBJ_EVENT_GFX_MAN_3", hidden="FLAG_POX_HIDE_STORY_NPCS"):
    gfx = gfx.replace('OBJ_EVENT_GFX_ROCKET_GRUNT_M', 'OBJ_EVENT_GFX_ROCKET_M')
    return dict(graphics_id=gfx, x=x, y=y, elevation=3,
                movement_type="MOVEMENT_TYPE_FACE_DOWN", movement_range_x=0,
                movement_range_y=0, trainer_type="TRAINER_TYPE_NONE",
                trainer_sight_or_berry_tree_id="0", script="Pox_" + script, flag=hidden)


def replace_npc(mapname, index, script, gfx=None, hidden=None):
    data = load_map(mapname)
    obj = data["object_events"][index]
    obj["script"] = "Pox_" + script
    save_map(mapname,data)
    obj['x'],obj['y'] = floor_cell(mapname,obj['x'],obj['y'],obj['script'])
    obj["movement_type"] = "MOVEMENT_TYPE_FACE_DOWN"
    obj["trainer_type"] = "TRAINER_TYPE_NONE"
    if gfx:
        obj["graphics_id"] = gfx.replace('OBJ_EVENT_GFX_ROCKET_GRUNT_M', 'OBJ_EVENT_GFX_ROCKET_M')
    if hidden:
        obj["flag"] = hidden
    save_map(mapname, data)
    manifest.append((mapname, obj['x'], obj['y'], script))


def add_npc(mapname, script, x, y, gfx="OBJ_EVENT_GFX_MAN_3"):
    data = load_map(mapname)
    data["object_events"] = [o for o in data["object_events"] if o["script"] != "Pox_" + script]
    save_map(mapname,data)
    x,y=floor_cell(mapname,x,y)
    data["object_events"].append(npc(script, x, y, gfx))
    save_map(mapname, data)
    manifest.append((mapname, x, y, script))


def mapid(name):
    return load_map(name)["id"]


def travel(name, destination, x, y, text, prerequisites=()):
    x,y=floor_cell(destination,x,y)
    start(name, prerequisites)
    msg = message(name, text)
    emit(f"\twarp {mapid(destination)}, {x}, {y}\n\twaitstate")
    finish()
    speech(*msg)


room_names = []


def room(name, parent, boss, source="RustboroCity_Gym", objects=None, return_xy=(10, 10)):
    dest = "PlasticOx_" + name
    source = {'BurnedTower':'MtPyre_1F', 'PokemonTower':'MtPyre_2F',
              'Mansion':'RustboroCity_DevonCorp_2F', 'Silph':'MossdeepCity_SpaceCenter_1F',
              'WhirlIslands':'GraniteCave_B1F', 'VictoryRoad':'GraniteCave_1F',
              'FujiHouse':'House_GenericA_hns',
              'WallaceRoom':'EverGrandeCity_SidneysRoom',
              'StevenRoom':'EverGrandeCity_PhoebesRoom',
              'LeagueLanceRoom':'EverGrandeCity_GlaciasRoom',
              'BlueRoom':'EverGrandeCity_DrakesRoom',
              'BillRoom':'EverGrandeCity_ChampionsRoom'}.get(name,source)
    data = copy.deepcopy(load_map(source))
    data["id"] = "MAP_PLASTIC_OX_" + re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper()
    data["name"] = dest
    data["connections"] = None
    data["region_map_section"] = load_map(parent)["region_map_section"]
    data["object_events"] = objects or [npc(boss, 5, 2)]
    data["coord_events"] = []
    data["bg_events"] = []
    # Exit through a guide on the known walkable entry corridor. All native
    # source warps are removed so no room can leak back into Emerald's story.
    data["warp_events"] = []
    data["object_events"].append(npc(name + "Exit", 4, 17))
    save_map(dest, data)
    for obj in data['object_events']:
        obj['x'],obj['y']=floor_cell(dest,obj['x'],obj['y'],obj['script'])
        save_map(dest,data)
    put(f"data/maps/{dest}/scripts.inc", f"{dest}_MapScripts::\n\t.byte 0\n")
    room_names.append(dest)
    travel(name + "Exit", parent, *return_xy, "I'll show you back outside.")
    manifest.extend((dest, o['x'], o['y'], o['script'][4:]) for o in data['object_events'])
    return dest


def guide(mapname, index, name, destination, text, prerequisites=()):
    replace_npc(mapname, index, name)
    travel(name, destination, 5, 17, text, prerequisites)


starter = "FLAG_POX_STORY_STARTER"
ilex = "FLAG_POX_STORY_ILEX"
moon = "FLAG_POX_STORY_MTMOON"
weather = "FLAG_POX_STORY_WEATHER"
mansion = "FLAG_POX_STORY_MANSION"
silph = "FLAG_POX_STORY_SILPH"
burned = flag("STORY_BURNED_TOWER")
fuji = flag("STORY_FUJI")
space = flag("STORY_SPACE_CENTER")
flag("HIDE_STORY_NPCS")
badges = [f"FLAG_BADGE{i:02}_GET" for i in range(1, 9)]

emit("Pox_End::\n\tend\nPox_Release::\n\treleaseall\n\tend")
for label, text in [("NotReady", "There is still something to do before you can continue. Ask the local guide."), ("Done", "You've taken care of things here. Good luck on the next road!"), ("GiftDone", "Take good care of EEVEE. I hope you two see plenty of the world."), ("NoRoom", "Your party and PC are full. Make room, then come back."), ("GiftReceived", "You received EEVEE! If your party was full, it went to your PC."), ("TwoMons", "Please bring two healthy POKéMON for our double battle."), ("Defeat", "You and your POKéMON earned that victory!")]:
    emit(f"Pox_{label}::\n\tmsgbox Pox_Text_{label}, MSGBOX_DEFAULT\n\treleaseall\n\tend")
    speech("Pox_Text_" + label, text)

# Pallet: each ball has its own choice; declined/full gifts do not consume it.
for name, species in [("Treecko", "TREECKO"), ("Torchic", "TORCHIC"), ("Mudkip", "MUDKIP")]:
    start(name)
    emit(f"\tgoto_if_set {starter}, Pox_Done\n\tmsgbox Pox_Text_{name}, MSGBOX_YESNO\n\tgoto_if_eq VAR_RESULT, NO, Pox_Release\n\tgivemon SPECIES_{species}, 5\n\tgoto_if_eq VAR_RESULT, MON_CANT_GIVE, Pox_NoRoom\n\tsetflag {starter}\n\tsetflag FLAG_SYS_POKEMON_GET\n\tsetflag FLAG_SYS_POKEDEX_GET\n\tsetflag FLAG_POX_HIDE_R29_GUARD\n\tmsgbox Pox_Text_Oak, MSGBOX_DEFAULT")
    finish()
    speech("Pox_Text_" + name, f"OAK: Will you choose {species}?")
speech("Pox_Text_Oak", "OAK: ELM, BIRCH and I are comparing the changed habitats.|Take this POKéDEX. Meet POKéMON, earn BADGES, and tell us what you find. CHERRYGROVE is west of OLDALE.")
lab = load_map("PalletTown_ProfessorOaksLab_Frlg")
balls = [o for o in lab['object_events'] if 'Ball' in o['script'] or o['script'] in ['Pox_Treecko','Pox_Torchic','Pox_Mudkip']]
assert len(balls) == 3
for obj, name in zip(balls, ["Treecko", "Torchic", "Mudkip"]):
    obj['script'] = 'Pox_' + name
save_map("PalletTown_ProfessorOaksLab_Frlg", lab)
start("Oak")
emit("\tmsgbox Pox_Text_Oak, MSGBOX_DEFAULT")
finish()
add_npc("PalletTown_ProfessorOaksLab_Frlg", "Oak", 6, 5, "OBJ_EVENT_GFX_PROF_OAK")
start("StarterGate")
emit(f"\tgoto_if_set {starter}, Pox_Release\n\tmsgbox Pox_Text_StarterGate, MSGBOX_DEFAULT\n\twarp MAP_PALLET_TOWN, 10, 4\n\twaitstate")
finish()
speech("Pox_Text_StarterGate", "It's dangerous to leave without a POKéMON. Visit OAK's LAB first.")
pallet = load_map("PalletTown_Frlg")
pallet['coord_events'] = [c for c in pallet['coord_events'] if c['script'] != 'Pox_StarterGate']
pallet['coord_events'] += [dict(type='trigger', x=x, y=1, elevation=0, var='VAR_TEMP_0', var_value=0, script='Pox_StarterGate') for x in range(24)]
save_map("PalletTown_Frlg", pallet)

beat("Cherrygrove", "GUIDE: The red roof is a POKéMON CENTER. The MART sells supplies.|These shoes are made for running. Hold B on the road!|A KANTO road on a JOHTO coast... My grandfather would have fainted! Head north through ROUTE 31 to ILEX FOREST.", flag("STORY_CHERRYGROVE"), [starter], "\tsetflag FLAG_SYS_B_DASH")
replace_npc("CherrygroveCity_hns", 0, "Cherrygrove")
beat("Ilex", "You found me! I was mapping the old forest path and lost the signposts.|Let's mark the trail together. The road beyond leads to RUSTBORO now. I still can't get used to that.", ilex, [starter])
replace_npc("IlexForest_hns", 0, "Ilex")
travel("IlexRoad", "RustboroCity", 16, 20, "The trail to RUSTBORO is marked. Follow me.", [ilex])
replace_npc("IlexForest_hns", 1, "IlexRoad")

# Gym order and roster. Alpha teams express each intended tier; competitive
# balance/encounter release is separate from the trigger implementation.
gymdata = [
 ("Roxanne", "ROXANNE", "RustboroCity", [ilex], 5, [('Geodude',['Rock Throw','Tackle']),('Onix',['Rock Tomb','Bind']),('Nosepass',['Rock Tomb','Tackle'])]),
 ("Whitney", "WHITNEY", "GoldenrodCity_hns", [badges[0],moon], 18, [('Delcatty',['Fake Out','Attract','Return']),('Furret',['Quick Attack','Defense Curl','Return']),('Miltank',['Rollout','Milk Drink','Stomp'])]),
 ("Morty", "MORTY", "EcruteakCity_hns", [badges[1],burned], 25, [('Haunter',['Hypnosis','Shadow Ball','Night Shade']),('Misdreavus',['Confuse Ray','Psybeam','Shadow Ball']),('Sableye',['Fake Out','Night Shade','Recover'])]),
 ("Winona", "WINONA", "FortreeCity", [badges[2],weather], 32, [('Swellow',['Quick Attack','Aerial Ace','Facade']),('Pelipper',['Water Pulse','Protect','Wing Attack']),('Altaria',['Dragon Dance','Dragon Breath','Aerial Ace'])]),
 ("Blaine", "BLAINE", "CinnabarIsland_hns", [badges[3],fuji], 38, [('Ninetales',['Flamethrower','Will O Wisp','Confuse Ray']),('Rapidash',['Fire Blast','Return','Sunny Day']),('Arcanine',['Flamethrower','Extreme Speed','Crunch'])]),
 ("TateLiza", "TATE & LIZA", "MossdeepCity", [badges[4],mansion], 44, [('Claydol',['Earthquake','Psychic','Protect']),('Xatu',['Psychic','Reflect','Protect']),('Lunatone',['Psychic','Hypnosis','Protect']),('Solrock',['Rock Slide','Sunny Day','Protect'])]),
 ("Bruno", "BRUNO", "SaffronCity_hns", [badges[5],space], 50, [('Heracross',['Megahorn','Brick Break','Rock Slide']),('Machamp',['Cross Chop','Rock Slide','Bulk Up']),('Hariyama',['Fake Out','Brick Break','Knock Off']),('Snorlax',['Return','Rest','Curse'])]),
 ("Clair", "CLAIR", "BlackthornCity_hns", [badges[6],silph], 55, [('Gyarados',['Dragon Dance','Return','Earthquake']),('Flygon',['Earthquake','Rock Slide','Dragon Claw']),('Kingdra',['Rain Dance','Surf','Ice Beam']),('Salamence',['Dragon Dance','Earthquake','Aerial Ace'])]),
]
for i, (name, display, town, prereq, level, team) in enumerate(gymdata):
    extra = "\tmsgbox Pox_Text_Badge, MSGBOX_DEFAULT"
    repeat = "Pox_Done"
    if name == 'Blaine':
        extra += "\n\tgoto Pox_MansionKey"
        repeat = "Pox_MansionKey"
    battle(name, display, f"{display}: Show me what you and your POKéMON have learned!", team, level, badges[i], prereq, extra, double=name=='TateLiza', repeat=repeat)
    if name in ['Roxanne','Winona','TateLiza']:
        native = {'Roxanne':'RustboroCity_Gym','Winona':'FortreeCity_Gym','TateLiza':'MossdeepCity_Gym'}[name]
        data = load_map(native)
        for obj in data['object_events']:
            if any(leader in obj['script'] for leader in ['Roxanne','Winona','TateAndLiza','Tate','Liza']):
                obj['script'] = 'Pox_' + name
        save_map(native, data)
    else:
        dest = room(name + 'Gym', town, name, return_xy={'Whitney':(25,14),'Morty':(35,44),'Blaine':(37,29),'Bruno':(16,23),'Clair':(16,29)}[name])
        guide(town, {'Whitney':0,'Morty':0,'Blaine':1,'Bruno':0,'Clair':0}[name], name+'Guide', dest, f"{display}'s challenge is this way.", prereq if name=='Clair' else ())
speech("Pox_Text_Badge", "You received a GYM BADGE! A new challenge waits on the next road.")
start("MansionKey", [badges[4]])
keyflag = flag('MANSION_KEY')
emit(f"\tgoto_if_set {keyflag}, Pox_Done\n\tgiveitem ITEM_SECRET_KEY\n\tgoto_if_eq VAR_RESULT, FALSE, Pox_Release\n\tsetflag {keyflag}\n\tmsgbox Pox_Text_MansionKey, MSGBOX_DEFAULT")
finish()
speech('Pox_Text_MansionKey', "BLAINE: This MANSION KEY opens the archives. The old records may help you understand what FUJI meant.")

# Rocket I, deliberately mundane criminals. Each grunt has an independent flag.
moon1 = 'FLAG_POX_HIDE_MTMOON_GRUNT_1'
moon2 = 'FLAG_POX_HIDE_MTMOON_GRUNT_2'
for n, completion, prereq in [(1,moon1,[badges[0]]),(2,moon2,[moon1])]:
    battle(f'MoonGrunt{n}', 'GRUNT', "These fossils belong to TEAM ROCKET now!", [('Zubat',['Bite','Wing Attack']),('Rattata',['Hyper Fang','Quick Attack'])], 12, completion, prereq, pic='Team Aqua M', cls='Team Aqua')
    replace_npc('MtMoon_Cave_hns', n-1, f'MoonGrunt{n}', 'OBJ_EVENT_GFX_ROCKET_GRUNT_M', completion)
beat('MoonScientist', "That isn't one of ours. We didn't install this receiver!|The ROCKETS left the fossils behind. Take one for safekeeping.", moon, [moon1,moon2], '\tgiveitem ITEM_HELIX_FOSSIL\n\tgoto_if_eq VAR_RESULT, FALSE, Pox_Release')
replace_npc('MtMoon_Cave_hns', 2, 'MoonScientist', 'OBJ_EVENT_GFX_SCIENTIST')
gift('Family', "BILL never visits enough. His first POKéMON was ABRA, you know.|I used to dance in ECRUTEAK when I was young.|This EEVEE needs someone with time for long walks. Will you look after it?", [starter])
replace_npc('GoldenrodCity_BillsHouse_hns', 0, 'Family')

# Ecruteak: the optional full troupe and the mandatory tower investigation.
kimono_flags = []
kimono_objects = []
for i, species in enumerate(['Vaporeon','Jolteon','Flareon','Espeon','Umbreon']):
    f = flag('KIMONO_' + species.upper())
    kimono_flags.append(f)
    battle('Kimono'+species, ['NAOKO','SAYO','ZUKI','KUNI','MIKI'][i], 'Our dance honors the BURNED TOWER. MORTY went there after the last rite.|Would you join our POKéMON in a battle?', [(species,['Quick Attack', {'Vaporeon':'Water Pulse','Jolteon':'Shock Wave','Flareon':'Flamethrower','Espeon':'Psybeam','Umbreon':'Faint Attack'}[species]])], 24, f, [badges[1]], pic='Beauty', cls='Beauty')
    kimono_objects.append(npc('Kimono'+species, [3,5,7,3,7][i], [9,2,9,13,13][i], 'OBJ_EVENT_GFX_WOMAN_2'))
gift('Kimono', 'You matched all five of our partners with grace. Please raise this EEVEE with the same care.', kimono_flags)
kimono_objects.append(npc('Kimono', 5, 15, 'OBJ_EVENT_GFX_OLD_WOMAN'))
dance = room('DanceTheater','EcruteakCity_hns',None,objects=kimono_objects,return_xy=(36,33))
guide('EcruteakCity_hns',1,'DanceGuide',dance,'The KIMONO troupe is performing. MORTY is investigating the BURNED TOWER.')
beat('BurnedTower', "MORTY: That doorway... It hasn't stood there for generations.|For a moment, you see an unburned stairway. Then only ash remains.|MORTY: Places remember what they were. Whatever moved the roads has disturbed this place too.|You recover the fallen ceremonial bell. MORTY returns to the GYM.", burned, [badges[1]])
tower = room('BurnedTower','EcruteakCity_hns','BurnedTower',return_xy=(19,23))
guide('EcruteakCity_hns',3,'BurnedGuide',tower,'MORTY needs help in the old tower.',[badges[1]])

battle('Weather','RESEARCHER','Help me test our field instruments. The weather lines have moved since yesterday.', [('Castform',['Water Pulse','Shock Wave','Weather Ball']),('Magnemite',['Thunder Wave','Spark'])], 28, weather, [badges[2]], '\tmsgbox Pox_Text_WeatherReport, MSGBOX_DEFAULT', pic='Scientist Frlg',cls='Scientist Frlg')
speech('Pox_Text_WeatherReport', 'These are new changes. The boundaries are still moving!|It is not just damage left by the convergence. Something is still changing our habitats.')
replace_npc('Route119_WeatherInstitute_2F',4,'Weather',hidden='FLAG_POX_HIDE_STORY_NPCS')
gift('Cottage', "The note says: 'For a visiting TRAINER. Please give EEVEE a good home.'|He's hardly ever here when he gets interested in something. That's nothing new.", [starter])
replace_npc('Route25_BillsHouse_hns',0,'Cottage')
# Direct return makes this unique interior safe without a dynamic-warp setup.
cottage=load_map('Route25_BillsHouse_hns')
cottage['object_events']=cottage['object_events'][:1]
cottage['warp_events']=[]
save_map('Route25_BillsHouse_hns',cottage)
add_npc('Route25_BillsHouse_hns','CottageExit',7,8)
travel('CottageExit','FortreeCity',7,8,'Safe travels!')
travel('CottageGuide','Route25_BillsHouse_hns',7,7,'The SEA COTTAGE is a short trip from here.',[badges[3]])
add_npc('FortreeCity','CottageGuide',7,7)

lav1='FLAG_POX_HIDE_LAVENDER_GRUNT_1'
lav2='FLAG_POX_HIDE_LAVENDER_GRUNT_2'
for n,f,req in [(1,lav1,[badges[3]]),(2,lav2,[lav1])]:
    battle('TowerGrunt'+str(n),'GRUNT',"FUJI knows something about reconstructing POKéMON. He'll answer our questions!", [('Golbat',['Bite','Wing Attack','Confuse Ray']),('Weezing',['Sludge','Smokescreen','Self Destruct'])],35,f,req,pic='Team Aqua M',cls='Team Aqua')
beat('FujiRescue', "FUJI: Thank you. They asked about preserving living states... old work I hoped never to hear of again.|The archives on CINNABAR may explain more. Ask BLAINE for access.|I'll return to the POKéMON HOUSE. Come visit us.",fuji,[lav1,lav2])
ptower=room('PokemonTower','LavenderTown_hns',None,objects=[npc('TowerGrunt1',3,13,'OBJ_EVENT_GFX_ROCKET_GRUNT_M',lav1),npc('TowerGrunt2',7,9,'OBJ_EVENT_GFX_ROCKET_GRUNT_M',lav2),npc('FujiRescue',5,2,'OBJ_EVENT_GFX_OLD_MAN')],return_xy=(17,8))
guide('LavenderTown_hns',0,'TowerGuide',ptower,'TEAM ROCKET is holding MR. FUJI in the POKéMON TOWER.',[badges[3]])
gift('Fuji','FUJI: This EEVEE was abandoned. You have shown it what kindness looks like.|BLAINE keeps the key to the CINNABAR archives.',[fuji])
house=room('FujiHouse','LavenderTown_hns','Fuji',return_xy=(12,11))
guide('LavenderTown_hns',1,'FujiGuide',house,'The POKéMON HOUSE welcomes everyone.')

archive1=flag('ARCHIVE_1')
archive2=flag('ARCHIVE_2')
beat('Archive1','ARCHIVE: A stored POKéMON is not simply a picture. Its living state must be preserved.',archive1,[keyflag])
beat('Archive2','ARCHIVE: Transfer protocols reconcile states recorded in different environments. A reconstruction can resemble an earlier state.',archive2,[archive1])
beat('Archive3','ARCHIVE: Never connect environmental reconstruction controls to an unconstrained transfer network.|The reports resemble the changes at the BURNED TOWER, on a much larger scale.',mansion,[archive2])
entei=flag('ENTEI')
start('Entei',[mansion])
emit(f'\tgoto_if_set {entei}, Pox_Done\n\tmsgbox Pox_Text_Entei, MSGBOX_YESNO\n\tgoto_if_eq VAR_RESULT, NO, Pox_Release\n\tsetwildbattle SPECIES_ENTEI, 40, ITEM_NONE\n\tdowildbattle\n\tspecialvar VAR_RESULT, GetBattleOutcome\n\tgoto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Pox_EnteiDone\n\tgoto_if_ne VAR_RESULT, B_OUTCOME_WON, Pox_Release\nPox_EnteiDone::\n\tsetflag {entei}')
finish()
speech('Pox_Text_Entei','A low growl echoes from the ruined hall. Approach ENTEI?')
man=room('Mansion','CinnabarIsland_hns',None,objects=[npc('Archive1',3,13,'OBJ_EVENT_GFX_SCIENTIST'),npc('Archive2',7,9,'OBJ_EVENT_GFX_SCIENTIST'),npc('Archive3',5,2,'OBJ_EVENT_GFX_SCIENTIST'),npc('Entei',3,9,'OBJ_EVENT_GFX_MAN_3',entei)],return_xy=(40,22))
guide('CinnabarIsland_hns',0,'MansionGuide',man,'The MANSION archives are sealed. BLAINE has the key.',[keyflag])

beat('SpaceReport','The region is not arranged randomly. Habitats and strong TRAINERS have become easier to reach.|It looks like an environment arranged for training.|Transfer traffic is converging on SAFFRON, at SILPH CO. We cannot identify its source.',space,[badges[5]])
gift('Space','This EEVEE helped us study adaptation. Our observations are complete. Please take it on your journey.',[space])
replace_npc('MossdeepCity_SpaceCenter_1F',0,'SpaceReport',hidden='FLAG_POX_HIDE_STORY_NPCS')
add_npc('MossdeepCity_SpaceCenter_1F','Space',5,7,'OBJ_EVENT_GFX_SCIENTIST')

silphgrunts=[]
for n in range(1,4):
    f='FLAG_POX_HIDE_SILPH_GRUNT_'+str(n)
    req=[space] if n==1 else [silphgrunts[-1]]
    silphgrunts.append(f)
    battle('SilphGrunt'+str(n),'GRUNT',"These terminals won't obey us. But the BOSS will make this system his!",[('Muk',['Sludge Bomb','Minimize','Body Slam']),('Golbat',['Bite','Confuse Ray','Wing Attack'])],48,f,req,pic='Team Aqua M',cls='Team Aqua')
gio='FLAG_POX_HIDE_SILPH_GIOVANNI'
battle('Giovanni','GIOVANNI',"We did not make this world. We followed a signal, then the old man's research.|A system that can rearrange a region can give its owner anything. Stand aside!",[('Nidoking',['Earthquake','Ice Beam','Thunderbolt']),('Kangaskhan',['Return','Shadow Ball','Fake Out']),('Dugtrio',['Earthquake','Rock Slide','Aerial Ace']),('Rhydon',['Earthquake','Rock Slide','Megahorn'])],52,gio,[silphgrunts[-1]],pic='Leader Giovanni Frlg')
beat('SilphCore','TERMINAL: ADAPTIVE TRAINER SYSTEM.|Battle profiles: BLUE, LANCE, STEVEN, WALLACE. Objective: improve training conditions.|Habitat isolation detected. Regional transfer links reconciled. Environmental restructuring active.|You isolate the environmental controls. The transfer links fall silent.|The existing region remains. Its boundaries have stopped moving.',silph,[gio], '\tsetflag FLAG_POX_HIDE_SAFFRON_GATE_NPC')
sroom=room('Silph','SaffronCity_hns',None,objects=[npc('SilphGrunt1',3,13,'OBJ_EVENT_GFX_ROCKET_GRUNT_M',silphgrunts[0]),npc('SilphGrunt2',7,13,'OBJ_EVENT_GFX_ROCKET_GRUNT_M',silphgrunts[1]),npc('SilphGrunt3',3,9,'OBJ_EVENT_GFX_ROCKET_GRUNT_M',silphgrunts[2]),npc('Giovanni',7,9,'OBJ_EVENT_GFX_MAN_3',gio),npc('SilphCore',5,2,'OBJ_EVENT_GFX_SCIENTIST')],return_xy=(26,16))
guide('SaffronCity_hns',1,'SilphGuide',sroom,'SILPH needs help. BRUNO is accepting challenges at the DOJO. You can visit either first.',[space])

# Travel services join the currently disconnected demo legs. Prerequisites
# remain at the objectives as well as at these connections.
links=[('RustboroCity',0,'MoonRoad','MtMoon_Cave_hns',10,11,'The mountain trail leads to MT. MOON.',[badges[0]]),
 ('MtMoon_Cave_hns',None,'GoldenrodRoad','GoldenrodCity_hns',25,14,'The road is clear to GOLDENROD.',[moon]),
 ('GoldenrodCity_hns',1,'ParkRoad','NationalPark_Normal_hns',39,21,'Take a break at the NATIONAL PARK before ECRUTEAK.',[badges[1]]),
 ('NationalPark_Normal_hns',0,'EcruteakRoad','EcruteakCity_hns',35,44,'ECRUTEAK lies beyond the park.',[badges[1]]),
 ('EcruteakCity_hns',2,'WeatherRoad','Route119_WeatherInstitute_1F',6,8,'The WEATHER INSTITUTE is asking for a field assistant.',[badges[2]]),
 ('FortreeCity',None,'LavenderRoad','LavenderTown_hns',12,11,'The eastern road reaches LAVENDER.',[badges[3]]),
 ('LavenderTown_hns',2,'CinnabarRoad','CinnabarIsland_hns',37,29,'A boat is leaving for CINNABAR.',[fuji]),
 ('CinnabarIsland_hns',None,'MossdeepRoad','MossdeepCity',38,13,'Our next port is MOSSDEEP.',[mansion]),
 ('MossdeepCity',0,'SaffronRoad','SaffronCity_hns',16,23,'The mainland service goes to SAFFRON.',[space]),
 ('SaffronCity_hns',2,'BlackthornRoad','BlackthornCity_hns',16,29,'With BRUNO defeated and SILPH stable, the mountain road to BLACKTHORN is open.',[badges[6],silph]),
 ('BlackthornCity_hns',1,'LeagueRoad','IndigoPlateau_hns',11,13,'The LEAGUE approach is open to holders of all eight BADGES.',badges),]
for town,index,name,dest,x,y,text,req in links:
    travel(name,dest,x,y,text,req)
    if index is not None:
        replace_npc(town,index,name)
    else:
        add_npc(town,name,*{'MtMoon_Cave_hns':(11,10),'FortreeCity':(8,7),'CinnabarIsland_hns':(38,28)}[town])

# Sequential League rooms: repeat interaction advances without granting a
# second victory; losing a battle never runs its completion script.
league=[('Wallace','WALLACE',[('Milotic',['Surf','Ice Beam','Recover']),('Ludicolo',['Surf','Giga Drain','Rain Dance']),('Gyarados',['Dragon Dance','Earthquake','Return']),('Starmie',['Surf','Psychic','Thunderbolt'])]),
 ('Steven','STEVEN',[('Skarmory',['Spikes','Roar','Drill Peck']),('Claydol',['Earthquake','Psychic','Rapid Spin']),('Metagross',['Meteor Mash','Earthquake','Agility']),('Cradily',['Recover','Toxic','Rock Slide'])]),
 ('LeagueLance','LANCE',[('Salamence',['Dragon Dance','Earthquake','Aerial Ace']),('Aerodactyl',['Rock Slide','Earthquake','Double Edge']),('Gyarados',['Dragon Dance','Earthquake','Return']),('Dragonite',['Dragon Claw','Thunderbolt','Ice Beam'])]),
 ('Blue','BLUE',[('Tyranitar',['Rock Slide','Earthquake','Dragon Dance']),('Alakazam',['Psychic','Calm Mind','Recover']),('Swampert',['Surf','Earthquake','Ice Beam']),('Arcanine',['Flamethrower','Extreme Speed','Crunch']),('Exeggutor',['Psychic','Giga Drain','Sleep Powder'])]),
 ('Bill','BILL',[('Jolteon',['Thunderbolt','Baton Pass','Substitute']),('Metagross',['Meteor Mash','Earthquake','Explosion']),('Swampert',['Earthquake','Surf','Ice Beam']),('Snorlax',['Return','Shadow Ball','Curse']),('Gengar',['Thunderbolt','Ice Punch','Will O Wisp']),('Salamence',['Dragon Dance','Earthquake','Aerial Ace'])])]
lf=[flag('LEAGUE_'+name.upper()) for name,_,_ in league]
for i,(name,display,team) in enumerate(league):
    room(name+'Room','IndigoPlateau_PokemonCenter_hns',name,return_xy=(19,14))
for i,(name,display,team) in enumerate(league):
    txt=f'{display}: The next room must be earned. Show me your best battle!'
    extra=''
    if name=='Bill':
        txt="BILL: Funny, isn't it? I built tools to help other TRAINERS. Then I built one to help myself.|BLUE, LANCE, STEVEN and WALLACE made it stronger. It made me stronger.|I never told it to move the world. But I built something that could. That responsibility is mine.|You've beaten all four of them. I've been looking forward to this!"
        extra='\tmsgbox Pox_Text_Champion, MSGBOX_DEFAULT\n\tspecial GameClear\n\twaitstate'
    else:
        nextroom='PlasticOx_'+league[i+1][0]+'Room'
        extra=f'\tgoto Pox_{name}Advance'
        travel(name+'Advance',nextroom,5,17,'The next room is yours.',[lf[i]])
    battle(name,display,txt,team,60+i,lf[i],badges if i==0 else [lf[i-1]],extra,pic='Champion Wallace' if name=='Bill' else 'Leader Roxanne',cls='Champion' if name=='Bill' else 'Elite Four',repeat='Pox_Done' if name=='Bill' else 'Pox_'+name+'Advance')
speech('Pox_Text_Champion',"BILL: You did it. These POKéMON and their TRAINER belong in the HALL OF FAME. Congratulations, CHAMPION!")
guide('IndigoPlateau_PokemonCenter_hns',1,'LeagueEntry','PlasticOx_WallaceRoom','The POKéMON LEAGUE challenge begins here.',badges)

# Preserve the Institute/Space Center architecture while removing the unrelated
# Aqua/Magma occupation scripts and their trainer objects from these chapters.
for native in ['Route119_WeatherInstitute_1F','Route119_WeatherInstitute_2F',
               'MossdeepCity_SpaceCenter_1F','MossdeepCity_SpaceCenter_2F']:
    data=load_map(native)
    data['coord_events']=[]
    for obj in data['object_events']:
        if not obj['script'].startswith('Pox_'):
            obj['script']='Pox_FacilityWorker'
            obj['trainer_type']='TRAINER_TYPE_NONE'
            if any(v in obj['graphics_id'] for v in ['AQUA','MAGMA','MAXIE','SHELLY']):
                obj['flag']='FLAG_POX_HIDE_UNUSED_ACTOR'
    save_map(native,data)
    p=f'data/maps/{native}/scripts.inc'
    put(p,re.sub(r'\A.*?\t.byte 0',native+'_MapScripts::\n\t.byte 0',read(p),count=1,flags=re.S))
flag('HIDE_UNUSED_ACTOR')
start('FacilityWorker')
emit('\tmsgbox Pox_Text_FacilityWorker, MSGBOX_DEFAULT')
finish()
speech('Pox_Text_FacilityWorker','Our field researchers can explain the latest observations. Please speak with them.')
start('Heal')
emit('\tcall Common_EventScript_OutOfCenterPartyHeal\n\tmsgbox Pox_Text_Heal, MSGBOX_DEFAULT')
finish()
speech('Pox_Text_Heal','Your POKéMON are feeling better. Take care on the road!')
for pc in ['PokemonCenter_Johto_hns','PokemonCenter_Kanto_hns','IndigoPlateau_PokemonCenter_hns']:
    replace_npc(pc,0,'Heal')

# Optional exploration rewards, with an explicit stop on the League approach.
beat('WhirlItem','You found a pearl tucked among the tide-worn stones.',flag('WHIRL_ITEM'),[mansion], '\tgiveitem ITEM_BIG_PEARL\n\tgoto_if_eq VAR_RESULT, FALSE, Pox_Release')
whirl=room('WhirlIslands','CinnabarIsland_hns','WhirlItem',return_xy=(37,29))
add_npc('CinnabarIsland_hns','WhirlGuide',39,28)
travel('WhirlGuide',whirl,5,17,'We can visit the WHIRL ISLANDS before sailing on to MOSSDEEP.',[mansion])
vrflag=flag('VICTORY_ROAD')
battle('VictoryRoad','ACE','One last test before the LEAGUE!', [('Metagross',['Meteor Mash','Earthquake','Agility']),('Starmie',['Surf','Psychic','Thunderbolt']),('Salamence',['Dragon Claw','Earthquake','Aerial Ace'])],57,vrflag,badges,pic='Cool Trainer M',cls='Cooltrainer')
vr=room('VictoryRoad','BlackthornCity_hns','VictoryRoad',return_xy=(25,28))
add_npc(vr,'LeagueContinue',5,15)
travel('LeagueContinue','IndigoPlateau_hns',11,13,'You are ready for the LEAGUE.',[vrflag])
# Replace the earlier direct League transport with this trial.
for i,s in enumerate(scripts):
    if s.startswith('warp MAP_INDIGO_PLATEAU_HNS, 11, 13'):
        # Only the existing LeagueRoad warp precedes this final section.
        if i and any('Pox_LeagueRoad::' in p for p in scripts[max(0,i-12):i]):
            scripts[i]=f'warp {mapid(vr)}, 5, 17\n\twaitstate\n'

put('data/scripts/plastic_ox_story.inc','@ Generated by plastic_ox/alpha/build_story.py. Edit the manifest there.\n\n'+'\n'.join(scripts))
path='data/event_scripts.s'
s=read(path)
for include in ['data/scripts/plastic_ox_story.inc']+[f'data/maps/{n}/scripts.inc' for n in room_names]:
    line=f'\t.include "{include}"\n'
    if line not in s:
        s+=line
put(path,s)
groups=json.loads(read('data/maps/map_groups.json'))
groups['gMapGroup_PlasticOxStory']=room_names
if 'gMapGroup_PlasticOxStory' not in groups['group_order']:
    groups['group_order'].append('gMapGroup_PlasticOxStory')
put('data/maps/map_groups.json',json.dumps(groups,indent=2)+'\n')

# Additional story flags occupy the previously unused 0x020..0x04F run.
assert len(flags)<=48
put('include/constants/plastic_ox_story.h','#ifndef GUARD_PLASTIC_OX_STORY_CONSTANTS_H\n#define GUARD_PLASTIC_OX_STORY_CONSTANTS_H\n\n// Reserved unused general flags. Never allocate trainer/daily flags here.\n'+''.join(f'#define {f} 0x{0x20+i:03X}\n' for i,f in enumerate(flags))+'\n#endif\n')
path='include/constants/plastic_ox_flags.h'
s=read(path)
if '#include "constants/plastic_ox_story.h"' not in s:
    s=s.replace('#define GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H','#define GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H\n\n#include "constants/plastic_ox_story.h"')
put(path,s)
path='include/constants/opponents.h'
s=read(path)
s=re.sub(r'// Plastic Ox story trainers\.\n.*?// End Plastic Ox story trainers\.\n\n','',s,flags=re.S)
defs='// Plastic Ox story trainers.\n'+''.join(f'#define {tid} {857+i}\n' for i,(tid,_) in enumerate(trainers))+'// End Plastic Ox story trainers.\n'
s=s.replace('// NOTE: Because each Trainer',defs+'\n// NOTE: Because each Trainer')
s=re.sub(r'#define TRAINERS_COUNT_EMERALD\s+\d+',f'#define TRAINERS_COUNT_EMERALD {857+len(trainers)}',s)
s=re.sub(r'#define MAX_TRAINERS_COUNT_EMERALD\s+\d+','#define MAX_TRAINERS_COUNT_EMERALD 896',s)
assert len(trainers)<=39
put(path,s)
path='src/data/trainers.party'
s=read(path).split('=== TRAINER_PLASTIC_OX_ROXANNE ===')[0].rstrip()+'\n\n'
put(path,s+'\n'.join(t for _,t in trainers))
put('plastic_ox/alpha/story_manifest.json',json.dumps(dict(events=[dict(map=m,x=x,y=y,script='Pox_'+s) for m,x,y,s in manifest],flags=flags,trainers=[t for t,_ in trainers],rooms=room_names),indent=2)+'\n')

different={p:t for p,t in changes.items() if not Path(p).exists() or Path(p).read_text()!=t}
if '--check' in sys.argv:
    if different:
        sys.exit('Story sources need regeneration: '+', '.join(different))
    print(f'Story sources current: {len(manifest)} events, {len(trainers)} trainers, {len(room_names)} rooms')
else:
    print('*** Begin Patch')
    for path,text in different.items():
        if Path(path).exists():
            print('*** Update File: '+path)
            diff=list(difflib.unified_diff(Path(path).read_text().splitlines(),text.splitlines(),n=3))[2:]
            for line in diff:
                print('@@' if line.startswith('@@') else line)
        else:
            print('*** Add File: '+path)
            print(''.join('+'+line+'\n' for line in text.splitlines()),end='')
    print('*** End Patch')
