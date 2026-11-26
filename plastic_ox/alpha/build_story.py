#!/usr/bin/env python3
"""Emit an apply_patch patch for the alpha story's declarative map/script sources.

Run from the repository root. This tool never writes files itself. --check
checks that the checked-in sources match the story manifest below.
Existing layouts are reused, not copied or converted. See STORY_TRIGGERS.md.
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
flag_allocations = json.loads(Path('plastic_ox/alpha/story_flags.json').read_text())
flag_values = [int(value, 0) for value in flag_allocations.values()]
assert len(flag_values) == len(set(flag_values)), 'Duplicate persistent story flag IDs'
assert all(0x020 <= value <= 0x04F for value in flag_values), 'Story flag outside reserved run'
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
    if name not in flag_allocations:
        raise ValueError(f'Allocate a stable ID for {name} in story_flags.json first')
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


def start(name, prerequisites=(), notready=None):
    emit(f"Pox_{name}::\n\tgoto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End\n\tlockall")
    for required in prerequisites:
        # notready maps a prerequisite flag to a leader-specific refusal label.
        label = (notready or {}).get(required, "Pox_NotReady")
        emit(f"\tgoto_if_unset {required}, {label}")


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


GIFT_DONE_LINES = {
    'Fuji': "FUJI: EEVEE seems lighter on its feet already. Thank you for giving it a home.|The archives on CINNABAR will not wait forever. ROUTE 8 west, then the UNDERGROUND PATH.",
    'Space': "How is EEVEE adapting? Our logs end where your journey begins.",
    'Family': "My father-in-law writes more than BILL does. The sea air suits him.|If you pass the SEA COTTAGE, tell him the EEVEE is walking every day.",
}


def gift(name, text, prerequisites=()):
    done = flag("GIFT_" + name.upper())
    start(name, prerequisites)
    if name in GIFT_DONE_LINES:
        emit(f"\tgoto_if_set {done}, Pox_{name}_GiftDone")
    else:
        emit(f"\tgoto_if_set {done}, Pox_GiftDone")
    msg = message(name, text)
    emit("\tgivemon SPECIES_EEVEE, 5\n\tgoto_if_eq VAR_RESULT, MON_CANT_GIVE, Pox_NoRoom")
    emit(f"\tsetflag {done}")
    emit("\tmsgbox Pox_Text_GiftReceived, MSGBOX_DEFAULT")
    finish()
    speech(*msg)
    if name in GIFT_DONE_LINES:
        emit(f"Pox_{name}_GiftDone::\n\tmsgbox Pox_Text_{name}_GiftDone, MSGBOX_DEFAULT\n\treleaseall\n\tend")
        speech(f"Pox_Text_{name}_GiftDone", GIFT_DONE_LINES[name])


# Authored trainer headers that differ from the generic Leader/Male default.
# The Kimono troupe (2026-11-11 fix pass) gives each dancer her own class, pic,
# music and AI; WHITNEY uses her HNS front pic.
TRAINER_HEADERS = {
    'Whitney': dict(pic='Leader Whitney Hns', gender='Female', music='Female'),
    'KimonoVaporeon': dict(gender='Female', music='Female'),
    'KimonoJolteon': dict(cls='Cooltrainer', pic='Cooltrainer F', gender='Female', music='Cool',
                          ai='Basic Trainer / Try To Faint / HP Aware'),
    'KimonoFlareon': dict(cls='Lady', pic='Lady', gender='Female', music='Female',
                          ai='Basic Trainer / Check Viability / Powerful Status'),
    'KimonoEspeon': dict(cls='Psychic', pic='Psychic F', gender='Female', music='Intense',
                         ai='Basic Trainer / Check Viability / Conservative'),
    'KimonoUmbreon': dict(cls='Hex Maniac', pic='Hex Maniac', gender='Female', music='Suspicious',
                          ai='Basic Trainer / HP Aware / Smart Mon Choices'),
}


def trainer(name, display, team, level, pic="Leader Roxanne", cls="Leader", double=False):
    tid = "TRAINER_PLASTIC_OX_" + name.upper()
    header = TRAINER_HEADERS.get(name, {})
    cls = header.get('cls', cls)
    pic = header.get('pic', pic)
    display = display.replace('TATE & LIZA', 'TATE&LIZA')
    pic = pic.replace('Team Aqua M', 'Aqua Grunt M')
    pic = pic.replace('Cool Trainer M', 'Cooltrainer M')
    party = []
    for species, moves, *details in team:
        attributes = details[0] if details else {}
        item = attributes.get('item')
        if item == 'Leftovers' and level < 25:
            item = 'Sitrus Berry'
        lines = [f'{species} @ {item}' if item else species, f'Level: {level}']
        if 'ability' in attributes:
            lines.append('Ability: ' + attributes['ability'])
        if 'ivs' in attributes:
            lines.append('IVs: ' + attributes['ivs'])
        if 'evs' in attributes:
            lines.append('EVs: ' + attributes['evs'])
        if 'nature' in attributes:
            lines.append(attributes['nature'] + ' Nature')
        lines.extend('- ' + move.split(' [', 1)[0] for move in moves)
        party.append('\n'.join(lines))
    gender = header.get('gender', 'Male')
    music = header.get('music', 'Male')
    ai = header.get('ai', 'Basic Trainer / Smart Switching / PP Stall Prevention')
    trainers.append((tid, f"=== {tid} ===\nName: {display}\nClass: {cls}\nPic: {pic}\nGender: {gender}\nMusic: {music}\nDouble Battle: {'Yes' if double else 'No'}\nAI: {ai}\n\n" + "\n\n".join(party) + "\n"))
    return tid


# Every story trainer gets its own defeat line (no two NPCs share dialogue).
# Names missing here fall back to the shared Pox_Text_Defeat.
DEFEAT_LINES = {
    'Roxanne': "ROXANNE: A textbook battle. I'll be revising my notes tonight.",
    'Morty': "MORTY: I saw this ending in the ash. Seeing it in person is different.",
    'Whitney': "WHITNEY: Huh. You kept up with every swap. Take the badge.",
    'Winona': "WINONA: You rode the wind better than my birds did today.",
    'Blaine': "BLAINE: Hah! You doused my flames without breaking a sweat!",
    'TateLiza': "TATE: We lost… LIZA: …but we lost together.",
    'Bruno': "BRUNO: Hrrgh! My training isn't finished. Neither is yours.",
    'Clair': "CLAIR: Fine. You've earned it. Don't expect me to say so twice.",
    'MoonGrunt1': "Ugh! The boss is gonna dock my pay for this.",
    'MoonGrunt2': "Tch. Fossils are heavy anyway. Who needs 'em?",
    'TowerGrunt1': "Fine. Ask him yourself. Maybe he'll answer you.",
    'TowerGrunt2': "Paper. It was all just paper. Why are we even fighting over it?",
    'SilphGrunt1': "Fine! The terminals didn't like me anyway.",
    'SilphGrunt2': "I'm just here for the overtime, kid!",
    'SilphGrunt3': "Go on, then. The BOSS will deal with you himself.",
    'Giovanni': "GIOVANNI: Hmph. You have no idea what you just interrupted.",
    'Wallace': "WALLACE: Such elegance. You've earned the next door.",
    'Steven': "STEVEN: Hard as stone. I'm glad I got to see your team up close.",
    'LeagueLance': "LANCE: Your POKéMON fight like they trust you completely.",
    'Blue': "BLUE: Tch. Fine. Smell ya at the next room.",
    'Bill': "BILL: …You really did it. I couldn't have predicted that.",
    'VictoryRoad': "ACE: You're ready. The LEAGUE won't know what hit it.",
    'PU_ROUTE33': "Like a rockslide! You flattened us!",
    'PU_ROUTE35': "Aw, my partners wanted to play longer!",
    'PU_PARK': "My bugs need more meadow time, I guess.",
    'PU_ROUTE36': "The old trees saw that coming. I didn't.",
}


def defeat_label(name):
    return f"Pox_Text_{name}_Defeat" if name in DEFEAT_LINES else "Pox_Text_Defeat"


def battle(name, display, text, team, level, completion, prerequisites=(), extra="", pic="Leader Roxanne", cls="Leader", double=False, repeat="Pox_Done", notready=None):
    tid = trainer(name, display, team, level, pic, cls, double)
    start(name, prerequisites, notready)
    emit(f"\tgoto_if_set {completion}, {repeat}")
    if double:
        emit('\tsetvar VAR_0x8004, PARTY_SIZE\n\tspecialvar VAR_RESULT, CountPartyAliveNonEggMons_IgnoreVar0x8004Slot\n\tgoto_if_lt VAR_RESULT, 2, Pox_TwoMons')
        emit(f"\ttrainerbattle_double {tid}, Pox_Text_{name}, {defeat_label(name)}, Pox_Text_TwoMons, Pox_{name}_Won")
    else:
        emit(f"\ttrainerbattle_single {tid}, Pox_Text_{name}, {defeat_label(name)}, Pox_{name}_Won")
    # Trainer defeat flag survives an interrupted reward script. Talking again
    # must resume the reward, not fall through into dialogue data.
    emit(f"\tgoto Pox_{name}_Won\nPox_{name}_Won::\n\tsetflag {completion}")
    emit(extra)
    finish()
    speech(f"Pox_Text_{name}", text)
    if name in DEFEAT_LINES:
        speech(defeat_label(name), DEFEAT_LINES[name])


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


def add_npc(mapname, script, x, y, gfx="OBJ_EVENT_GFX_MAN_3", hidden="FLAG_POX_HIDE_STORY_NPCS"):
    data = load_map(mapname)
    data["object_events"] = [o for o in data["object_events"] if o["script"] != "Pox_" + script]
    save_map(mapname,data)
    x,y=floor_cell(mapname,x,y)
    data["object_events"].append(npc(script, x, y, gfx, hidden))
    save_map(mapname, data)
    manifest.append((mapname, x, y, script))


def mapid(name):
    return load_map(name)["id"]


def manifest_event(mapname, script, x, y):
    """Record an event that is placed on a map by hand rather than by add_npc.

    The Route 36 Sudowoodo and the Flower Shop's flower grower both predate
    this generator; without them the manifest could not validate the
    SquirtBottle -> Sudowoodo chain.
    """
    manifest.append((mapname, x, y, script))


def travel(name, destination, x, y, text, prerequisites=()):
    # Regional movement is now owned by physical trail/gate/cave transitions.
    # Retain these actors as directions, never as town-skipping transports.
    regional_hints = {
        'IlexRoad':"I came through the north gate. That's the way to ROUTE 2.|RUSTBORO is farther north. I'm resting before I head back.",
        'MoonRoad':'The east road crosses ROUTE 44 to MT. MOON.',
        'GoldenrodRoad':'The far cave exit leads to ROUTE 33 and GOLDENROD.',
        'ParkRoad':'Take ROUTE 35 north to NATIONAL PARK.',
        'EcruteakRoad':'The east exit leads through ROUTES 36 and 37 to ECRUTEAK.',
        'WeatherRoad':'Take the east road to ROUTE 119 and the WEATHER INSTITUTE.',
        'CottageGuide':'BILL\'s SEA COTTAGE is near RUSTBORO, beyond ROUTES 24 and 25.',
        'LavenderRoad':'The east road joins ROUTE 110. Follow it south to LAVENDER.',
        'CinnabarRoad':'Take ROUTE 8 west. The UNDERGROUND PATH bypasses closed SAFFRON.|From ROUTE 7, cross ROUTE 103 to CINNABAR.',
        'MossdeepRoad':'Follow the southern coast through SEAFOAM ISLANDS to MOSSDEEP.',
        'SaffronRoad':'The northern coast leads through ROUTE 19 to SAFFRON.',
        'BlackthornRoad':'Take SAFFRON\'s north exit through ROUTES 5 and 115 and METEOR FALLS to BLACKTHORN.',
        'LeagueRoad':'The LEAGUE gate is west of ECRUTEAK. Bring all eight BADGES.',
        'WhirlGuide':'SEAFOAM ISLANDS lie along the coast to MOSSDEEP.',
    }
    if name in regional_hints:
        start(name)
        msg=message(name,regional_hints[name])
        finish()
        speech(*msg)
        return
    x,y=floor_cell(destination,x,y)
    start(name, prerequisites)
    msg = message(name, text)
    emit(f"\twarp {mapid(destination)}, {x}, {y}\n\twaitstate")
    finish()
    speech(*msg)


room_names = []
# Each room's exit attendant says something of its own.
ROOM_EXIT_LINES = {
    'WhitneyGym': "Heading out? Mind the flower beds on your way!",
    'MortyGym': "The way out is the way you came in. I will walk you to the last lamp.",
    'DanceTheater': "The door is behind the third curtain. Mind the rope; the dancers leave it out.",
    'BlaineGym': "Need some air? I'll walk you out of the heat.",
    'BrunoGym': "Leaving the DOJO? Bow on your way out, please.",
    'ClairGym': "The lava's hot today. I'll lead you back to town.",
    'Mansion': "These halls are easy to get lost in. Follow me out.",
    'Silph': "Elevators are down. I'll take you out the back.",
    'WhirlIslands': "The tide's turning. Let's head back to shore.",
    'VictoryRoad': "Not ready yet? I'll guide you back down the trail.",
    'WallaceRoom': "Want to step out? The LEAGUE lobby is this way.",
    'StevenRoom': "Need to regroup? I'll take you back to the lobby.",
    'LeagueLanceRoom': "Take a breather if you need one. Lobby's this way.",
    'BlueRoom': "Backing out? No shame in it. This way to the lobby.",
    'BillRoom': "Not yet? Of course. I'll show you to the lobby.",
}


# Hand-authored room details (2026-11-11/13 fix passes). WHITNEY's hall,
# MORTY's, CLAIR's and the Dance Theater have real doors back to their towns,
# so WHITNEY's hall no longer needs an exit attendant; the theater uses the
# HNS theater interior.
ROOM_OVERRIDES = {
    'WhitneyGym': dict(boss_gfx='OBJ_EVENT_GFX_WHITNEY_HNS', boss_flag='0', exit_guide=False,
                       doors=[(5, 19, 0, 'GoldenrodCity_hns', '5'), (6, 19, 0, 'GoldenrodCity_hns', '5')]),
    'MortyGym': dict(doors=[(5, 19, 0, 'EcruteakCity_hns', '4'), (6, 19, 0, 'EcruteakCity_hns', '4')]),
    'ClairGym': dict(doors=[(5, 19, 3, 'BlackthornCity_hns', '2'), (6, 19, 3, 'BlackthornCity_hns', '2')]),
    'DanceTheater': dict(layout='LAYOUT_ECRUTEAK_CITY_THEATER_HNS', music='MUS_RG_CELADON',
                         battle_scene='MAP_BATTLE_SCENE_NORMAL',
                         doors=[(10, 17, 0, 'EcruteakCity_hns', '3')]),
}
# Tier-rule greeter scripts for the gym halls (2026-11-02). No map object
# uses them yet; see the cinnabarisland-frlg and saffroncity-hns notes.
GYM_GREETERS = {
    'WhitneyGym': ('GOLDENROD GYM', 'PU', 'CheckGoldenrodGymPURules'),
    'MortyGym': ('ECRUTEAK GYM', 'NU', 'CheckEcruteakGymNURules'),
    'BlaineGym': ('CINNABAR GYM', 'UU', 'CheckCinnabarGymUURules'),
    'BrunoGym': ('SAFFRON DOJO GYM', 'OU', 'CheckSaffronGymOURules'),
    'ClairGym': ('BLACKTHORN GYM', 'OU', 'CheckBlackthornGymOURules'),
}


def greeter_scripts(dest, gym, tier, special):
    p = dest + '_'
    return (f'\n{p}EventScript_Greeter::\n\tlock\n\tfaceplayer\n\tmsgbox {p}Text_Greeter, MSGBOX_DEFAULT\n'
            f'\tspecialvar VAR_RESULT, {special}\n'
            f'\tgoto_if_eq VAR_RESULT, 1, {p}EventScript_GreeterBannedMove\n'
            f'\tgoto_if_eq VAR_RESULT, 2, {p}EventScript_GreeterBannedItem\n\trelease\n\tend\n\n'
            f'{p}EventScript_GreeterBannedMove::\n\tmsgbox {p}Text_GreeterBannedMove, MSGBOX_DEFAULT\n\trelease\n\tend\n\n'
            f'{p}EventScript_GreeterBannedItem::\n\tmsgbox {p}Text_GreeterBannedItem, MSGBOX_DEFAULT\n\trelease\n\tend\n\n'
            f'{p}Text_Greeter:\n\t.string "Yo! Champ in the making!\\n"\n\t.string "Welcome to {gym}.\\p"\n'
            f'\t.string "This GYM follows {tier} tier rules.\\p"\n\t.string "Bring your best {tier}-tier POKéMON!$"\n\n'
            f'{p}Text_GreeterBannedMove:\n\t.string "This GYM follows {tier} rules.\\p"\n\t.string "That move is banned here.\\n"\n'
            f'\t.string "Please change it before entering.$"\n\n'
            f'{p}Text_GreeterBannedItem:\n\t.string "This GYM follows {tier} rules.\\p"\n\t.string "That item is banned here.\\n"\n'
            f'\t.string "Please remove it before entering.$"\n')


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
    # source warps are removed so no room can leak back into Emerald's story;
    # only the authored doors in ROOM_OVERRIDES lead back to the parent town.
    over = ROOM_OVERRIDES.get(name, {})
    for field in ('layout', 'music', 'battle_scene'):
        if field in over:
            data[field] = over[field]
    if 'boss_gfx' in over:
        data["object_events"][0]["graphics_id"] = over['boss_gfx']
    if 'boss_flag' in over:
        data["object_events"][0]["flag"] = over['boss_flag']
    data["warp_events"] = [dict(x=x, y=y, elevation=e, dest_map=mapid(town), dest_warp_id=w)
                           for x, y, e, town, w in over.get('doors', [])]
    if over.get('exit_guide', True):
        data["object_events"].append(npc(name + "Exit", 4, 17))
    save_map(dest, data)
    for obj in data['object_events']:
        obj['x'],obj['y']=floor_cell(dest,obj['x'],obj['y'],obj['script'])
        save_map(dest,data)
    put(f"data/maps/{dest}/scripts.inc", f"{dest}_MapScripts::\n\t.byte 0\n"
        + (greeter_scripts(dest, *GYM_GREETERS[name]) if name in GYM_GREETERS else ''))
    room_names.append(dest)
    travel(name + "Exit", parent, *return_xy, ROOM_EXIT_LINES.get(name, "I'll show you back outside."))
    manifest.extend((dest, o['x'], o['y'], o['script'][4:]) for o in data['object_events'])
    return dest


def guide(mapname, index, name, destination, text, prerequisites=()):
    replace_npc(mapname, index, name)
    if name == 'WhitneyGuide':
        emit('Pox_WhitneyGuide::\n\tmsgbox Pox_Text_WhitneyGuide, MSGBOX_NPC\n\tend')
        speech('Pox_Text_WhitneyGuide', "I like watching the GYM challengers.|WHITNEY always gives them a tough battle!")
        return
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
# Saffron and the entire northern OU region open together. Keep the same
# prerequisite on travel, Clair's guide, and her battle so optional OU
# objectives cannot accidentally restore the old Bruno + Silph lock.
northern_ou = [space]
flag("HIDE_STORY_NPCS")
badges = [f"FLAG_BADGE{i:02}_GET" for i in range(1, 9)]

emit("Pox_End::\n\tend\nPox_Release::\n\treleaseall\n\tend")
for label, text in [("NotReady", "There is still something to do before you can continue. Ask the local guide."), ("Done", "You've taken care of things here. Good luck on the next road!"), ("GiftDone", "Take good care of EEVEE. I hope you two see plenty of the world."), ("NoRoom", "Your party and PC are full. Make room, then come back."), ("GiftReceived", "You received EEVEE! If your party was full, it went to your PC."), ("TwoMons", "Please bring two healthy POKéMON for our double battle."), ("Defeat", "You and your POKéMON earned that victory!")]:
    emit(f"Pox_{label}::\n\tmsgbox Pox_Text_{label}, MSGBOX_DEFAULT\n\treleaseall\n\tend")
    speech("Pox_Text_" + label, text)

# Pallet's authored dialogue lives separately from the chapter manifest.
emit('.include "data/scripts/plastic_ox_pallet.inc"')
# Authored item scripts (Training Kit, Pocket Watch) live separately from the
# chapter manifest so regeneration cannot drop them.
emit('.include "data/scripts/plastic_ox_items.inc"')
lab = load_map("PalletTown_ProfessorOaksLab_Frlg")
balls = [o for o in lab['object_events'] if o['graphics_id'] == 'OBJ_EVENT_GFX_ITEM_BALL']
assert len(balls) == 3
for obj, name in zip(balls, ["Treecko", "Squirtle", "Cyndaquil"]):
    obj['script'] = 'Pox_' + name
    obj['flag'] = 'FLAG_POX_HIDE_' + name.upper() + '_BALL'
# Remove the old automatic Treecko choice and unused imported rival.
lab['coord_events'] = []
for obj in lab['object_events']:
    if obj['script'] == 'PalletTown_ProfessorOaksLab_EventScript_Rival':
        obj['flag'] = 'FLAG_POX_HIDE_UNUSED_ACTOR'
save_map("PalletTown_ProfessorOaksLab_Frlg", lab)
add_npc("PalletTown_ProfessorOaksLab_Frlg", "Oak", 6, 4, "OBJ_EVENT_GFX_PROF_OAK")
add_npc("PalletTown_ProfessorOaksLab_Frlg", "Elm", 5, 4, "OBJ_EVENT_GFX_SCIENTIST", hidden="FLAG_POX_ELM_EXP_ALL")
add_npc("PalletTown_ProfessorOaksLab_Frlg", "Birch", 7, 4, "OBJ_EVENT_GFX_PROF_BIRCH", hidden="FLAG_POX_ELM_TMS")
start("StarterGate")
emit(f"\tgoto_if_set {starter}, Pox_Release\n\tmsgbox Pox_Text_StarterGate, MSGBOX_DEFAULT\n\twarp MAP_PALLET_TOWN, 10, 4\n\twaitstate")
finish()
speech("Pox_Text_StarterGate", "It's dangerous to leave without a POKéMON. Visit OAK's LAB first.")
pallet = load_map("PalletTown_Frlg")
pallet['coord_events'] = [c for c in pallet['coord_events'] if c['script'] != 'Pox_StarterGate']
pallet['coord_events'] += [dict(type='trigger', x=x, y=1, elevation=0, var='VAR_TEMP_0', var_value=0, script='Pox_StarterGate') for x in range(24)]
save_map("PalletTown_Frlg", pallet)

beat("Cherrygrove", "GUIDE: The red roof is a POKéMON CENTER. The MART sells supplies.|These shoes are made for running. Hold B on the road!|A KANTO road on a JOHTO coast... My grandfather would have fainted! Head north through ROUTE 2 to ILEX FOREST.", flag("STORY_CHERRYGROVE"), [starter], "\tsetflag FLAG_SYS_B_DASH")
replace_npc("CherrygroveCity_hns", 0, "Cherrygrove")
beat("Ilex", "I walk this trail to warm up. Watch your footing on the roots.|The north path meets ROUTE 2. Beyond it is RUSTBORO, in HOENN.", ilex, [starter])
replace_npc("IlexForest_hns", 0, "Ilex")
travel("IlexRoad", "RustboroCity", 16, 20, "The trail to RUSTBORO is marked. Follow me.", [ilex])
replace_npc("IlexForest_hns", 1, "IlexRoad")

# Gym order and roster. Alpha teams express each intended tier; competitive
# balance/encounter release is separate from the trigger implementation.
gymdata = [
 ("Roxanne", "ROXANNE", "RustboroCity", [ilex], 13, [
     ('Voltorb', ['Thunderbolt', 'Hidden Power [Grass]', 'Substitute', 'Explosion'], dict(item='Sitrus Berry', ability='Static', ivs='30 HP / 31 Atk / 31 Def / 30 SpA / 31 SpD / 31 Spe', evs='36 HP / 36 Def / 240 SpA / 196 Spe', nature='Modest')),
     ('Trapinch', ['Earthquake', 'Quick Attack', 'Hidden Power [Ghost]', 'Endure'], dict(item='Sitrus Berry', ability='Arena Trap', ivs='31 HP / 30 Atk / 31 Def / 31 SpA / 30 SpD / 31 Spe', evs='156 HP / 36 Atk / 160 SpD / 116 Spe', nature='Adamant')),
     ('Cacnea', ['Spikes', 'Giga Drain', 'Hidden Power [Ice]', 'Encore'], dict(item='Sitrus Berry', ability='Sand Veil', ivs='31 HP / 2 Atk / 30 Def / 31 SpA / 31 SpD / 31 Spe', evs='116 HP / 40 Def / 196 SpD / 156 Spe', nature='Calm')),
     ('Chinchou', ['Thunderbolt', 'Hidden Power [Grass]', 'Surf', 'Ice Beam'], dict(item='Sitrus Berry', ability='Volt Absorb', ivs='31 HP / 2 Atk / 31 Def / 30 SpA / 31 SpD / 31 Spe', evs='52 Def / 152 SpA / 68 SpD / 220 Spe', nature='Timid')),
     ('Anorith', ['Swords Dance', 'Hidden Power [Bug]', 'Rock Blast', 'Brick Break'], dict(item='Sitrus Berry', ability='Battle Armor', ivs='31 HP / 31 Atk / 31 Def / 31 SpA / 30 SpD / 30 Spe', evs='76 HP / 76 Atk / 116 Def / 240 Spe', nature='Jolly')),
     ('Lileep', ['Rock Slide', 'Giga Drain', 'Barrier', 'Recover'], dict(item='Sitrus Berry', ability='Suction Cups', evs='148 HP / 108 Atk / 60 Def / 28 SpA / 140 SpD / 12 Spe', nature='Brave')),
 ]),
 ("Whitney", "WHITNEY", "GoldenrodCity_hns", [badges[0],moon], 20, [('Furret',['Quick Attack','Brick Break','Return','Defense Curl']),('Delcatty',['Fake Out','Attract','Return','Sing']),('Wigglytuff',['Body Slam','Rollout','Defense Curl','Disable'],dict(item='Sitrus Berry'))]),
 ("Morty", "MORTY", "EcruteakCity_hns", [badges[1],burned], 25, [('Haunter',['Hypnosis','Shadow Ball','Night Shade']),('Misdreavus',['Confuse Ray','Psybeam','Shadow Ball']),('Sableye',['Fake Out','Night Shade','Recover'])]),
 ("Winona", "WINONA", "FortreeCity", [badges[2],weather], 32, [('Swellow',['Quick Attack','Aerial Ace','Facade']),('Pelipper',['Water Pulse','Protect','Wing Attack']),('Altaria',['Dragon Dance','Dragon Breath','Aerial Ace'])]),
 ("Blaine", "BLAINE", "CinnabarIsland_Frlg", [badges[3],fuji], 38, [('Ninetales',['Flamethrower','Will O Wisp','Confuse Ray']),('Rapidash',['Fire Blast','Return','Sunny Day']),('Arcanine',['Flamethrower','Extreme Speed','Crunch'])]),
 ("TateLiza", "TATE & LIZA", "MossdeepCity", [badges[4],mansion], 44, [('Claydol',['Earthquake','Psychic','Protect']),('Xatu',['Psychic','Reflect','Protect']),('Lunatone',['Psychic','Hypnosis','Protect']),('Solrock',['Rock Slide','Sunny Day','Protect'])]),
 ("Bruno", "BRUNO", "SaffronCity_hns", [badges[5],space], 50, [('Heracross',['Megahorn','Brick Break','Rock Slide']),('Machamp',['Cross Chop','Rock Slide','Bulk Up']),('Hariyama',['Fake Out','Brick Break','Knock Off']),('Snorlax',['Return','Rest','Curse'])]),
 ("Clair", "CLAIR", "BlackthornCity_hns", northern_ou, 55, [('Gyarados',['Dragon Dance','Return','Earthquake']),('Flygon',['Earthquake','Rock Slide','Dragon Claw']),('Kingdra',['Rain Dance','Surf','Ice Beam']),('Salamence',['Dragon Dance','Earthquake','Aerial Ace'])]),
]
for i, (name, display, town, prereq, level, team) in enumerate(gymdata):
    extra = "\tmsgbox Pox_Text_Badge, MSGBOX_DEFAULT"
    repeat = "Pox_Done"
    if name == 'Whitney':
        extra += "\n\tmsgbox Pox_Text_WhitneyAfter, MSGBOX_DEFAULT"
        repeat = "Pox_WhitneyDone"
    if name == 'Blaine':
        extra += "\n\tgoto Pox_MansionKey_Award"
        repeat = "Pox_MansionKey"
    if name == 'Winona':
        # LINDEN (Devon, met at the Weather Institute) walks up with the
        # DEVON SCOPE; talking to Winona again resumes an interrupted gift.
        extra += "\n\tgoto Pox_DevonScope_Award"
        repeat = "Pox_WinonaDone"
    intro = ("WHITNEY: My team keeps moving! Show me how you handle surprises!"
             if name == 'Whitney' else
             "MORTY: You went under the tower. You saw them leave, all eleven, and not one of them looked lost.|I have no explanation that would survive daylight. What I have is a GYM and a badge.|Show me the team you carried down there."
             if name == 'Morty' else
             f"{display}: Show me what you and your POKéMON have learned!")
    whitney = dict(notready={badges[0]: 'Pox_WhitneyNeedsBadge', moon: 'Pox_WhitneyNeedsMoon'}) if name == 'Whitney' else {}
    battle(name, display, intro, team, level, badges[i], prereq, extra,
           double=name=='TateLiza', repeat=repeat, **whitney)
    if name in ['Roxanne','Winona','TateLiza']:
        native = {'Roxanne':'RustboroCity_Gym','Winona':'FortreeCity_Gym','TateLiza':'MossdeepCity_Gym'}[name]
        data = load_map(native)
        for obj in data['object_events']:
            if any(leader in obj['script'] for leader in ['Roxanne','Winona','TateAndLiza','Tate','Liza']):
                obj['script'] = 'Pox_' + name
        if name == 'Winona':
            # Only ever shown by addobject in Pox_DevonScope_Award.
            data['object_events'] = [o for o in data['object_events'] if o['script'] != 'Pox_DevonScopeLinden']
            linden = npc('DevonScopeLinden', 7, 4, 'OBJ_EVENT_GFX_SCIENTIST_1', 'FLAG_POX_HIDE_UNUSED_ACTOR')
            linden = {'local_id': 'LOCALID_FORTREE_GYM_LINDEN', **linden}
            data['object_events'].append(linden)
        save_map(native, data)
    else:
        dest = room(name + 'Gym', town, name, return_xy={'Whitney':(25,14),'Morty':(35,44),'Blaine':(11,11),'Bruno':(16,23),'Clair':(16,29)}[name])
        guide(town, {'Whitney':0,'Morty':0,'Blaine':1,'Bruno':0,'Clair':0}[name], name+'Guide', dest, f"{display}'s challenge is this way.", prereq if name=='Clair' else ())
speech("Pox_Text_Badge", "You received a GYM BADGE! A new challenge waits on the next road.")
# Fortree: after Winona, LINDEN brings the DEVON SCOPE (reveals invisible
# KECLEON, as in Emerald). He enters along the gym's row 4 from (7,4) and stops
# just below the player, who may be facing Winona from (15,3), (14,2) or (16,2).
emit("""Pox_DevonScopeLinden::
\tend
Pox_WinonaDone::
\tgoto_if_set FLAG_RECEIVED_DEVON_SCOPE, Pox_Done
Pox_DevonScope_Award::
\tgetplayerxy VAR_0x8004, VAR_0x8005
\taddobject LOCALID_FORTREE_GYM_LINDEN
\tgoto_if_eq VAR_0x8004, 14, Pox_DevonScope_Left
\tgoto_if_eq VAR_0x8004, 16, Pox_DevonScope_Right
\tapplymovement LOCALID_FORTREE_GYM_LINDEN, Pox_Movement_LindenApproachCenter
\twaitmovement 0
\tcall Pox_DevonScope_Give
\tapplymovement LOCALID_FORTREE_GYM_LINDEN, Pox_Movement_LindenLeaveCenter
\tgoto Pox_DevonScope_End
Pox_DevonScope_Left::
\tapplymovement LOCALID_FORTREE_GYM_LINDEN, Pox_Movement_LindenApproachLeft
\twaitmovement 0
\tcall Pox_DevonScope_Give
\tapplymovement LOCALID_FORTREE_GYM_LINDEN, Pox_Movement_LindenLeaveLeft
\tgoto Pox_DevonScope_End
Pox_DevonScope_Right::
\tapplymovement LOCALID_FORTREE_GYM_LINDEN, Pox_Movement_LindenApproachRight
\twaitmovement 0
\tcall Pox_DevonScope_Give
\tapplymovement LOCALID_FORTREE_GYM_LINDEN, Pox_Movement_LindenLeaveRight
Pox_DevonScope_End::
\twaitmovement 0
\tremoveobject LOCALID_FORTREE_GYM_LINDEN
\treleaseall
\tend
Pox_DevonScope_Give::
\tapplymovement OBJ_EVENT_ID_PLAYER, Common_Movement_WalkInPlaceFasterDown
\twaitmovement 0
\tmsgbox Pox_Text_DevonScope, MSGBOX_DEFAULT
\tgiveitem ITEM_DEVON_SCOPE
\tsetflag FLAG_RECEIVED_DEVON_SCOPE
\tmsgbox Pox_Text_DevonScopeAfter, MSGBOX_DEFAULT
\tclosemessage
\treturn""")
for label, steps in [
    ('ApproachCenter', ['walk_right'] * 8 + ['face_up']),
    ('ApproachLeft', ['walk_right'] * 7 + ['walk_up']),
    ('ApproachRight', ['walk_right'] * 9 + ['walk_up']),
    ('LeaveCenter', ['walk_left'] * 8),
    ('LeaveLeft', ['walk_down'] + ['walk_left'] * 7),
    ('LeaveRight', ['walk_down'] + ['walk_left'] * 9),
]:
    emit(f"Pox_Movement_Linden{label}:\n" + "".join(f"\t{s}\n" for s in steps) + "\tstep_end")
speech("Pox_Text_DevonScope", "LINDEN: There you are! We met at the WEATHER INSTITUTE. LINDEN, DEVON field research.|Our sensors keep logging something on FORTREE's walkways that no camera can see.|This is a DEVON SCOPE. It picks out POKéMON that would rather not be seen. You'll get more use from it out on the road than I will in a lab.")
speech("Pox_Text_DevonScopeAfter", "LINDEN: If something invisible is in your way, look at it through the SCOPE.|Well, back to the INSTITUTE. Those readings won't log themselves!")
# Whitney-specific refusals, repeat line and defeat line (pox-2ma.4); the
# shared Pox_NotReady/Pox_Done/Pox_Text_Defeat stay for everyone else.
for label, line in [
    ('Pox_WhitneyNeedsBadge', "WHITNEY: Badge one first. ROXANNE is in RUSTBORO. The queue starts there."),
    ('Pox_WhitneyNeedsMoon', "WHITNEY: You have a badge, but MT. MOON is still closed behind you. Go through it, then come back."),
    ('Pox_WhitneyDone', "WHITNEY: You have the badge. Next challenger, please."),
]:
    emit(f"{label}::\n\tmsgbox {label.replace('Pox_', 'Pox_Text_')}, MSGBOX_DEFAULT\n\treleaseall\n\tend")
    speech(label.replace('Pox_', 'Pox_Text_'), line)
speech("Pox_Text_WhitneyAfter", "WHITNEY: My friend at the FLOWER SHOP has a SQUIRTBOTTLE. Ask her about the odd tree on ROUTE 36!")
start("MansionKey", [badges[4]])
keyflag = flag('MANSION_KEY')
emit("Pox_MansionKey_Award:")
for machine in ['ITEM_HM04', 'ITEM_HM06']:
    emit(f'\tcheckitem {machine}\n\tgoto_if_eq VAR_RESULT, TRUE, Pox_MansionKey_{machine}\n\tgiveitem {machine}\n\tgoto_if_eq VAR_RESULT, FALSE, Pox_Release\nPox_MansionKey_{machine}::')
emit(f"\tgoto_if_set {keyflag}, Pox_Done\n\tgiveitem ITEM_SECRET_KEY\n\tgoto_if_eq VAR_RESULT, FALSE, Pox_Release\n\tsetflag {keyflag}\n\tmsgbox Pox_Text_MansionKey, MSGBOX_DEFAULT")
finish()
speech('Pox_Text_MansionKey', "BLAINE: This MANSION KEY opens the archives. The old records may help you understand what FUJI meant.|These STRENGTH and ROCK SMASH machines will help you explore the caves ahead.")

# Rocket I, deliberately mundane criminals. Each grunt has an independent flag.
moon1 = 'FLAG_POX_HIDE_MTMOON_GRUNT_1'
moon2 = 'FLAG_POX_HIDE_MTMOON_GRUNT_2'
moon_teams = [
    [('Zubat',['Bite','Wing Attack','Supersonic']),('Rattata',['Hyper Fang','Quick Attack','Tail Whip'])],
    [('Ekans',['Bite','Glare','Wrap']),('Koffing',['Sludge','Smokescreen','Tackle'])],
]
for n, completion, prereq in [(1,moon1,[badges[0]]),(2,moon2,[moon1])]:
    battle(f'MoonGrunt{n}', 'GRUNT', ["These fossils belong to TEAM ROCKET now!","Hands off! These rocks are company property!"][n-1], moon_teams[n-1], 14+n, completion, prereq, pic='Team Aqua M', cls='Team Aqua')
    # Retired trainer IDs stay reserved for existing saves.
beat('MoonRocketMap', "You beat both of our grunts! Fine, take this TOWN MAP and leave TEAM ROCKET alone.", moon, [moon1,moon2], '\tgiveitem ITEM_TOWN_MAP\n\tgoto_if_eq VAR_RESULT, FALSE, Pox_Release')
# Mt. Moon now uses the FireRed floor actors and fossil quest.
# BILL's mother, at home in Goldenrod (the family's later EEVEE). The first
# gift EEVEE comes from the SEA COTTAGE (Pox_Cottage); this one is a second
# EEVEE, per plastic_ox/plastic_ox_story_v7.md.
emit("@ BILL's mother, at home in Goldenrod (the family's later EEVEE). The first\n@ gift EEVEE comes from the SEA COTTAGE (Pox_Cottage); this one is a second\n@ EEVEE, per plastic_ox/plastic_ox_story_v7.md.")
gift('Family', "I used to dance in ECRUTEAK, back when my knees agreed with me.|BILL is my son. He writes about POKéMON and never about himself.|My father-in-law keeps the SEA COTTAGE up north. He sent this EEVEE down on the ferry.|It hates sitting still. Will you walk it for us?", [starter])
replace_npc('GoldenrodCity_BillsHouse_hns', 0, 'Family')

# Ecruteak: the optional troupe battle and the mandatory tower investigation.
# Since 2026-11-25 the troupe is ONE battle. The five dancers stand in a
# semicircle on the stage, open toward the audience; NAOKO leads from the
# centre and fights with the whole troupe's party: EEVEE opens the rite, then
# each dancer's Eeveelution in the order she takes the floor (Jolteon,
# Vaporeon, Flareon, Umbreon, Espeon). The party is authored in
# plastic_ox/tools/authored_trainers.party.
#
# The five old per-dancer trainer ids keep their slots (trainer numbers are
# save data) but nothing battles them any more. Winning the troupe battle sets
# all five FLAG_POX_KIMONO_* flags, so the EEVEE gift and old saves (where some
# dancers were already beaten one at a time) keep working.
KIMONO_TROUPE = 'TRAINER_PLASTIC_OX_KIMONO_TROUPE'
KIMONO_TROUPE_ID = 961
KIMONO_TROUPE_HEADER = ('Name: NAOKO\nClass: Beauty\nPic: Beauty\nGender: Female\nMusic: Female\n'
                        'Double Battle: No\nAI: Basic Trainer / Check Viability / Smart Switching')
# species -> (dancer, stage cell, facing, line before the dance, line after it)
KIMONO_DANCERS = {
    'Vaporeon': ('NAOKO', (10, 2), 'DOWN', None,
                 "Come at dusk sometime. The river sounds different once the lamps are lit."),
    'Jolteon': ('SAYO', (6, 4), 'RIGHT',
                "Rain step, spark step. I go second, right after EEVEE, and I don't wait for anyone.|NAOKO calls the figures. Stand in the middle of the circle and she'll start us.",
                "A quick step is a short one. MORTY says the same about battles, only slower."),
    'Flareon': ('ZUKI', (14, 4), 'LEFT',
                "The ember step comes after the tide. It is not meant to be gentle.|NAOKO has the first word. Mind the edge of the stage on your way round.",
                "The brazier holds its heat till morning. Warm up before you cross the river."),
    'Espeon': ('KUNI', (8, 3), 'DOWN',
               "The mirror step closes the rite, so I dance last. You hear the next move before it happens.|NAOKO is waiting in the middle. She already knows you're here.",
               "Sit a moment. A dance settles like water after a stone."),
    'Umbreon': ('MIKI', (12, 3), 'DOWN',
                "The moon step comes after the ember, once the lamps are out. Only us after the second bell.|When you're ready, NAOKO will start the dance.",
                "The moon step ends facing the tower. We still face it, even now.|Come back at dusk and watch from the door."),
}
KIMONO_TROUPE_LINES = (
    "We don't dance the rite one at a time. EEVEE opens it, and each of us answers in turn.|Stay in the middle of the circle. All five of us will dance with you.",
    "Every figure, every turn, and you were still standing in the middle. Go and see our mistress by the door.",
)
kimono_flags = []
kimono_objects = []
for species in ['Vaporeon','Jolteon','Flareon','Espeon','Umbreon']:
    f = flag('KIMONO_' + species.upper())
    kimono_flags.append(f)
    name = 'Kimono' + species
    dancer, (x, y), facing, before, after = KIMONO_DANCERS[species]
    # Retired one-dancer battle: the header and id stay, the script does not.
    trainer(name, dancer, [(species,['Quick Attack'])], 24, pic='Beauty', cls='Beauty')
    if before is not None:
        start(name)
        for done in ['FLAG_POX_KIMONO_' + other.upper() for other in KIMONO_DANCERS]:
            emit(f"\tgoto_if_unset {done}, Pox_{name}_Before")
        emit(f"\tmsgbox Pox_Text_{name}_After, MSGBOX_DEFAULT")
        finish()
        emit(f"Pox_{name}_Before::\n\tmsgbox Pox_Text_{name}_Before, MSGBOX_DEFAULT\n\treleaseall\n\tend")
        speech(f"Pox_Text_{name}_Before", before)
        speech(f"Pox_Text_{name}_After", after)
    obj = npc('KimonoTroupe' if before is None else name, x, y, 'OBJ_EVENT_GFX_KIMONO_HNS')
    obj['movement_type'] = 'MOVEMENT_TYPE_FACE_' + facing
    kimono_objects.append(obj)
# NAOKO's troupe battle. Fought unless every dancer's flag is already set.
start('KimonoTroupe', [badges[1]])
for done in kimono_flags:
    emit(f"\tgoto_if_unset {done}, Pox_KimonoTroupe_Battle")
emit("\tgoto Pox_KimonoTroupe_After")
emit(f"Pox_KimonoTroupe_Battle::\n\ttrainerbattle_single {KIMONO_TROUPE}, Pox_Text_KimonoTroupe, Pox_Text_KimonoTroupe_Defeat, Pox_KimonoTroupe_Won")
emit("\tgoto Pox_KimonoTroupe_Won\nPox_KimonoTroupe_Won::")
for done in kimono_flags:
    emit(f"\tsetflag {done}")
emit("\tmsgbox Pox_Text_KimonoTroupe_After, MSGBOX_DEFAULT")
finish()
emit("Pox_KimonoTroupe_After::\n\tmsgbox Pox_Text_KimonoTroupe_After, MSGBOX_DEFAULT\n\treleaseall\n\tend")
speech("Pox_Text_KimonoTroupe", KIMONO_TROUPE_LINES[0])
speech("Pox_Text_KimonoTroupe_Defeat", KIMONO_TROUPE_LINES[1])
speech("Pox_Text_KimonoTroupe_After", KIMONO_DANCERS['Vaporeon'][4])
gift('Kimono', 'You danced with all five of my girls, and none of them took it easy on you.|The EEVEE that opens our rite had a litter this spring. This one copies every turn, and it has no partner of its own.|Take it with you - not as a prize, but as a dance partner.', kimono_flags)
kimono_objects.append(npc('Kimono', 5, 15, 'OBJ_EVENT_GFX_OLD_WOMAN'))
dance = room('DanceTheater','EcruteakCity_hns',None,objects=kimono_objects,return_xy=(36,33))
guide('EcruteakCity_hns',1,'DanceGuide',dance,'The KIMONO troupe is performing. MORTY is investigating the BURNED TOWER.')
# Burned Tower B1F (2026-11-12): eleven displaced legendaries gather around
# MORTY, then scatter; he sends the sages after them. Their B1F objects are
# authored in the map; the movement scripts are emitted at the end of the file.
TOWER_CUTSCENE = "closemessage\n\tplayse SE_M_EARTHQUAKE\n\tsetvar VAR_0x8004, 2\n\tsetvar VAR_0x8005, 1\n\tsetvar VAR_0x8006, 20\n\tsetvar VAR_0x8007, 3\n\tspecial ShakeCamera\n\twaitstate\n\tdelay 90\n\tturnobject OBJ_EVENT_ID_PLAYER, DIR_NORTH\n\tplaymoncry SPECIES_ENTEI, CRY_MODE_NORMAL\n\tapplymovement LOCALID_BURNEDTOWER_ENTEI, PoxTower_AwakenBeasts\n\twaitmovement 0\n\twaitmoncry\n\tplaymoncry SPECIES_RAIKOU, CRY_MODE_NORMAL\n\tapplymovement LOCALID_BURNEDTOWER_RAIKOU, PoxTower_AwakenBeasts\n\twaitmovement 0\n\twaitmoncry\n\tplaymoncry SPECIES_SUICUNE, CRY_MODE_NORMAL\n\tapplymovement LOCALID_BURNEDTOWER_SUICUNE, PoxTower_AwakenBeasts\n\twaitmovement 0\n\twaitmoncry\n\tplayse SE_LEDGE\n\tapplymovement LOCALID_BURNEDTOWER_ENTEI, PoxTower_EnteiLeave\n\twaitmovement 0\n\tremoveobject LOCALID_BURNEDTOWER_ENTEI\n\tplayse SE_LEDGE\n\tapplymovement LOCALID_BURNEDTOWER_RAIKOU, PoxTower_RaikouLeave\n\twaitmovement 0\n\tremoveobject LOCALID_BURNEDTOWER_RAIKOU\n\tplayse SE_LEDGE\n\tapplymovement LOCALID_BURNEDTOWER_SUICUNE, PoxTower_SuicuneLeave\n\twaitmovement 0\n\tremoveobject LOCALID_BURNEDTOWER_SUICUNE\n\n\tplaymoncry SPECIES_ARTICUNO, CRY_MODE_NORMAL\n\twaitmoncry\n\tplaymoncry SPECIES_ZAPDOS, CRY_MODE_NORMAL\n\twaitmoncry\n\tplaymoncry SPECIES_MOLTRES, CRY_MODE_NORMAL\n\twaitmoncry\n\tapplymovement LOCALID_POX_TOWER_ARTICUNO, PoxTower_BirdFly\n\tapplymovement LOCALID_POX_TOWER_ZAPDOS, PoxTower_BirdFly\n\tapplymovement LOCALID_POX_TOWER_MOLTRES, PoxTower_BirdFly\n\twaitmovement 0\n\tremoveobject LOCALID_POX_TOWER_ARTICUNO\n\tremoveobject LOCALID_POX_TOWER_ZAPDOS\n\tremoveobject LOCALID_POX_TOWER_MOLTRES\n\tplaymoncry SPECIES_REGIROCK, CRY_MODE_NORMAL\n\twaitmoncry\n\tplaymoncry SPECIES_REGICE, CRY_MODE_NORMAL\n\twaitmoncry\n\tplaymoncry SPECIES_REGISTEEL, CRY_MODE_NORMAL\n\twaitmoncry\n\tapplymovement LOCALID_POX_TOWER_REGIROCK, PoxTower_RegiTeleport\n\tapplymovement LOCALID_POX_TOWER_REGICE, PoxTower_RegiTeleport\n\tapplymovement LOCALID_POX_TOWER_REGISTEEL, PoxTower_RegiTeleport\n\twaitmovement 0\n\tremoveobject LOCALID_POX_TOWER_REGIROCK\n\tremoveobject LOCALID_POX_TOWER_REGICE\n\tremoveobject LOCALID_POX_TOWER_REGISTEEL\n\tplaymoncry SPECIES_CELEBI, CRY_MODE_NORMAL\n\twaitmoncry\n\tapplymovement LOCALID_POX_TOWER_CELEBI, PoxTower_CelebiVanish\n\twaitmovement 0\n\tremoveobject LOCALID_POX_TOWER_CELEBI\n\tplaymoncry SPECIES_JIRACHI, CRY_MODE_NORMAL\n\twaitmoncry\n\tapplymovement LOCALID_POX_TOWER_JIRACHI, PoxTower_JirachiAscend\n\twaitmovement 0\n\tremoveobject LOCALID_POX_TOWER_JIRACHI\n\tdelay 30"
TOWER_SAGES_LEAVE = "closemessage\n\tapplymovement LOCALID_POX_TOWER_SAGE_1, PoxTower_Sage1Leave\n\tapplymovement LOCALID_POX_TOWER_SAGE_2, PoxTower_Sage2Leave\n\twaitmovement 0\n\tremoveobject LOCALID_POX_TOWER_SAGE_1\n\tremoveobject LOCALID_POX_TOWER_SAGE_2\n\tfaceplayer"
TOWER_MOVEMENTS = "PoxTower_AwakenBeasts:\n\tjump_in_place_down\n\tjump_in_place_down\n\tjump_in_place_down\n\tstep_end\n\nPoxTower_EnteiLeave:\n\tjump_down\n\tjump_2_right\n\tjump_2_right\n\tjump_2_right\n\tjump_2_right\n\tstep_end\n\nPoxTower_RaikouLeave:\n\tjump_down\n\tjump_2_left\n\tjump_2_left\n\tjump_2_left\n\tjump_2_left\n\tstep_end\n\nPoxTower_SuicuneLeave:\n\tjump_2_down\n\tdelay_8\n\tjump_in_place_right_left\n\tjump_in_place_right_left\n\tjump_left\n\tjump_2_down\n\tjump_2_down\n\tjump_2_down\n\tstep_end\n\nPoxTower_Sage1Leave:\n\twalk_up\n\twalk_right\n\twalk_right\n\twalk_right\n\twalk_right\n\twalk_right\n\twalk_right\n\twalk_right\n\twalk_right\n\twalk_down\n\twalk_up\n\twalk_up\n\twalk_up\n\twalk_right\n\twalk_right\n\twalk_up\n\twalk_up\n\twalk_right\n\twalk_right\n\tstep_end\n\nPoxTower_Sage2Leave:\n\twalk_right\n\twalk_right\n\twalk_right\n\twalk_right\n\twalk_up\n\twalk_up\n\twalk_up\n\twalk_right\n\twalk_right\n\twalk_up\n\twalk_up\n\twalk_right\n\twalk_right\n\tstep_end\n\n\nPoxTower_Text_Rift::\n\t.string \"MORTY: The air is still shaking.\\nThere are more coming through!$\"\n\nPoxTower_BirdFly:\n\tlevitate\n\tdelay_16\n\tface_up\n stop_levitate\n\tfly_up\n\tset_invisible\n\tstep_end\n\nPoxTower_RegiTeleport:\n\tface_left\n\tdelay_4\n\tface_up\n\tdelay_4\n\tface_right\n\tdelay_4\n\tface_down\n\tdelay_4\n\tface_left\n\tdelay_4\n\tface_up\n\tdelay_4\n\tface_right\n\tdelay_4\n\tface_down\n\tdelay_4\n\tface_left\n\tdelay_4\n\tface_up\n\tdelay_4\n\tface_right\n\tdelay_4\n\tface_down\n\tdelay_4\n\tface_left\n\tdelay_4\n\tface_up\n\tdelay_4\n\tface_right\n\tdelay_4\n\tface_down\n\tdelay_4\n\tset_invisible\n\tdelay_4\n\tset_visible\n\tdelay_4\n\tset_invisible\n\tstep_end\n\nPoxTower_CelebiVanish:\n\tlevitate\n\tjump_in_place_left_right\n\tjump_in_place_right_left\n\tjump_in_place_left_right\n\tjump_in_place_right_left\n\tset_invisible\n\tdelay_8\n\tset_visible\n\tdelay_4\n\tset_invisible\n\tstep_end\n\nPoxTower_JirachiAscend:\n\tlevitate\n\tjump_in_place_up\n\tdelay_16\n\tface_up\n stop_levitate\n\tfly_up\n\tset_invisible\n\tstep_end"
TOWER_LINES = [
    ('BurnedTowerBefore', "MORTY: Eleven gathered here... Listening. Waiting for something.|Wait... Do you feel that?"),
    ('BurnedTowerAfter', "MORTY: Eleven... All drawn to the same place.|The tower was a refuge. Now they must find their way home."),
    ('BurnedTowerMission', "MORTY: Sages, follow them. The world has changed.|Find them shelter. Give them space. Let them choose to stay."),
    ('BurnedTowerSages', "SAGE: We will watch over them. You have our word."),
    ('BurnedTowerFarewell', "MORTY: SUICUNE looked back at you before it left.|Remember that. Trust begins with a moment like this.|I will be at the GYM. Come when you are ready."),
]
start('BurnedTower', [badges[1]])
emit(f'\tgoto_if_set {burned}, Pox_Done')
emit('faceplayer')
emit('\tmsgbox Pox_Text_BurnedTowerBefore, MSGBOX_DEFAULT')
emit(TOWER_CUTSCENE)
emit('\tmsgbox Pox_Text_BurnedTowerAfter, MSGBOX_DEFAULT')
emit('faceplayer')
emit('\tmsgbox Pox_Text_BurnedTowerMission, MSGBOX_DEFAULT')
emit('\tmsgbox Pox_Text_BurnedTowerSages, MSGBOX_DEFAULT')
emit(TOWER_SAGES_LEAVE)
emit('\tmsgbox Pox_Text_BurnedTowerFarewell, MSGBOX_DEFAULT')
emit(f'\tsetflag {burned}\n\tremoveobject VAR_LAST_TALKED')
finish()
for label, text in TOWER_LINES:
    speech('Pox_Text_' + label, text)
# Burned Tower uses the two original HNS floors. Their authored warps and
# basement event are kept in the map sources rather than a generated room.
tower = 'PlasticOx_BurnedTower'
room_names.append(tower)
replace_npc('EcruteakCity_hns', 3, 'BurnedGuide')
start('BurnedGuide')
emit('\tgoto_if_set FLAG_POX_STORY_BURNED_TOWER, Pox_BurnedGuide_After')
before = message('BurnedGuide_Before', 'Someone lights the tower lamps before the ninth hour. I have done it since the fire, and I still count the stairs twice.|MORTY went below this morning. The way down is north of here, past the last lamp.')
emit('\treleaseall\n\tend\nPox_BurnedGuide_After::')
emit('\tgoto_if_set FLAG_BADGE03_GET, Pox_BurnedGuide_Badge')
after = message('BurnedGuide_After', 'The lamps are lit. He came up before dawn and did not say what he found.|That is answer enough for this street.|The GYM is open. He will be waiting at the top of the shadows.')
emit('\treleaseall\n\tend\nPox_BurnedGuide_Badge::')
# After badge 3 the lamp-trimmer stops sending the player to MORTY.
badge = message('BurnedGuide_Badge', 'MORTY came down the street at dusk and trimmed a wick himself.|First time in years. The GYM is quiet again, so I hear it went well for you.|The tower lamps still want oil. That part never changes.')
finish()
speech(*before)
speech(*after)
speech(*badge)

# Project Equilibrium (two trials + Director) is authored in weather_institute.py
# and data/scripts/plastic_ox_weather_institute.inc. Keep the trainer here so
# TRAINER_PLASTIC_OX_WEATHER (872, Silph's VALE) keeps its stable ID; its party
# is authored in trainers.party and kept by apply_trainer_teams_v2.py.
trainer('Weather','VALE',[('Castform',['Sunny Day','Weather Ball','Solar Beam','Thunderbolt'])],34,pic='Scientist Frlg',cls='Scientist Frlg')
replace_npc('Route119_WeatherInstitute_2F',4,'WI_Vale',gfx='OBJ_EVENT_GFX_SCIENTIST',hidden='FLAG_POX_HIDE_STORY_NPCS')
# Bill's grandfather gives Eevee once, then tracks five strictly ordered fossil
# rewards in one small progression variable. Safe legacy flags are imported on
# first interaction; old 0x071 is intentionally not read because Cave of Origin
# still uses it.
start('Cottage',[starter])
emit('''\tgoto_if_set FLAG_POX_KNOWS_BILL_PC, Pox_CottageGift
\tmsgbox Pox_Text_Cottage, MSGBOX_DEFAULT
\tsetflag FLAG_POX_KNOWS_BILL_PC
Pox_CottageGift::
\tgoto_if_set FLAG_POX_GIFT_COTTAGE, Pox_CottageFossils
\tgivemon SPECIES_EEVEE, 5
\tgoto_if_eq VAR_RESULT, MON_CANT_GIVE, Pox_NoRoom
\tsetflag FLAG_POX_GIFT_COTTAGE
\tmsgbox Pox_Text_GiftReceived, MSGBOX_DEFAULT
\tgoto Pox_CottageFossils
Pox_CottageFossils::
\tgoto_if_ne VAR_POX_GRANDPA_PROGRESS, 0, Pox_CottageFossilsDispatch
\tgoto_if_set FLAG_POX_LEGACY_GRANDPA_OLD_AMBER, Pox_CottageMigrate5
\tgoto_if_set FLAG_POX_LEGACY_GRANDPA_ROOT_FOSSIL, Pox_CottageMigrate3
\tgoto_if_set FLAG_POX_LEGACY_GRANDPA_CLAW_FOSSIL, Pox_CottageMigrate2
\tgoto_if_set FLAG_POX_LEGACY_GRANDPA_DOME_FOSSIL, Pox_CottageMigrate1
Pox_CottageFossilsDispatch::
\tgoto_if_eq VAR_POX_GRANDPA_PROGRESS, 0, Pox_CottageRalts
\tgoto_if_eq VAR_POX_GRANDPA_PROGRESS, 1, Pox_CottagePhanpy
\tgoto_if_eq VAR_POX_GRANDPA_PROGRESS, 2, Pox_CottageTeddiursa
\tgoto_if_eq VAR_POX_GRANDPA_PROGRESS, 3, Pox_CottageYanma
\tgoto_if_eq VAR_POX_GRANDPA_PROGRESS, 4, Pox_CottageMagikarp
\tmsgbox Pox_Text_CottageFossilsDone, MSGBOX_DEFAULT
\treleaseall
\tend
Pox_CottageMigrate5::
\tsetvar VAR_POX_GRANDPA_PROGRESS, 5
\tgoto Pox_CottageFossilsDispatch
Pox_CottageMigrate3::
\tsetvar VAR_POX_GRANDPA_PROGRESS, 3
\tgoto Pox_CottageFossilsDispatch
Pox_CottageMigrate2::
\tsetvar VAR_POX_GRANDPA_PROGRESS, 2
\tgoto Pox_CottageFossilsDispatch
Pox_CottageMigrate1::
\tsetvar VAR_POX_GRANDPA_PROGRESS, 1
\tgoto Pox_CottageFossilsDispatch
Pox_CottageRalts::
\tcheckspecies SPECIES_RALTS
\tgoto_if_eq VAR_RESULT, TRUE, Pox_CottageGiveDomeFossil
\tmsgbox Pox_Text_CottageAskRalts, MSGBOX_DEFAULT
\treleaseall
\tend
Pox_CottageGiveDomeFossil::
\tcheckitemspace ITEM_DOME_FOSSIL
\tgoto_if_eq VAR_RESULT, FALSE, Pox_NoRoom
\tgiveitem_msg Pox_Text_CottageGiveDomeFossil, ITEM_DOME_FOSSIL, 1, MUS_RG_OBTAIN_KEY_ITEM
\tsetvar VAR_POX_GRANDPA_PROGRESS, 1
\tgoto Pox_CottageFossils
Pox_CottagePhanpy::
\tcheckspecies SPECIES_PHANPY
\tgoto_if_eq VAR_RESULT, TRUE, Pox_CottageGiveClawFossil
\tmsgbox Pox_Text_CottageAskPhanpy, MSGBOX_DEFAULT
\treleaseall
\tend
Pox_CottageGiveClawFossil::
\tcheckitemspace ITEM_CLAW_FOSSIL
\tgoto_if_eq VAR_RESULT, FALSE, Pox_NoRoom
\tgiveitem_msg Pox_Text_CottageGiveClawFossil, ITEM_CLAW_FOSSIL, 1, MUS_RG_OBTAIN_KEY_ITEM
\tsetvar VAR_POX_GRANDPA_PROGRESS, 2
\tgoto Pox_CottageFossils
Pox_CottageTeddiursa::
\tcheckspecies SPECIES_TEDDIURSA
\tgoto_if_eq VAR_RESULT, TRUE, Pox_CottageGiveRootFossil
\tmsgbox Pox_Text_CottageAskTeddiursa, MSGBOX_DEFAULT
\treleaseall
\tend
Pox_CottageGiveRootFossil::
\tcheckitemspace ITEM_ROOT_FOSSIL
\tgoto_if_eq VAR_RESULT, FALSE, Pox_NoRoom
\tgiveitem_msg Pox_Text_CottageGiveRootFossil, ITEM_ROOT_FOSSIL, 1, MUS_RG_OBTAIN_KEY_ITEM
\tsetvar VAR_POX_GRANDPA_PROGRESS, 3
\tgoto Pox_CottageFossils
Pox_CottageYanma::
\tcheckspecies SPECIES_YANMA
\tgoto_if_eq VAR_RESULT, TRUE, Pox_CottageGiveHelixFossil
\tmsgbox Pox_Text_CottageAskYanma, MSGBOX_DEFAULT
\treleaseall
\tend
Pox_CottageGiveHelixFossil::
\tcheckitemspace ITEM_HELIX_FOSSIL
\tgoto_if_eq VAR_RESULT, FALSE, Pox_NoRoom
\tgiveitem_msg Pox_Text_CottageGiveHelixFossil, ITEM_HELIX_FOSSIL, 1, MUS_RG_OBTAIN_KEY_ITEM
\tsetvar VAR_POX_GRANDPA_PROGRESS, 4
\tgoto Pox_CottageFossils
Pox_CottageMagikarp::
\tcheckspecies SPECIES_MAGIKARP
\tgoto_if_eq VAR_RESULT, TRUE, Pox_CottageGiveOldAmber
\tmsgbox Pox_Text_CottageAskMagikarp, MSGBOX_DEFAULT
\treleaseall
\tend
Pox_CottageGiveOldAmber::
\tcheckitemspace ITEM_OLD_AMBER
\tgoto_if_eq VAR_RESULT, FALSE, Pox_NoRoom
\tgiveitem_msg Pox_Text_CottageGiveOldAmber, ITEM_OLD_AMBER, 1, MUS_RG_OBTAIN_KEY_ITEM
\tsetvar VAR_POX_GRANDPA_PROGRESS, 5
\tgoto Pox_CottageFossils''')
finish()
speech('Pox_Text_Cottage', "I'm BILL's grandfather. My grandson designed the POKéMON Storage System on the PC. He's away on a project right now.|This EEVEE needs a good TRAINER. Take it!")
for name,text in [
 ('CottageAskRalts','I\'d love to see a RALTS. Bring one along sometime.'),
 ('CottageGiveDomeFossil','Ah, RALTS! Just as I hoped. Please take this DOME FOSSIL.'),
 ('CottageAskPhanpy','Next, I\'d love to see a PHANPY. Bring one along.'),
 ('CottageGiveClawFossil','What a fine PHANPY! Please take this CLAW FOSSIL.'),
 ('CottageAskTeddiursa','Now I\'d love to see a TEDDIURSA. Bring one along.'),
 ('CottageGiveRootFossil','TEDDIURSA is delightful! Please take this ROOT FOSSIL.'),
 ('CottageAskYanma','Next, I\'d love to see a YANMA. Bring one along.'),
 ('CottageGiveHelixFossil','That\'s a splendid YANMA! Please take this HELIX FOSSIL.'),
 ('CottageAskMagikarp','Finally, I\'d love to see a MAGIKARP. Bring one along.'),
 ('CottageGiveOldAmber','MAGIKARP never disappoints! Please take this OLD AMBER.'),
 ('CottageFossilsDone','Thank you for showing me all those wonderful POKéMON!')]:
    speech('Pox_Text_'+name,text)
replace_npc('Route25_BillsHouse_hns',0,'Cottage')
# Direct return makes this unique interior safe without a dynamic-warp setup.
cottage=load_map('Route25_BillsHouse_hns')
cottage['object_events']=cottage['object_events'][:1]
cottage['warp_events']=[]
save_map('Route25_BillsHouse_hns',cottage)
add_npc('Route25_BillsHouse_hns','CottageExit',7,8)
travel('CottageExit','Route25_hns',85,14,'Safe travels!')
travel('CottageGuide','Route25_BillsHouse_hns',7,7,'The SEA COTTAGE is a short trip from here.',[badges[3]])
add_npc('FortreeCity','CottageGuide',7,7)

# Lavender / Pokemon Tower (Team Rocket II). The three grunts stand around
# MR. FUJI on the FRLG tower's 7F; plastic_ox/alpha/lavender.py places them,
# owns the tower floors, FUJI's rescue and the SURF KEY hand-off in his house.
lav1='FLAG_POX_HIDE_LAVENDER_GRUNT_1'
lav2='FLAG_POX_HIDE_LAVENDER_GRUNT_2'
tower_grunt_lines=[
    "Don't come any closer. We're asking the old man a few questions, that's all.|How do you move a POKéMON without moving the room it's in? He knows. He won't say.",
    "We were told to find a man, not a library. Every answer he gives is another stack of paper.|What does 'preserve a living state' even mean? You tell me!",
    "You got past both of them? Then you've seen it too, haven't you. The roads that weren't there last year.|We just want to know who did it before somebody else finds out first.",
]
# TowerGrunt3 (a later trainer id) is authored in lavender.py so the story
# trainer ids in this file keep their numbering.
for n,f,req in [(1,lav1,[badges[3]]),(2,lav2,[lav1])]:
    battle('TowerGrunt'+str(n),'GRUNT',tower_grunt_lines[n-1],[('Golbat',['Bite','Wing Attack','Confuse Ray']),('Weezing',['Sludge','Smokescreen','Self Destruct'])],35,f,req,
           extra='\tremoveobject VAR_LAST_TALKED',pic='Rocket Grunt M Frlg',cls='Team Rocket Frlg')
# The old teleport rooms keep their map-group slots (map numbers are save
# data); lavender.py empties them.
room_names += ['PlasticOx_PokemonTower', 'PlasticOx_FujiHouse']
for n,(x,y) in enumerate([(9,10),(13,8),(9,6)],1):
    manifest_event('PokemonTower_7F_Frlg','TowerGrunt'+str(n),x,y)
gift('Fuji','FUJI: One more thing. This EEVEE came to the house last winter and never left. I think it has been waiting for someone like you.|Take good care of it.',[fuji])

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
man=room('Mansion','CinnabarIsland_Frlg',None,objects=[npc('Archive1',3,13,'OBJ_EVENT_GFX_SCIENTIST'),npc('Archive2',7,9,'OBJ_EVENT_GFX_SCIENTIST'),npc('Archive3',5,2,'OBJ_EVENT_GFX_SCIENTIST'),npc('Entei',3,9,'OBJ_EVENT_GFX_MAN_3',entei)],return_xy=(14,6))
guide('CinnabarIsland_Frlg',0,'MansionGuide',man,'The MANSION archives are sealed. BLAINE has the key.',[keyflag])

# Pox_SpaceReport (sets FLAG_POX_STORY_SPACE_CENTER) is authored in weather_institute.py.
gift('Space','This EEVEE helped us study adaptation. Our observations are complete. Please take it on your journey.',[space])
replace_npc('MossdeepCity_SpaceCenter_1F',0,'SpaceReport',hidden='FLAG_POX_HIDE_STORY_NPCS')
add_npc('MossdeepCity_SpaceCenter_1F','Space',5,7,'OBJ_EVENT_GFX_SCIENTIST')

silphgrunts=[]
for n in range(1,4):
    f='FLAG_POX_HIDE_SILPH_GRUNT_'+str(n)
    req=[space] if n==1 else [silphgrunts[-1]]
    silphgrunts.append(f)
    battle('SilphGrunt'+str(n),'GRUNT',["These terminals won't obey us. But the BOSS will make this system his!","Keep away from the server room! I just got the cables untangled.","You got past two of us? The BOSS won't like this one bit!"][n-1],[('Muk',['Sludge Bomb','Minimize','Body Slam']),('Golbat',['Bite','Confuse Ray','Wing Attack'])],48,f,req,pic='Team Aqua M',cls='Team Aqua')
gio='FLAG_POX_HIDE_SILPH_GIOVANNI'
battle('Giovanni','GIOVANNI',"We did not make this world. We followed a signal, then the old man's research.|A system that can rearrange a region can give its owner anything. Stand aside!",[('Nidoking',['Earthquake','Ice Beam','Thunderbolt']),('Kangaskhan',['Return','Shadow Ball','Fake Out']),('Dugtrio',['Earthquake','Rock Slide','Aerial Ace']),('Rhydon',['Earthquake','Rock Slide','Megahorn'])],52,gio,[silphgrunts[-1]],pic='Leader Giovanni Frlg')
beat('SilphCore','TERMINAL: ADAPTIVE TRAINER SYSTEM.|Battle profiles: BLUE, LANCE, STEVEN, WALLACE. Objective: improve training conditions.|Habitat isolation detected. Regional transfer links reconciled. Environmental restructuring active.|You isolate the environmental controls. The transfer links fall silent.|The existing region remains. Its boundaries have stopped moving.',silph,[gio])
sroom=room('Silph','SaffronCity_hns',None,objects=[npc('SilphGrunt1',3,13,'OBJ_EVENT_GFX_ROCKET_GRUNT_M',silphgrunts[0]),npc('SilphGrunt2',7,13,'OBJ_EVENT_GFX_ROCKET_GRUNT_M',silphgrunts[1]),npc('SilphGrunt3',3,9,'OBJ_EVENT_GFX_ROCKET_GRUNT_M',silphgrunts[2]),npc('Giovanni',7,9,'OBJ_EVENT_GFX_MAN_3',gio),npc('SilphCore',5,2,'OBJ_EVENT_GFX_SCIENTIST')],return_xy=(26,16))
guide('SaffronCity_hns',1,'SilphGuide',sroom,'SILPH needs help. BRUNO is accepting challenges at the DOJO, and the northern road leads to CLAIR in BLACKTHORN.|You can choose where to go first.',[space])

# Travel services join the currently disconnected demo legs. Prerequisites
# remain at the objectives as well as at these connections.
links=[('RustboroCity',0,'MoonRoad','MtMoon_Cave_hns',10,11,'The mountain trail leads to MT. MOON.',[badges[0]]),
 ('MtMoon_Cave_hns',None,'GoldenrodRoad','GoldenrodCity_hns',25,14,'The road is clear to GOLDENROD.',[moon]),
 ('GoldenrodCity_hns',1,'ParkRoad','NationalPark_Normal_hns',39,21,'Take a break at the NATIONAL PARK before ECRUTEAK.',[badges[1]]),
 ('NationalPark_Normal_hns',0,'EcruteakRoad','EcruteakCity_hns',35,44,'ECRUTEAK lies beyond the park.',[badges[1]]),
 ('EcruteakCity_hns',2,'WeatherRoad','Route119_WeatherInstitute_1F',6,8,'The WEATHER INSTITUTE is asking for a field assistant.',[badges[2]]),
 ('FortreeCity',None,'LavenderRoad','LavenderTown_hns',12,11,'The eastern road reaches LAVENDER.',[badges[3]]),
 ('LavenderTown_hns',2,'CinnabarRoad','CinnabarIsland_Frlg',12,12,'A boat is leaving for CINNABAR.',[fuji]),
 ('CinnabarIsland_Frlg',None,'MossdeepRoad','MossdeepCity',38,13,'Our next port is MOSSDEEP.',[mansion]),
 ('MossdeepCity',0,'SaffronRoad','SaffronCity_hns',16,23,'The mainland service goes to SAFFRON.',[space]),
 ('SaffronCity_hns',2,'BlackthornRoad','BlackthornCity_hns',16,29,'The northern road to BLACKTHORN is open. CLAIR welcomes challengers whenever you are ready.',northern_ou),
 ('BlackthornCity_hns',1,'LeagueRoad','IndigoPlateau_hns',11,13,'The LEAGUE approach is open to holders of all eight BADGES.',badges),]
for town,index,name,dest,x,y,text,req in links:
    travel(name,dest,x,y,text,req)
    if index is not None:
        replace_npc(town,index,name)
    else:
        add_npc(town,name,*{'MtMoon_Cave_hns':(11,10),'FortreeCity':(8,7),'CinnabarIsland_Frlg':(11,12)}[town])

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

# Visible Institute/Space Center staff and visitors each get a line that fits
# their sprite (children are on a field trip, not running the lab).
FACILITY_LINES = {
    ('Route119_WeatherInstitute_1F',2): "The barometer on this floor gets read every hour. I've had the 3 a.m. reading four nights running.",
    ('Route119_WeatherInstitute_1F',3): "Rain gauges from ROUTE 119 come back full of mud. Washing them is half my job.",
    ('Route119_WeatherInstitute_1F',4): "We're here on a school field trip! Teacher says if we behave we get to watch the weather balloon go up!",
    ('Route119_WeatherInstitute_2F',3): "These printouts track wind over FORTREE. Lately the lines wobble in ways our models never drew.",
    ('Route119_WeatherInstitute_2F',5): "The coffee machine's broken again. Forecasting runs on coffee, so… expect clouds.",
    ('MossdeepCity_SpaceCenter_1F',1): "Launch windows depend on the wind high up. We trade data with the WEATHER INSTITUTE every morning.",
    ('MossdeepCity_SpaceCenter_1F',2): "I ferry rocket parts over from the mainland. Strangest cargo I've ever tied down on deck.",
    ('MossdeepCity_SpaceCenter_1F',3): "I've watched every launch from this bench since they built the place. The rumble still rattles my teeth.",
    ('MossdeepCity_SpaceCenter_1F',4): "The gift shop sold out of rocket keychains again. My kids won't forgive me if I go home without one.",
    ('MossdeepCity_SpaceCenter_1F',9): "When I grow up, I'm gonna ride a rocket! Mom says I have to eat my vegetables first.",
    ('MossdeepCity_SpaceCenter_1F',10): "STEVEN: Meteorites tell you where a world has been. I came to see the ones kept here.",
    ('MossdeepCity_SpaceCenter_2F',0): "Dad brought me to look through the telescope! I saw a crater on the moon. It looked like a cookie!",
    ('MossdeepCity_SpaceCenter_2F',1): "I donated the telescope on this floor. Do have a look. The view over the strait is lovely.",
    ('MossdeepCity_SpaceCenter_2F',2): "Satellite pictures of the coast came back fuzzy again. We've recalibrated twice this week.",
    ('MossdeepCity_SpaceCenter_2F',3): "STEVEN: From up here you can see all of MOSSDEEP's shoreline. I never tire of it.",
}
for (native,i),line in FACILITY_LINES.items():
    start(f'Facility_{native}_{i}')
    emit(f'\tmsgbox Pox_Text_Facility_{native}_{i}, MSGBOX_DEFAULT')
    finish()
    speech(f'Pox_Text_Facility_{native}_{i}', line)

# Preserve the Institute/Space Center architecture while removing the unrelated
# Aqua/Magma occupation scripts and their trainer objects from these chapters.
for native in ['Route119_WeatherInstitute_1F','Route119_WeatherInstitute_2F',
               'MossdeepCity_SpaceCenter_1F','MossdeepCity_SpaceCenter_2F']:
    data=load_map(native)
    data['coord_events']=[]
    for i,obj in enumerate(data['object_events']):
        if not obj['script'].startswith('Pox_') or obj['script'] == 'Pox_FacilityWorker' or obj['script'].startswith('Pox_Facility_'):
            obj['script']='Pox_FacilityWorker'
            obj['trainer_type']='TRAINER_TYPE_NONE'
            if any(v in obj['graphics_id'] for v in ['AQUA','MAGMA','MAXIE','SHELLY']):
                obj['flag']='FLAG_POX_HIDE_UNUSED_ACTOR'
            elif (native,i) in FACILITY_LINES:
                obj['script']=f'Pox_Facility_{native}_{i}'
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
whirl=room('WhirlIslands','CinnabarIsland_Frlg','WhirlItem',return_xy=(12,12))
add_npc('CinnabarIsland_Frlg','WhirlGuide',13,12)
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

# Append PU opponents after the stable story roster; their IDs follow the LC
# route block, never renumbering victory flags in existing saves.
pu_trainer_start = len(trainers)
pu_trainers = [
    ('PU_ROUTE33', 'ANTHONY', 'Route33_hns', 0, 16, 'Hiker', 'Hiker', 'OBJ_EVENT_GFX_HIKER',
     [('Geodude',['Rock Throw','Defense Curl','Magnitude']),('Spinda',['Psybeam','Dizzy Punch','Teeter Dance'])],
     'The mountain made us tough. Show me what you found in the cave!', 'A steady pace gets you up any mountain.'),
    ('PU_ROUTE35', 'BROOKE', 'Route35_hns', 0, 18, 'Picnicker', 'Picnicker', 'OBJ_EVENT_GFX_PICNICKER',
     [('Nidorina',['Double Kick','Poison Sting','Bite']),('Farfetch\'d',['Aerial Ace','Fury Attack','Sand Attack'])],
     'The city is fun, but my partners prefer the meadow!', 'Different habitats make a balanced team.'),
    ('PU_PARK', 'WILLIAM', 'NationalPark_Normal_hns', 4, 19, 'Bug Catcher', 'Bug Catcher', 'OBJ_EVENT_GFX_BUG_CATCHER',
     [('Ledian',['Light Screen','Comet Punch','Supersonic']),('Butterfree',['Confusion','Stun Spore','Gust'])],
     'I train the bugs I catch here. Let me show you their strength!', 'The Contest is for catching. This meadow is for training!'),
    ('PU_ROUTE36', 'MARK', 'Route36_hns', 3, 20, 'Psychic', 'Psychic M', 'OBJ_EVENT_GFX_PSYCHIC_M',
     [('Natu',['Night Shade','Confuse Ray','Peck']),('Drowzee',['Confusion','Headbutt','Hypnosis']),('Baltoy',['Psybeam','Rock Tomb','Rapid Spin'])],
     'These old trees have seen so many battles. Ours will be another!', 'That strange tree ahead seems to move when nobody watches.'),
]
for name, display, mapname, index, level, cls, pic, gfx, team, intro, after in pu_trainers:
    tid = trainer(name, display, team, level, pic, cls)
    contest_guard = ''  # Contest protection lives in battle_setup/trainer_see.
    emit(f'Pox_{name}::\n{contest_guard}\ttrainerbattle_single {tid}, Pox_Text_{name}, {defeat_label(name)}\n\tmsgbox Pox_Text_{name}_After, MSGBOX_AUTOCLOSE\n\tend')
    speech('Pox_Text_'+name, intro)
    speech('Pox_Text_'+name+'_After', after)
    if name in DEFEAT_LINES:
        speech(defeat_label(name), DEFEAT_LINES[name])
    replace_npc(mapname, index, name, gfx, '0')
    data = load_map(mapname)
    data['object_events'][index].update(trainer_type='TRAINER_TYPE_NONE' if name == 'PU_PARK' else 'TRAINER_TYPE_NORMAL', trainer_sight_or_berry_tree_id='3')
    save_map(mapname, data)

# The bottle is a dedicated persistent key item, available only after Whitney.
start('SquirtBottle')
# Run 5 warp/Sudowoodo fix pass.  B cannot answer NO on a field YES/NO box in
# this build, and giveitem fails silently, so both paths changed here rather
# than only in the generated .inc.
emit('''\tgoto_if_unset FLAG_BADGE02_GET, Pox_SquirtBottle_Wait
\tcheckitem ITEM_SQUIRT_BOTTLE
\tgoto_if_eq VAR_RESULT, TRUE, Pox_SquirtBottle_Have
\tgiveitem ITEM_SQUIRT_BOTTLE
\tgoto_if_eq VAR_RESULT, FALSE, Pox_SquirtBottle_Full
Pox_SquirtBottle_Have::
\tmsgbox Pox_Text_SquirtBottle, MSGBOX_DEFAULT''')
finish()
emit('Pox_SquirtBottle_Wait::\n\tmsgbox Pox_Text_SquirtBottle_Wait, MSGBOX_DEFAULT\n\treleaseall\n\tend')
emit('Pox_SquirtBottle_Full::\n\tmsgbox Pox_Text_SquirtBottle_Full, MSGBOX_DEFAULT\n\treleaseall\n\tend')
speech('Pox_Text_SquirtBottle_Wait', 'The odd tree on ROUTE 36 hates water. Beat WHITNEY, then I can lend you my SQUIRTBOTTLE.')
speech('Pox_Text_SquirtBottle', 'Use my SQUIRTBOTTLE when you examine the odd tree on ROUTE 36. Be ready for a battle!')
speech('Pox_Text_SquirtBottle_Full', 'There is no room in your KEY ITEMS POCKET right now. Come back once you have made some space.')
add_npc('GoldenrodCity_hns', 'SquirtBottle', 27, 15, 'OBJ_EVENT_GFX_WOMAN_2', '0')
manifest_event('GoldenrodCity_FlowerShop_hns', 'Pox_SquirtBottle', 2, 4)
manifest_event('Route36_hns', 'Pox_Sudowoodo', 39, 19)
start('Sudowoodo')
# Gen 2/4 ask nothing at all before the Sudowoodo appears, and this build's
# field YES/NO box cannot be answered with B, so there is no question.
emit('''\tgoto_if_set FLAG_POX_SUDOWOODO_CLEARED, Pox_Release
\tgoto_if_unset FLAG_BADGE02_GET, Pox_Sudowoodo_Wait
\tcheckitem ITEM_SQUIRT_BOTTLE
\tgoto_if_eq VAR_RESULT, FALSE, Pox_Sudowoodo_Wait
\tmsgbox Pox_Text_Sudowoodo, MSGBOX_DEFAULT
\tsetwildbattle SPECIES_SUDOWOODO, 20, ITEM_NONE
\tspecial PlasticOx_PrepareSudowoodoMoves
\tdowildbattle
\tspecialvar VAR_RESULT, GetBattleOutcome
\tgoto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Pox_Sudowoodo_Cleared
\tgoto_if_ne VAR_RESULT, B_OUTCOME_WON, Pox_Release
Pox_Sudowoodo_Cleared::
\tsetflag FLAG_POX_SUDOWOODO_CLEARED
\tremoveitem ITEM_SQUIRT_BOTTLE
\tremoveobject VAR_LAST_TALKED''')
finish()
emit('Pox_Sudowoodo_Wait::\n\tmsgbox Pox_Text_Sudowoodo_Wait, MSGBOX_DEFAULT\n\treleaseall\n\tend')
speech('Pox_Text_Sudowoodo', 'You spray the odd tree with the SQUIRTBOTTLE. It shivers!')
speech('Pox_Text_Sudowoodo_Wait', 'This tree feels like stone! Someone near WHITNEY\'s GYM has a SQUIRTBOTTLE that might help.')

# Append the new floor only after the existing story rooms, preserving their
# stable map numbers in existing saves.
room_names.append('PlasticOx_BurnedTowerB1F')
manifest.append(('PlasticOx_BurnedTowerB1F', 8, 9, 'BurnedTower'))
emit(TOWER_MOVEMENTS)
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

# IDs are independent of event order. Keep retired allocations reserved so
# moving a gift or adding a scene cannot reinterpret an existing save flag.
legacy_grandpa = '''
// Legacy Bill's-grandfather reward flags. New scripts consolidate the ordered
// rewards into VAR_POX_GRANDPA_PROGRESS. Keep these safe old-save inputs
// reserved; 0x071 is deliberately omitted because retained Cave of Origin
// scripts read that vanilla flag and therefore make it unsafe to repurpose.
#define FLAG_POX_LEGACY_GRANDPA_DOME_FOSSIL 0x054
#define FLAG_POX_LEGACY_GRANDPA_CLAW_FOSSIL 0x055
#define FLAG_POX_LEGACY_GRANDPA_ROOT_FOSSIL 0x068
#define FLAG_POX_LEGACY_GRANDPA_OLD_AMBER   0x096
'''
put('include/constants/plastic_ox_story.h','#ifndef GUARD_PLASTIC_OX_STORY_CONSTANTS_H\n#define GUARD_PLASTIC_OX_STORY_CONSTANTS_H\n\n// Generated from plastic_ox/alpha/story_flags.json; IDs must remain stable.\n// Reserved unused general flags. Never allocate trainer/daily flags here.\n'+''.join(f'#define {f} {value}\n' for f,value in flag_allocations.items())+legacy_grandpa+'\n#endif\n')
path='include/constants/plastic_ox_flags.h'
s=read(path)
if '#include "constants/plastic_ox_story.h"' not in s:
    s=s.replace('#define GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H','#define GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H\n\n#include "constants/plastic_ox_story.h"')
put(path,s)
path='include/constants/opponents.h'
s=read(path)
# Every other TRAINER_PLASTIC_OX_* id in the block (route, Mt. Moon, Johto,
# sage, ridge, tournament, Ecruteak staff, ...) is owned by its own module or
# by apply_trainer_teams_v2.py. Keep those lines verbatim, comments included.
story_ids={tid for tid,_ in trainers}
old_block=re.search(r'// Plastic Ox story trainers\.\n(.*?)// End Plastic Ox story trainers\.\n',s,flags=re.S)
route_defs=[line+'\n' for line in (old_block[1].splitlines() if old_block else [])
            if line.startswith('#define TRAINER_PLASTIC_OX_') and line.split()[1] not in story_ids]
defs='// Plastic Ox story trainers.\n'+''.join(f'#define {tid} {857+i if i < pu_trainer_start else 895+i-pu_trainer_start}\n' for i,(tid,_) in enumerate(trainers))+''.join(route_defs)+'// End Plastic Ox story trainers.\n'
if old_block:
    s=s[:old_block.start()]+defs+s[old_block.end():]
else:
    s=s.replace('// Plastic Ox trainer victories above ID 856',defs+'\n// Plastic Ox trainer victories above ID 856')
route_ids=[int(line.split()[2]) for line in route_defs]
trainer_count=max([895+len(trainers)-pu_trainer_start, *(value + 1 for value in route_ids)])
s=re.sub(r'#define TRAINERS_COUNT_EMERALD\s+\d+',f'#define TRAINERS_COUNT_EMERALD {trainer_count}',s)
s=re.sub(r'#define MAX_TRAINERS_COUNT_EMERALD\s+\d+',f'#define MAX_TRAINERS_COUNT_EMERALD {trainer_count}',s)
assert pu_trainer_start == 28 and len(trainers) == 32
put(path,s)
# This generator owns each story trainer's header (name, class, pic, music,
# AI). Party bodies are authored by plastic_ox/tools/apply_trainer_teams_v2.py
# and stay as checked in; the placeholder party above is only used for a
# trainer that has no block yet. Every other block is left untouched.
path='src/data/trainers.party'
s=read(path)
for tid,text in trainers:
    head,_,body=text.partition('\n\n')
    m=re.search(r'^=== '+re.escape(tid)+r' ===\n.*?\n\n',s,flags=re.M|re.S)
    if m:
        s=s[:m.start()]+head+'\n\n'+s[m.end():]
    else:
        s=s.rstrip('\n')+'\n\n'+text
put(path,s)
# The Kimono troupe trainer has a fixed id after the existing ones (the story
# block above numbers its trainers by position, so it can't join that list).
# Its party body is authored in plastic_ox/tools/authored_trainers.party.
path='include/constants/opponents.h'
s=read(path)
if f'#define {KIMONO_TROUPE} ' not in s:
    s=s.replace('// End Plastic Ox story trainers.',f'#define {KIMONO_TROUPE} {KIMONO_TROUPE_ID}\n// End Plastic Ox story trainers.')
for c in ['TRAINERS_COUNT_EMERALD','MAX_TRAINERS_COUNT_EMERALD']:
    s=re.sub(r'(#define '+c+r'\s+)(\d+)',lambda m:m[1]+str(max(KIMONO_TROUPE_ID+1,int(m[2]))),s)
put(path,s)
path='src/data/trainers.party'
s=read(path)
m=re.search(r'^=== '+KIMONO_TROUPE+r' ===\n.*?\n\n',s,flags=re.M|re.S)
head=f'=== {KIMONO_TROUPE} ===\n{KIMONO_TROUPE_HEADER}\n\n'
if m:
    s=s[:m.start()]+head+s[m.end():]
else:
    s=s.rstrip('\n')+'\n\n'+head+'Eevee\nLevel: 27\n- Quick Attack\n'
put(path,s)
put('plastic_ox/alpha/story_manifest.json',json.dumps(dict(events=[dict(map=m,x=x,y=y,script='Pox_'+s) for m,x,y,s in manifest],flags=flags,trainers=[t for t,_ in trainers],rooms=room_names),indent=2)+'\n')

# Apply physical topology last so room/story regeneration cannot restore old
# entrances, callbacks, or travel bypasses.
from region_v7 import apply_region
apply_region(read, put)


def keep_stable_trainer_layout():
    """Area modules (mt_moon, johto_outdoors, cinnabar, ...) re-append their own
    trainer defines and blocks. IDs are save data and party bodies belong to
    plastic_ox/tools/apply_trainer_teams_v2.py, so keep the checked-in define
    order and every checked-in party body; generators own only the headers and
    any trainer that does not exist yet (appended at the end)."""
    path='include/constants/opponents.h'
    disk=Path(path).read_text()
    pat=r'// Plastic Ox story trainers\.\n(.*?)// End Plastic Ox story trainers\.\n'
    new=re.search(pat,read(path),flags=re.S)
    old=re.search(pat,disk,flags=re.S)
    if new and old:
        ident=lambda line: line.split()[1] if line.startswith('#define ') else None
        new_lines={ident(l):l for l in new[1].splitlines() if ident(l)}
        old_lines=[l for l in old[1].splitlines() if ident(l)]
        lines=[l if l.split()[:3]==new_lines[ident(l)].split()[:3] else new_lines[ident(l)] for l in old_lines if ident(l) in new_lines]
        lines+= [l for k,l in new_lines.items() if k not in {ident(o) for o in old_lines}]
        s=read(path)
        s=s[:new.start()]+'// Plastic Ox story trainers.\n'+''.join(l+'\n' for l in lines)+'// End Plastic Ox story trainers.\n'+s[new.end():]
        count=max(int(l.split()[2]) for l in lines)+1
        for c in ['TRAINERS_COUNT_EMERALD','MAX_TRAINERS_COUNT_EMERALD']:
            s=re.sub(r'(#define '+c+r'\s+)\d+',lambda m:m[1]+str(count),s)
        put(path,s)
    path='src/data/trainers.party'
    split=lambda text: re.split(r'(?=^=== TRAINER_)',text,flags=re.M)
    disk_blocks=split(Path(path).read_text())
    gen_blocks=split(read(path))
    key=lambda b: b.split(' ===',1)[0] if b.startswith('=== TRAINER_') else None
    gen={key(b):b for b in gen_blocks if key(b)}
    out=[]
    seen=set()
    for b in disk_blocks:
        k=key(b)
        if k is None:
            out.append(b)
            continue
        if k not in gen:
            continue
        seen.add(k)
        g=gen[k]
        if k.startswith('=== TRAINER_PLASTIC_OX_'):
            head=g.split('\n\n',1)[0]
            body=b.split('\n\n',1)[1] if '\n\n' in b else ''
            out.append(head+'\n\n'+body)
        else:
            out.append(g if g.rstrip()!=b.rstrip() else b)
    extra=[gen[k] for k in gen if k not in seen]
    text=''.join(out)
    if extra:
        text=text.rstrip('\n')+'\n\n'+''.join(extra)
    put(path,text)


keep_stable_trainer_layout()
manifest=[(m,x,y,s) for m,x,y,s in manifest if any(o.get('script') == 'Pox_'+s and (o['x'],o['y']) == (x,y) for o in load_map(m)['object_events'])]
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
