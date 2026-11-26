"""Lavender Town and the FRLG Pokemon Tower: Team Rocket II and MR. FUJI.

Installed last by region_v7.apply_region, so it owns the final shape of:

* LavenderTown_hns doors: the HNS radio station door (22,6) is the POKeMON
  TOWER, the volunteer-house door (8,13) is FUJI's house (the FRLG Volunteer
  Pokemon House) and the HNS House3 door (10,19) takes the FRLG House1.
* PokemonTower_1F..7F_Frlg: mourners and channelers who no longer battle, the
  original floor-to-floor stairs, item balls on their own Plastic Ox flags, and
  three Rocket grunts around FUJI on 7F (trainers come from build_story.py's
  TowerGrunt1..3 battles).
* FUJI's rescue: talking to him on 7F after the third grunt walks the player
  home; in the house he gives the SURF KEY, sets FLAG_POX_STORY_FUJI (which
  opens Route 8) and offers the Eevee (Pox_Fuji, build_story.py).
* The Soul House door (22,19) leads into the retired PlasticOx_FujiHouse room
  (HNS generic house), now the town's small memorial house.
* The old teleport room PlasticOx_PokemonTower is an empty placeholder that
  keeps its map number for existing saves.

Story source: plastic_ox/story/locations/lavender-town.md.
"""
import json
import re
import textwrap

TOWN = 'LavenderTown_hns'
TOWN_ID = 'MAP_LAVENDER_TOWN_HNS'
HOUSE = 'LavenderTown_VolunteerPokemonHouse_Frlg'
P = 'PoxLavender_'

# New persistent flags (POX_EXT pool; see the plastic-ox-flags skill).
EXT_FLAGS = [
    ('FLAG_POX_FUJI_RESCUED', 0, 'Pokemon Tower 7F: FUJI walked home after the three grunts.'),
    ('FLAG_POX_HIDE_HOUSE_FUJI', 1, "FUJI's house: hides FUJI until he is rescued (set on transition)."),
    ('FLAG_POX_HIDE_LAVENDER_GRUNT_3', 2, 'Pokemon Tower 7F: third Rocket grunt beaten.'),
    ('FLAG_POX_HIDE_TOWER_3F_ESCAPE_ROPE', 3, 'Pokemon Tower item balls.'),
    ('FLAG_POX_HIDE_TOWER_4F_ELIXIR', 4, None),
    ('FLAG_POX_HIDE_TOWER_4F_AWAKENING', 5, None),
    ('FLAG_POX_HIDE_TOWER_4F_GREAT_BALL', 6, None),
    ('FLAG_POX_HIDE_TOWER_5F_NUGGET', 7, None),
    ('FLAG_POX_HIDE_TOWER_5F_CLEANSE_TAG', 8, None),
    ('FLAG_POX_HIDE_TOWER_6F_RARE_CANDY', 9, None),
    ('FLAG_POX_HIDE_TOWER_6F_X_ACCURACY', 10, None),
]
ITEM_FLAGS = {
    'FLAG_HIDE_POKEMON_TOWER_3F_ESCAPE_ROPE': 'FLAG_POX_HIDE_TOWER_3F_ESCAPE_ROPE',
    'FLAG_HIDE_POKEMON_TOWER_4F_ELIXIR': 'FLAG_POX_HIDE_TOWER_4F_ELIXIR',
    'FLAG_HIDE_POKEMON_TOWER_4F_AWAKENING': 'FLAG_POX_HIDE_TOWER_4F_AWAKENING',
    'FLAG_HIDE_POKEMON_TOWER_4F_GREAT_BALL': 'FLAG_POX_HIDE_TOWER_4F_GREAT_BALL',
    'FLAG_HIDE_POKEMON_TOWER_5F_NUGGET': 'FLAG_POX_HIDE_TOWER_5F_NUGGET',
    'FLAG_HIDE_POKEMON_TOWER_5F_CLEANSE_TAG': 'FLAG_POX_HIDE_TOWER_5F_CLEANSE_TAG',
    'FLAG_HIDE_POKEMON_TOWER_6F_RARE_CANDY': 'FLAG_POX_HIDE_TOWER_6F_RARE_CANDY',
    'FLAG_HIDE_POKEMON_TOWER_6F_X_ACCURACY': 'FLAG_POX_HIDE_TOWER_6F_X_ACCURACY',
}

# Lavender speaks quietly: short sentences, no exclamation marks.
# Each entry: label -> text, or label -> (text before FUJI is rescued, text after).
LINES = {
    # --- town ---
    'Caretaker': ("We keep the candles low in the tower. The POKéMON there don't like a bright room.|Some men in black went up three days ago. MR. FUJI was already inside, praying. Neither has come down.",
                  "MR. FUJI is home. I saw him on the steps this morning, slower than usual.|We relit the candles on the top floor. It took most of the day."),
    'Neighbour': ("I live next door to MR. FUJI. His POKéMON have been crying at the window every night.|He always comes home by supper. Always.",
                  "MR. FUJI is back. I brought him soup and he fell asleep before it cooled.|The POKéMON stopped crying. That is how I knew before anyone told me."),
    'Mourner': "My NIDORINO is buried on the fourth floor. Thirty years now.|I don't cry anymore. I just like to tell him what the weather is doing.",
    'Clerk': "Ferry's not running. Hasn't been since the roads moved.|Come back when you're famous. They'll find a boat for you then.",
    'Fisherman': "I used to fish off the end of the harbour road. Now there's a barrier and a man with a clipboard.|The fish didn't go anywhere. I checked.",
    'Kid': "My dad says the big boat goes to an island full of strong TRAINERS.|He says only CHAMPIONS get a ticket. I'm going to be one.",
    # --- signs ---
    'TownSign': "LAVENDER TOWN\nThe Noble Purple Town",
    'TowerSign': "POKéMON TOWER\nBecalm the spirits of POKéMON.\\pPlease keep voices low.",
    'HouseSign': "VOLUNTEER POKéMON HOUSE\nMR. FUJI cares for POKéMON that\\pno longer have a home.",
    'SoulSign': "SOUL HOUSE\nA quiet place to remember\\pthe POKéMON who came before.",
    # --- Soul House (PlasticOx_FujiHouse) ---
    'SoulKeeper': ("I keep this little house for people who can't manage the tower stairs.|There are no graves here. Just names, and somewhere to sit.",
                   "MR. FUJI came by after he got home. He sat a long time and didn't say anything.|Then he swept the step. He always sweeps the step."),
    'SoulVisitor': "My grandmother wrote her BUTTERFREE's name on the wall here. I come to make sure it hasn't faded.|It hasn't. Somebody keeps tracing over it.",
    # --- tower 1F ---
    'T1Keeper': ("Welcome to the POKéMON TOWER. Visiting hours never end, but please don't run on the stairs.|Some men went up without signing the book. MR. FUJI is up there too.",
                 "MR. FUJI signed out this morning. He wrote, Thank you, in the margin. He's never done that before."),
    'T1Channeler': "...The spirits are restless today... They don't like the men upstairs...",
    'T1Woman1': "GROWLITHE was with me since I was a girl. I come every year on his birthday.|He'd be fifty now. Can you imagine.",
    'T1Woman2': "Have you come to pay your respects? Take your time. Nobody here is in a hurry.",
    'T1Man': "I don't know anyone buried here, honestly. I just started coming after I retired.|It's the only quiet room in the region.",
    # --- channelers 2F-6F (fragments) ---
    'T2Channeler': "...Shh... Do you hear them?... Someone is moving furniture upstairs...",
    'T3Channeler1': "...A candle leaned toward the stairs... then it went out...",
    'T3Channeler2': "...The ghosts were here before the town... They remember where the walls used to be...",
    'T3Channeler3': "...Paper... so much paper going up the stairs... and none coming down...",
    'T4Channeler1': "...I asked the spirits who the men are... The spirits asked me the same...",
    'T4Channeler2': "...A radio is playing in the empty room... It plays a station that isn't there...",
    'T4Channeler3': "...Don't step on the cracked stone... a CUBONE's mother sleeps beneath it...",
    'T5Channeler1': "...Heavy footsteps... boots, not slippers... boots don't belong here...",
    'T5Channeler2': "...The old man hums when he prays... I haven't heard him humming...",
    'T5Channeler3': "...Wait... wait... I lost count of the stairs again...",
    'T5Channeler4': "...Whatever they are asking him, the ghosts don't want him to answer...",
    'T5Purifier': "This floor is purified. Rest here a while.|The POKéMON in your party will feel better.",
    'T6Channeler1': "...Turn back... no... keep going... he needs someone...",
    'T6Channeler2': "...They asked the ghosts how to bring a POKéMON back... The ghosts laughed...",
    'T6Channeler3': "...The top floor is very cold now... colder than the dead like it...",
    # --- Rocket grunts 1-2 are build_story.py's TowerGrunt1/2 ---
    # --- Rocket Executive PROTON: the last Rocket before FUJI (TOWERGRUNT3 id) ---
    'Grunt3Intro': "So you got past both of my grunts. I'm PROTON, an EXECUTIVE of TEAM ROCKET.|You've seen the roads that weren't there last year. We'll know who moved them before anyone else does.",
    'Grunt3Defeat': "Go on, then. But whatever's moving the roads, it isn't going to stop for you.",
    # --- FUJI ---
    'TowerFujiWaiting': "FUJI: Please, be careful. Those men are not cruel. They are frightened, and that is worse.",
    'TowerFujiRescued': "FUJI: Thank you. They kept me here three days, reading my own old notes back to me.|I am too tired to talk here. Come to my house, please. It is just below the hill.",
    'HouseFuji1': "FUJI: Forgive the state of the house. Sit, if you can find a chair.|Those men asked how to move a POKéMON without moving it, and how to keep a living thing exactly as it was.|I spent a life learning how to keep things. I never learned how to put them back.",
    'HouseFuji2': "Whatever is changing this land, it is not my work. I do not know what it is.|But the oldest records of that kind of research are on CINNABAR ISLAND. BLAINE keeps what is left of them.",
    'HouseFuji3': "SAFFRON is still closed. Take ROUTE 8 west; the UNDERGROUND PATH runs under the city to ROUTE 7.|From ROUTE 7, follow ROUTE 103 to the sea. This SURF KEY will carry you the rest of the way.",
    'HouseGirl': ("MR. FUJI went to the tower to pray and didn't come back. I fed everyone breakfast by myself.",
                  "MR. FUJI is home. He says I did a good job with breakfast. I did."),
    'HouseBoy': ("PSYDUCK keeps looking at the door. I told it MR. FUJI will be back soon. I hope I didn't lie.",
                 "PSYDUCK stopped looking at the door. Now it just looks at MR. FUJI."),
    'HouseYoungster': ("I came to help MR. FUJI with the POKéMON, but he's gone. There were men in black on the tower stairs.",
                       "Some men were asking MR. FUJI about old science. He wouldn't tell them. He wouldn't tell me either."),
}


def text(label, body):
    if '\n' in body:  # signs carry their own layout
        return f'{P}Text_{label}::\n\t.string "' + body.replace('\n', '\\n') + '$"\n'
    pages = []
    for paragraph in body.split('|'):
        lines = textwrap.wrap(paragraph, 32)
        pages.extend('\\n'.join(lines[i:i + 2]) for i in range(0, len(lines), 2))
    return f'{P}Text_{label}::\n\t.string "' + '\\p'.join(pages) + '$"\n'


def scripts():
    out = ['@ Generated by plastic_ox/alpha/lavender.py\n']
    texts = []
    for label, body in LINES.items():
        if label.endswith('Sign'):
            out.append(f'{P}{label}::\n\tmsgbox {P}Text_{label}, MSGBOX_SIGN\n\tend\n')
            texts.append(text(label, body))
        elif isinstance(body, tuple):
            out.append(f'{P}{label}::\n\tlock\n\tfaceplayer\n\tgoto_if_set FLAG_POX_FUJI_RESCUED, {P}{label}_After\n'
                       f'\tmsgbox {P}Text_{label}, MSGBOX_DEFAULT\n\trelease\n\tend\n'
                       f'{P}{label}_After::\n\tmsgbox {P}Text_{label}_After, MSGBOX_DEFAULT\n\trelease\n\tend\n')
            texts.append(text(label, body[0]))
            texts.append(text(label + '_After', body[1]))
        elif label.startswith(('TowerFuji', 'HouseFuji', 'Grunt3')):
            texts.append(text(label, body))
        else:
            out.append(f'{P}{label}::\n\tmsgbox {P}Text_{label}, MSGBOX_NPC\n\tend\n')
            texts.append(text(label, body))
    out.append(f'''@ Same shape as build_story.battle(): talking resumes an interrupted reward.
Pox_TowerGrunt3::
	goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End
	lockall
	goto_if_unset FLAG_POX_HIDE_LAVENDER_GRUNT_2, Pox_NotReady
	goto_if_set FLAG_POX_HIDE_LAVENDER_GRUNT_3, Pox_Done
	trainerbattle_single TRAINER_PLASTIC_OX_TOWERGRUNT3, {P}Text_Grunt3Intro, {P}Text_Grunt3Defeat, Pox_TowerGrunt3_Won
	goto Pox_TowerGrunt3_Won
Pox_TowerGrunt3_Won::
	setflag FLAG_POX_HIDE_LAVENDER_GRUNT_3
	removeobject VAR_LAST_TALKED
	releaseall
	end

@ 7F Rockets battle on sight. The object script must open with
@ trainerbattle so the engine can spot the player; talking to a beaten or
@ dormant one falls through to the story script (Done / NotReady).
{P}TowerGrunt1Sight::
	trainerbattle_single TRAINER_PLASTIC_OX_TOWERGRUNT1, Pox_Text_TowerGrunt1, Pox_Text_TowerGrunt1_Defeat, Pox_TowerGrunt1_Won
	goto Pox_TowerGrunt1
{P}TowerGrunt2Sight::
	trainerbattle_single TRAINER_PLASTIC_OX_TOWERGRUNT2, Pox_Text_TowerGrunt2, Pox_Text_TowerGrunt2_Defeat, Pox_TowerGrunt2_Won
	goto Pox_TowerGrunt2
{P}TowerGrunt3Sight::
	trainerbattle_single TRAINER_PLASTIC_OX_TOWERGRUNT3, {P}Text_Grunt3Intro, {P}Text_Grunt3Defeat, Pox_TowerGrunt3_Won
	goto Pox_TowerGrunt3

@ A grunt spots the player only while his story battle is due: story mode
@ (FLAG_POX_TRIGGERS_ENABLED), badge 4 (GRUNT 1's story prerequisite)
@ and not yet beaten (FLAG_POX_HIDE_LAVENDER_GRUNT_n, the real record). The
@ trainer flag is only the engine's "don't look" switch, recomputed on entry.
{P}Tower7FOnTransition::
	call {P}Tower7FGrunt1
	call {P}Tower7FGrunt2
	call {P}Tower7FGrunt3
	end
{P}Tower7FGrunt1::
	settrainerflag TRAINER_PLASTIC_OX_TOWERGRUNT1
	goto_if_unset FLAG_POX_TRIGGERS_ENABLED, {P}Return
	goto_if_unset FLAG_BADGE04_GET, {P}Return
	goto_if_set FLAG_POX_HIDE_LAVENDER_GRUNT_1, {P}Return
	cleartrainerflag TRAINER_PLASTIC_OX_TOWERGRUNT1
	return
{P}Tower7FGrunt2::
	settrainerflag TRAINER_PLASTIC_OX_TOWERGRUNT2
	goto_if_unset FLAG_POX_TRIGGERS_ENABLED, {P}Return
	goto_if_unset FLAG_BADGE04_GET, {P}Return
	goto_if_set FLAG_POX_HIDE_LAVENDER_GRUNT_2, {P}Return
	cleartrainerflag TRAINER_PLASTIC_OX_TOWERGRUNT2
	return
{P}Tower7FGrunt3::
	settrainerflag TRAINER_PLASTIC_OX_TOWERGRUNT3
	goto_if_unset FLAG_POX_TRIGGERS_ENABLED, {P}Return
	goto_if_unset FLAG_BADGE04_GET, {P}Return
	goto_if_set FLAG_POX_HIDE_LAVENDER_GRUNT_3, {P}Return
	cleartrainerflag TRAINER_PLASTIC_OX_TOWERGRUNT3
	return
{P}Return::
	return

{P}TowerFuji::
	lock
	faceplayer
	goto_if_unset FLAG_POX_HIDE_LAVENDER_GRUNT_3, {P}TowerFujiWaiting
	msgbox {P}Text_TowerFujiRescued, MSGBOX_DEFAULT
	closemessage
	setflag FLAG_POX_FUJI_RESCUED
	clearflag FLAG_POX_HIDE_HOUSE_FUJI
	warp MAP_LAVENDER_TOWN_VOLUNTEER_POKEMON_HOUSE, 4, 7
	waitstate
	release
	end
{P}TowerFujiWaiting::
	msgbox {P}Text_TowerFujiWaiting, MSGBOX_DEFAULT
	release
	end

{P}HouseOnTransition::
	call_if_unset FLAG_POX_FUJI_RESCUED, {P}HideHouseFuji
	call_if_set FLAG_POX_FUJI_RESCUED, {P}ShowHouseFuji
	end
{P}HideHouseFuji::
	setflag FLAG_POX_HIDE_HOUSE_FUJI
	return
{P}ShowHouseFuji::
	clearflag FLAG_POX_HIDE_HOUSE_FUJI
	return

@ The SURF KEY and FLAG_POX_STORY_FUJI (Route 8) come first; the Eevee offer
@ (Pox_Fuji in plastic_ox_story.inc) follows every time until it is accepted.
{P}HouseFuji::
	lock
	faceplayer
	goto_if_set FLAG_POX_STORY_FUJI, {P}HouseFujiGift
	msgbox {P}Text_HouseFuji1, MSGBOX_DEFAULT
	msgbox {P}Text_HouseFuji2, MSGBOX_DEFAULT
	msgbox {P}Text_HouseFuji3, MSGBOX_DEFAULT
	checkitem ITEM_SURF_KEY
	goto_if_eq VAR_RESULT, TRUE, {P}HouseFujiHasKey
	giveitem ITEM_SURF_KEY
	goto_if_eq VAR_RESULT, FALSE, {P}HouseFujiNoRoom
{P}HouseFujiHasKey::
	setflag FLAG_POX_STORY_FUJI
{P}HouseFujiGift::
	release
	goto Pox_Fuji
{P}HouseFujiNoRoom::
	release
	end
''')
    return '\n'.join(out) + '\n' + '\n'.join(texts)


def npc(gfx, x, y, script, flag='0', movement='MOVEMENT_TYPE_FACE_DOWN'):
    return dict(graphics_id=gfx, x=x, y=y, elevation=3, movement_type=movement,
                movement_range_x=0, movement_range_y=0, trainer_type='TRAINER_TYPE_NONE',
                trainer_sight_or_berry_tree_id='0', script=P + script, flag=flag)


def install(read, put):
    def load(name):
        return json.loads(read(f'data/maps/{name}/map.json'))

    def save(name, data):
        put(f'data/maps/{name}/map.json', json.dumps(data, indent=2) + '\n')

    # --- flags ---
    path = 'include/constants/plastic_ox_flags.h'
    header = read(path)
    block = ''.join((f'// {comment}\n' if comment else '') + f'#define {name} (POX_EXT_FLAGS_START + {n})\n'
                    for name, n, comment in EXT_FLAGS)
    begin, end = '// Lavender / Pokemon Tower (plastic_ox/alpha/lavender.py).\n', '// End Lavender flags.\n'
    header = re.sub(re.escape(begin) + '.*?' + re.escape(end) + '\n?', '', header, flags=re.S)
    header = header.replace('#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H',
                            begin + block + end + '\n#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H')
    put(path, header)

    # --- town: real doors, no teleport guides ---
    town = load(TOWN)
    warps = town['warp_events']
    door = lambda x, y, dest, wid: dict(x=x, y=y, elevation=3, dest_map=dest, dest_warp_id=wid)
    warps[2] = door(8, 13, 'MAP_LAVENDER_TOWN_VOLUNTEER_POKEMON_HOUSE', '1')
    del warps[4:]
    warps.append(door(22, 6, 'MAP_POKEMON_TOWER_1F', '1'))       # warp 4
    warps.append(door(10, 19, 'MAP_LAVENDER_TOWN_HOUSE1', '1'))   # warp 5
    warps.append(door(22, 19, 'MAP_PLASTIC_OX_FUJI_HOUSE', '0'))  # warp 6: Soul House
    keep = []
    for o in town['object_events']:
        s = o['script']
        if s in ('Pox_TowerGuide', 'Pox_FujiGuide') or s.startswith(P):
            continue
        if s == 'LavenderTown_EventScript_Npc4':
            continue
        if s.startswith('LavenderTown_EventScript_SouthRoadClosed'):
            role = {'': ('Clerk', 'OBJ_EVENT_GFX_SAILOR'), '_2': ('Fisherman', 'OBJ_EVENT_GFX_FISHERMAN'),
                    '_3': ('Kid', 'OBJ_EVENT_GFX_BOY_1')}[s[len('LavenderTown_EventScript_SouthRoadClosed'):]]
            o['script'], o['graphics_id'] = P + role[0], role[1]
        keep.append(o)
    keep += [npc('OBJ_EVENT_GFX_OLD_WOMAN', 17, 7, 'Caretaker'),
             npc('OBJ_EVENT_GFX_WOMAN_2', 12, 10, 'Neighbour'),
             npc('OBJ_EVENT_GFX_WOMAN_3', 8, 21, 'Mourner', movement='MOVEMENT_TYPE_FACE_UP')]
    town['object_events'] = keep
    signs = {'LavenderTown_EventScript_Sign1': 'TownSign', 'LavenderTown_EventScript_Sign2': 'TowerSign',
             'LavenderTown_EventScript_Sign3': 'HouseSign', 'LavenderTown_EventScript_Sign4': 'SoulSign'}
    for b in town['bg_events']:
        if b.get('script') in signs:
            b['script'] = P + signs[b['script']]
    save(TOWN, town)

    def returns(name, wid):
        d = load(name)
        for w in d['warp_events']:
            if w['dest_map'] in ('MAP_LAVENDER_TOWN', TOWN_ID):
                w.update(dest_map=TOWN_ID, dest_warp_id=wid)
        return d

    # --- FUJI's house (FRLG Volunteer Pokemon House) ---
    house = returns(HOUSE, '2')
    for o in house['object_events']:
        role = {'LavenderTown_VolunteerPokemonHouse_EventScript_MrFuji': 'HouseFuji',
                'LavenderTown_VolunteerPokemonHouse_EventScript_LittleGirl': 'HouseGirl',
                'LavenderTown_VolunteerPokemonHouse_EventScript_LittleBoy': 'HouseBoy',
                'LavenderTown_VolunteerPokemonHouse_EventScript_Youngster': 'HouseYoungster'}.get(o['script'])
        if role:
            o['script'] = P + role
        if role == 'HouseFuji':
            o['flag'] = 'FLAG_POX_HIDE_HOUSE_FUJI'
    save(HOUSE, house)
    p = f'data/maps/{HOUSE}/scripts.inc'
    put(p, re.sub(r'\A.*?\t\.byte 0', HOUSE + '_MapScripts::\n\tmap_script MAP_SCRIPT_ON_TRANSITION, '
                  + P + 'HouseOnTransition\n\t.byte 0', read(p), count=1, flags=re.S))
    save('LavenderTown_House1_Frlg', returns('LavenderTown_House1_Frlg', '5'))

    # --- the tower ---
    roles = {
        1: {'PokemonTower_1F_EventScript_WorkerF': 'T1Keeper', 'PokemonTower_1F_EventScript_Channeler': 'T1Channeler',
            'PokemonTower_1F_EventScript_Woman1': 'T1Woman1', 'PokemonTower_1F_EventScript_Woman2': 'T1Woman2',
            'PokemonTower_1F_EventScript_BaldingMan': 'T1Man'},
        2: {'PokemonTower_2F_EventScript_Channeler': 'T2Channeler'},
        3: {'PokemonTower_3F_EventScript_Patricia': 'T3Channeler1', 'PokemonTower_3F_EventScript_Carly': 'T3Channeler2',
            'PokemonTower_3F_EventScript_Hope': 'T3Channeler3'},
        4: {'PokemonTower_4F_EventScript_Laurel': 'T4Channeler1', 'PokemonTower_4F_EventScript_Jody': 'T4Channeler2',
            'PokemonTower_4F_EventScript_Paula': 'T4Channeler3'},
        5: {'PokemonTower_5F_EventScript_Ruth': 'T5Channeler1', 'PokemonTower_5F_EventScript_Tammy': 'T5Channeler2',
            'PokemonTower_5F_EventScript_Karina': 'T5Channeler3', 'PokemonTower_5F_EventScript_Janae': 'T5Channeler4',
            'PokemonTower_5F_EventScript_Channeler': 'T5Purifier'},
        6: {'PokemonTower_6F_EventScript_Angelica': 'T6Channeler1', 'PokemonTower_6F_EventScript_Emilia': 'T6Channeler2',
            'PokemonTower_6F_EventScript_Jennifer': 'T6Channeler3'},
    }
    for floor in range(1, 8):
        name = f'PokemonTower_{floor}F_Frlg'
        d = returns(name, '4') if floor == 1 else load(name)
        for o in d['object_events']:
            s = o['script']
            if s in roles.get(floor, {}):
                # Channelers talk in fragments; the tower is not a gauntlet.
                o.update(script=P + roles[floor][s], trainer_type='TRAINER_TYPE_NONE',
                         trainer_sight_or_berry_tree_id='0')
            o['flag'] = ITEM_FLAGS.get(o['flag'], o['flag'])
            if o.get('local_id') == 'LOCALID_POKEMON_TOWER_RIVAL':
                o['flag'] = 'FLAG_POX_HIDE_UNUSED_ACTOR'
            n = {'LOCALID_POKEMON_TOWER_GRUNT1': 1, 'LOCALID_POKEMON_TOWER_GRUNT2': 2,
                 'LOCALID_POKEMON_TOWER_GRUNT3': 3}.get(o.get('local_id'))
            if n:
                # Line-of-sight trainers. 7F is one corridor (x 9..13): GRUNT1
                # (9,10) and PROTON (9,6) face east and GRUNT2 (13,8) faces
                # west, so a sight of 4 covers every tile of rows 10, 8 and 6
                # and nobody reaches FUJI unseen, in that order.
                o.update(script=f'{P}TowerGrunt{n}Sight', flag=f'FLAG_POX_HIDE_LAVENDER_GRUNT_{n}',
                         trainer_type='TRAINER_TYPE_NORMAL', trainer_sight_or_berry_tree_id='4')
            if s in ('PokemonTower_1F_EventScript_Woman1', P + 'T1Woman1'):
                # She has visited her GROWLITHE for fifty years: an old woman.
                o['graphics_id'] = 'OBJ_EVENT_GFX_OLD_WOMAN_FRLG'
            if o['graphics_id'] == 'OBJ_EVENT_GFX_MR_FUJI':
                o.update(script=P + 'TowerFuji', flag='FLAG_POX_FUJI_RESCUED')
        # The FRLG rival (2F) and Silph Scope ghost (6F) scenes use FRLG vars
        # that alias live Emerald vars; Plastic Ox has neither scene.
        if floor in (2, 6):
            d['coord_events'] = []
        save(name, d)

    p = 'data/maps/PokemonTower_7F_Frlg/scripts.inc'
    put(p, re.sub(r'\A.*?\t\.byte 0', 'PokemonTower_7F_Frlg_MapScripts::\n\tmap_script MAP_SCRIPT_ON_TRANSITION, '
                  + P + 'Tower7FOnTransition\n\t.byte 0', read(p), count=1, flags=re.S))

    # --- old teleport tower room: empty placeholder (map number stays put) ---
    d = load('PlasticOx_PokemonTower')
    d.update(object_events=[], warp_events=[], coord_events=[], bg_events=[])
    save('PlasticOx_PokemonTower', d)

    # --- Soul House: the retired FUJI teleport room, entered from (22,19) ---
    d = load('PlasticOx_FujiHouse')
    d.update(music='MUS_RG_LAVENDER', region='REGION_KANTO', allow_running=False,
             include_in_versions=['emerald'],
             object_events=[npc('OBJ_EVENT_GFX_OLD_WOMAN', 4, 4, 'SoulKeeper'),
                            npc('OBJ_EVENT_GFX_LASS', 8, 6, 'SoulVisitor', movement='MOVEMENT_TYPE_FACE_UP')],
             warp_events=[dict(x=4, y=8, elevation=0, dest_map=TOWN_ID, dest_warp_id='6')],
             coord_events=[], bg_events=[])
    save('PlasticOx_FujiHouse', d)

    # --- TowerGrunt3: its own trainer id after the existing ones ---
    path = 'include/constants/opponents.h'
    s = read(path)
    if '#define TRAINER_PLASTIC_OX_TOWERGRUNT3 ' not in s:
        s = s.replace('// End Plastic Ox story trainers.',
                      '#define TRAINER_PLASTIC_OX_TOWERGRUNT3 960\n// End Plastic Ox story trainers.')
    for constant in ['TRAINERS_COUNT_EMERALD', 'MAX_TRAINERS_COUNT_EMERALD']:
        s = re.sub(r'(#define ' + constant + r'\s+)(\d+)', lambda m: m[1] + str(max(961, int(m[2]))), s)
    put(path, s)
    path = 'src/data/trainers.party'
    s = read(path)
    head = ('=== TRAINER_PLASTIC_OX_TOWERGRUNT3 ===\nName: PROTON\nClass: Rocket Executive Hns\nPic: Proton Hns\n'
            'Gender: Male\nMusic: Male\nDouble Battle: No\nAI: Basic Trainer / Smart Switching / PP Stall Prevention\n\n')
    m = re.search(r'^=== TRAINER_PLASTIC_OX_TOWERGRUNT3 ===\n.*?\n\n', s, flags=re.M | re.S)
    if m:  # party body belongs to plastic_ox/tools/apply_trainer_teams_v2.py
        s = s[:m.start()] + head + s[m.end():]
    else:
        s = s.rstrip('\n') + '\n\n' + head + 'Golbat\nLevel: 38\n- Bite\n'
    put(path, s)

    put('data/scripts/plastic_ox_lavender.inc', scripts())
    path = 'data/event_scripts.s'
    s = read(path)
    line = '\t.include "data/scripts/plastic_ox_lavender.inc"\n'
    if line not in s:
        s += '\n' + line
    put(path, s)
