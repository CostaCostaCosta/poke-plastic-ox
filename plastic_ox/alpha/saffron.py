"""Saffron City: the Fighting Dojo (Gym 7, BRUNO) and Silph Co. (Team Rocket III).

Installed last by region_v7.apply_region, so it owns the final shape of:

* SaffronCity_hns: nine residents, real doors and building signs. The wooden
  hall's doorway (45,12) is the FIGHTING DOJO, the tower door (33,30) is SILPH
  CO. and the red-roofed door (18,38) is the shared Kanto POKeMON CENTER. The
  three teleport guides are gone. Edge crossings, their two signs and the mart
  and gatehouse warps (0-2) stay with region_v7.py.
* SaffronCity_Dojo_Frlg: BRUNO's Gym in the FRLG Dojo interior. A desk clerk
  checks the ADV OU clauses (CheckSaffronGymOURules), two BLACK BELTS battle
  whoever walks into their half of the mat, and after the badge BRUNO offers
  one of two prize fighters (HITMONLEE / HITMONCHAN).
* SilphCo_1F_Frlg and SilphCo_11F_Frlg: the lobby, the lift, and the executive
  floor. Three Rocket grunts stand in the way in order (lift, east corridor,
  west corridor), GIOVANNI waits in the boardroom, and the PRESIDENT's terminal
  is the adaptive Trainer system (Pox_SilphCore sets FLAG_POX_STORY_SILPH).
  The lift only stops at 11F; a warp pad joins the floor's two halves.
* PlasticOx_BrunoGym and PlasticOx_Silph, the old teleport rooms: empty
  placeholders that keep their map numbers, with a door back to the street for
  a save made inside one.

The story battles themselves (Pox_Bruno, Pox_SilphGrunt1-3, Pox_Giovanni) stay
in build_story.py so their trainer ids keep their numbering.

Story source: plastic_ox/story/locations/saffroncity-hns.md.
"""
import json
import re
import textwrap

CITY = 'SaffronCity_hns'
CITY_ID = 'MAP_SAFFRON_CITY_HNS'
DOJO = 'SaffronCity_Dojo_Frlg'
LOBBY = 'SilphCo_1F_Frlg'
BOARD = 'SilphCo_11F_Frlg'
P = 'PoxSaffron_'

# City warp ids. 0-2 (mart, east and west gatehouses) belong to region_v7.py.
WARP_DOJO, WARP_SILPH, WARP_CENTER = '3', '4', '5'
# FRLG Silph warp-pad metatile (MB_AQUA_HIDEOUT_WARP), as at 11F (2,5).
PAD_METATILE = '0x390'
PRIZE_LEVEL = 45

# New persistent flags (POX_EXT pool; see the plastic-ox-flags skill).
EXT_FLAGS = [
    ('FLAG_POX_DOJO_PRIZE', 12, 'Fighting Dojo: took HITMONLEE or HITMONCHAN (hides both prize balls).'),
    ('FLAG_POX_SILPH_MASTER_BALL', 13, "Silph Co. 11F: the PRESIDENT's MASTER BALL was handed over."),
    ('FLAG_POX_HIDE_SILPH_STAFF', 14, 'Silph Co. 11F: hides the PRESIDENT and SECRETARY until Silph is resolved (set on transition).'),
]

# Dojo trainers get their own ids after the existing ones. Party bodies belong
# to plastic_ox/tools/apply_trainer_teams_v2.py.
DOJO_TRAINERS = [
    ('TRAINER_PLASTIC_OX_DOJO_KENJI', 962, 'KENJI', 'Hitmonlee\nLevel: 52\n- Brick Break\n'),
    ('TRAINER_PLASTIC_OX_DOJO_NOB', 963, 'NOB', 'Hitmonchan\nLevel: 52\n- Brick Break\n'),
]

# Two registers. The street is loud and knows nothing; the Dojo is etiquette;
# Silph is fear and hardware. Nobody says "convergence", nobody names BILL,
# and no civilian can say what is inside SILPH.
# label -> text, or label -> (before FLAG_POX_STORY_SILPH, after).
LINES = {
    # --- street ---
    'Queue': "My brother's been in the DOJO since the morning bell. They take your bag at the desk and you don't get it back until you've bowed properly.|He says the MASTER watches your POKéMON more than he watches you. I think that's why he keeps going back.",
    'Clerk': ("I work on the fourth floor. Worked. My pass has been red at the door since Tuesday.|Security says it's maintenance. Maintenance doesn't usually bring that many men in black coats.",
              "My pass went green this morning. Nobody upstairs will say what the week was about.|My lunch was still in the fridge on four. I've decided not to think about that either."),
    'Grocer': "You picked a decent week. A month back the gates were shut and the trucks sat outside. We sold rice and batteries and that was the shop.|Now it's all four roads at once and I can't stack the shelves fast enough.",
    'Courier': "Four gates, four checkpoints, and every one of them wants to weigh the parcel.|I used to do the east side before lunch. Now the east side comes out on a different coast, so I bill by the hour.",
    'Schoolkid': "I look through the DOJO door after school. Nobody shouts. Somebody says 'again' and everyone does it again.|It's scarier than shouting.",
    'TrainKid': "The station says the trains aren't stopping, but they still go past. I counted six while I waited for my sister.|She says the drivers are waiting for somebody to tell them where the next station is.",
    'Overtime': "I haven't been home since the roads opened. Everyone who was stuck outside for a month wants their paperwork stamped today.|The POKéMON CENTER lets me nap in the chairs. Don't tell them I said so.",
    'OldHall': "That hall with the GYM plate has been dark as long as I've lived here. Good step for tying your shoes.|The real challengers go next door. You can tell which ones by how quiet they are coming out.",
    # --- street signs and dead doors ---
    'DojoSign': "SAFFRON FIGHTING DOJO\nPOKéMON LEAGUE GYM  MASTER: BRUNO\\pShoes off. Voices down.",
    'OldHallSign': "SAFFRON TRAINING HALL\nClosed until further notice.\\pLEAGUE challenges are held at\nthe DOJO next door.",
    'SilphSign': "SILPH CO. HEAD OFFICE\nVisitors report to reception.",
    'StationSign': "SAFFRON STATION\nService suspended.\\pTrains will not stop until the\nline has been surveyed again.",
    'OldHallDoor': "The doors are locked. Through\nthe glass, the floor is covered\\pin dust sheets.",
    'StationDoor': "The station doors are chained.\nA timetable is taped inside\\pwith every row crossed out.",
    'WestHouseDoor': "Nobody answers. A note says:\nBACK WHEN THE OFFICE REOPENS.",
    'SouthHouseDoor': "The door is locked. Someone\ninside is practising scales.",
    # --- Dojo ---
    'DeskHello': "Sign here, bag on the shelf, and mind the floor. The MASTER has been on it since the morning bell.|This hall is a LEAGUE GYM under OU rules. No one-hit knockout moves and no evasion items. I check every team at the desk.",
    'DeskClear': "Your team is in order. Walk up the middle of the mat.|The BLACK BELTS will only stop you if you step into their half. Some people do it on purpose.",
    'DeskMove': "One moment. Your {STR_VAR_1} knows {STR_VAR_2}. That move isn't allowed on this floor.|The MASTER won't begin until it's gone. I don't write the rules. I hold the clipboard.",
    'DeskItem': "One moment. Your {STR_VAR_1} is holding {STR_VAR_2}. That item isn't allowed on this floor.|Leave it in your BAG and the MASTER will see you.",
    'DeskAfter': "You're in the book now. Seventh line, in the MASTER's own handwriting. He doesn't usually write them himself.",
    'StudentLeft': "...Forty-one. Forty-two. Hands lower. Forty-three.|Sorry. If I stop counting I have to start again.",
    'StudentRight': "The MASTER gave up a room at the top of the LEAGUE to come back and sweep this one.|I asked him why. He said, 'Again,' so I did the form again. I think that was the answer.",
    'KenjiIntro': "You stepped onto my half of the mat. That is a request. I accept.",
    'KenjiDefeat': "Clean. I have nothing to correct.",
    'KenjiAfter': "Bow before you speak to the MASTER. He will answer with a POKé BALL.",
    'NobIntro': "I have held this corner for nine years. Show me why you walked into it.",
    'NobDefeat': "Nine years, and still a lesson.",
    'NobAfter': "HITMONCHAN and I will be here tomorrow. We are always here tomorrow.",
    'BrunoNotReady': "BRUNO: Not yet. The LEAGUE sends me challengers who hold six BADGES. Train, and come back.",
    'BrunoRules': "BRUNO: Your {STR_VAR_1}, and its {STR_VAR_2}. Not on this floor.|The desk will explain. I will be here when it is settled.",
    'BrunoAfter': "BRUNO: That is the seventh BADGE by the LEAGUE's count. Count however you like. The roads out of this city do not ask what order you walked them in.|Behind me are two POKé BALLS. Each year this hall raises two fighters for someone who has earned the floor. Take one. Only one.",
    'BrunoDone': "BRUNO: You are welcome on this floor whenever you wish. Shoes off.",
    'BrunoPrizeWaiting': "BRUNO: The two fighters are still waiting behind me. Choose one.",
    'PrizeLeeNotYet': "A POKé BALL on a folded cloth. It is not yours to touch yet.",
    'PrizeChanNotYet': "A second POKé BALL, set a careful hand's width from the first. BRUNO has not offered it.",
    'PrizeLee': "BRUNO: HITMONLEE. All leg and no patience. Will you take it?",
    'PrizeChan': "BRUNO: HITMONCHAN. It has never once dropped its guard. Will you take it?",
    'PrizeLeeTaken': "BRUNO: One. That was the arrangement.",
    'PrizeChanTaken': "BRUNO: The other one stays with the hall.",
    'PrizeLeeNoRoom': "BRUNO: No room in your party or your PC. Make some, then come back.",
    'PrizeChanNoRoom': "BRUNO: It will wait. Clear a space for it first.",
    'PrizeLeeGot': "{PLAYER} took HITMONLEE from its stand! If your party was full, it went to your PC.",
    'PrizeChanGot': "{PLAYER} took HITMONCHAN from its stand! If your party was full, it went to your PC.",
    'StatueLeft': "SAFFRON FIGHTING DOJO\nLEAGUE GYM No. 7  MASTER: BRUNO",
    'StatueRight': "Carved along the base:\nWHAT FALLS, GETS UP.",
    'ScrollLeft': "A hanging scroll.\nTHE FLOOR TEACHES FIRST.",
    'ScrollRight': "A hanging scroll.\nAGAIN.",
    # --- Silph 1F ---
    'LobbyDesk': ("Welcome to SILPH C-- no. Sorry. Habit.|They came in on Tuesday with toolboxes and sent everyone upstairs. I got under the desk and nobody counted.|There's a first-aid cabinet back here. Let me see your POKéMON.",
                  "The PRESIDENT says reception reopens on Monday. I have been at this desk for nine days. I don't know what he thinks I was doing.|Sit down a moment. The cabinet's still stocked."),
    'LobbyDeskHealed': ("That's all I can do. The lift still answers, but it only goes to the top floor now, and one of them is standing in front of it.",
                        "There. If anyone asks, the first-aid cabinet was always this empty."),
    'LobbyStairs': "The stairwell door is chained from the other side.",
    'LobbySign': "SILPH CO. HEAD OFFICE\n1F  RECEPTION",
    'GruntNotYet1': "Lift's not for visitors. Come back when somebody upstairs has heard of you.",
    'GruntNotYet2': "Not my floor, not my problem. Take it up with whoever let you past.",
    'GruntNotYet3': "I'm reading. If the others had stopped you, nobody would have to tell you that.",
    # --- Silph 11F ---
    'BoardStairs': "The stairs down are chained shut. Somebody has wedged a chair under the handle as well.",
    'BoardSign': "SILPH CO. HEAD OFFICE\n11F  BOARDROOM",
    'GiovanniNotReady': "GIOVANNI: You have left some of my people standing. I do not speak to anyone who leaves work unfinished.",
    'GiovanniLeaves': "GIOVANNI: Keep it, then. I wanted to own it. In all this time I never once made it answer me.|It answers to battles. Remember that when you sit down at that terminal.|TEAM ROCKET is leaving SAFFRON. We were never the ones you should have been worried about.",
    'CoreLocked': "The PRESIDENT's terminal. GIOVANNI is watching you, not the screen.",
    'Core1': "The PRESIDENT's terminal is still logged in. Under SILPH's own menus there is a layer that nobody in this building installed.|ADAPTIVE TRAINER SYSTEM. STATUS: ACTIVE.|OBJECTIVE: IMPROVE TRAINING CONDITIONS.|BATTLE PROFILES LOGGED: BLUE. LANCE. STEVEN. WALLACE. 61,204 OTHERS.|FINDING: HABITAT ISOLATION REDUCES TRAINING QUALITY. REGIONAL TRANSFER LINKS: RECONCILED.|ENVIRONMENTAL RESTRUCTURING: ONGOING. NEXT PASS: SCHEDULED.",
    'CoreAsk': "ISOLATE ENVIRONMENTAL CONTROLS FROM THE TRANSFER NETWORK?",
    'CoreNo': "The cursor waits. NEXT PASS: SCHEDULED.",
    'Core2': "ENVIRONMENTAL CONTROLS: ISOLATED. RESTRUCTURING: HALTED.|EXISTING GEOGRAPHY: RETAINED. BATTLE ANALYSIS: CONTINUING.|The transfer links fall silent. Nothing outside the window moves back. Nothing moves at all.",
    'CoreStaff': "Footsteps in the corridor. Somewhere below, the lift starts to run again.",
    'CoreDone': "ENVIRONMENTAL CONTROLS: ISOLATED.\nBATTLE ANALYSIS: CONTINUING.",
    'President': "PRESIDENT: They kept us in the supply room on nine with a kettle and no cups. I am told you are the reason the door opened.|I will not ask what was on my terminal. I have a feeling I should have asked years ago.|SILPH made exactly one of these. It was meant for a display case. Take it.",
    'PresidentNoRoom': "PRESIDENT: Your BAG is full. It has waited in a drawer this long. It can wait until you have made room.",
    'PresidentAfter': "PRESIDENT: The board wants a report. I intend to write 'maintenance' and see how far that gets me.",
    'Secretary': "Nine days of minutes to type up, and for eight of them the only item is STILL LOCKED IN.|The lift stops at every floor again. I rode it down and back up just to check.",
}

# label -> kind. 'npc' is a plain talk script; 'silph' switches on
# FLAG_POX_STORY_SILPH; 'sign' is a MSGBOX_SIGN; everything else is text only.
SIMPLE = {
    'npc': ['Queue', 'Grocer', 'Courier', 'Schoolkid', 'TrainKid', 'Overtime', 'OldHall',
            'StudentLeft', 'StudentRight', 'Secretary'],
    'silph': ['Clerk'],
    'sign': ['DojoSign', 'OldHallSign', 'SilphSign', 'StationSign', 'OldHallDoor', 'StationDoor',
             'WestHouseDoor', 'SouthHouseDoor', 'StatueLeft', 'StatueRight', 'ScrollLeft', 'ScrollRight',
             'LobbySign', 'BoardSign'],
}


def text(label, body):
    if '\n' in body:  # signs and terminal read-outs carry their own layout
        return f'{P}Text_{label}::\n\t.string "' + body.replace('\n', '\\n') + '$"\n'
    pages = []
    for paragraph in body.split('|'):
        lines = textwrap.wrap(paragraph, 32)
        pages.extend('\\n'.join(lines[i:i + 2]) for i in range(0, len(lines), 2))
    return f'{P}Text_{label}::\n\t.string "' + '\\p'.join(pages) + '$"\n'


def sight(n, prerequisite):
    """A grunt spots the player only while his story battle is due (the
    lavender.py pattern): the trainer flag is the engine's "don't look"
    switch, recomputed on entry from the real record, the hide flag."""
    t = f'TRAINER_PLASTIC_OX_SILPHGRUNT{n}'
    return (f'{P}ArmGrunt{n}::\n\tsettrainerflag {t}\n'
            f'\tgoto_if_unset FLAG_POX_TRIGGERS_ENABLED, {P}Return\n'
            f'\tgoto_if_unset {prerequisite}, {P}Return\n'
            f'\tgoto_if_set FLAG_POX_HIDE_SILPH_GRUNT_{n}, {P}Return\n'
            f'\tcleartrainerflag {t}\n\treturn\n')


def scripts():
    out = ['@ Generated by plastic_ox/alpha/saffron.py\n']
    texts = []
    for label, body in LINES.items():
        if isinstance(body, tuple):
            texts.append(text(label, body[0]))
            texts.append(text(label + '_After', body[1]))
        else:
            texts.append(text(label, body))
    for label in SIMPLE['npc']:
        out.append(f'{P}{label}::\n\tmsgbox {P}Text_{label}, MSGBOX_NPC\n\tend\n')
    for label in SIMPLE['silph']:
        out.append(f'{P}{label}::\n\tlock\n\tfaceplayer\n\tgoto_if_set FLAG_POX_STORY_SILPH, {P}{label}_After\n'
                   f'\tmsgbox {P}Text_{label}, MSGBOX_DEFAULT\n\trelease\n\tend\n'
                   f'{P}{label}_After::\n\tmsgbox {P}Text_{label}_After, MSGBOX_DEFAULT\n\trelease\n\tend\n')
    for label in SIMPLE['sign']:
        out.append(f'{P}{label}::\n\tmsgbox {P}Text_{label}, MSGBOX_SIGN\n\tend\n')
    out.append(f'''{P}Return::
	return

@ ---------------------------------------------------------------- Dojo
@ The desk reports the first ADV OU clause the party breaks. BRUNO runs the
@ same check before his battle, so the desk is advice, not a gate.
{P}DojoDesk::
	lock
	faceplayer
	goto_if_set FLAG_BADGE07_GET, {P}DojoDeskAfter
	msgbox {P}Text_DeskHello, MSGBOX_DEFAULT
	specialvar VAR_RESULT, CheckSaffronGymOURules
	goto_if_eq VAR_RESULT, 1, {P}DojoDeskMove
	goto_if_eq VAR_RESULT, 2, {P}DojoDeskItem
	msgbox {P}Text_DeskClear, MSGBOX_DEFAULT
	release
	end
{P}DojoDeskMove::
	msgbox {P}Text_DeskMove, MSGBOX_DEFAULT
	release
	end
{P}DojoDeskItem::
	msgbox {P}Text_DeskItem, MSGBOX_DEFAULT
	release
	end
{P}DojoDeskAfter::
	msgbox {P}Text_DeskAfter, MSGBOX_DEFAULT
	release
	end

{P}Kenji::
	trainerbattle_single TRAINER_PLASTIC_OX_DOJO_KENJI, {P}Text_KenjiIntro, {P}Text_KenjiDefeat
	msgbox {P}Text_KenjiAfter, MSGBOX_AUTOCLOSE
	end
{P}Nob::
	trainerbattle_single TRAINER_PLASTIC_OX_DOJO_NOB, {P}Text_NobIntro, {P}Text_NobDefeat
	msgbox {P}Text_NobAfter, MSGBOX_AUTOCLOSE
	end

@ BRUNO's story battle (plastic_ox_story.inc) jumps to these.
{P}BrunoNotReady::
	msgbox {P}Text_BrunoNotReady, MSGBOX_DEFAULT
	releaseall
	end
{P}BrunoRules::
	msgbox {P}Text_BrunoRules, MSGBOX_DEFAULT
	releaseall
	end
{P}BrunoAfter::
	msgbox {P}Text_BrunoAfter, MSGBOX_DEFAULT
	releaseall
	end
{P}BrunoDone::
	msgbox {P}Text_BrunoDone, MSGBOX_DEFAULT
	goto_if_set FLAG_POX_DOJO_PRIZE, Pox_Release
	msgbox {P}Text_BrunoPrizeWaiting, MSGBOX_DEFAULT
	releaseall
	end

@ One prize fighter, after the badge. Taking either hides both balls.
{P}PrizeLee::
	lock
	goto_if_set FLAG_POX_DOJO_PRIZE, {P}PrizeLeeTaken
	goto_if_unset FLAG_BADGE07_GET, {P}PrizeLeeNotYet
	showmonpic SPECIES_HITMONLEE, 10, 3
	msgbox {P}Text_PrizeLee, MSGBOX_YESNO
	hidemonpic
	goto_if_eq VAR_RESULT, NO, {P}PrizeEnd
	givemon SPECIES_HITMONLEE, {PRIZE_LEVEL}
	goto_if_eq VAR_RESULT, MON_CANT_GIVE, {P}PrizeLeeNoRoom
	setflag FLAG_POX_DOJO_PRIZE
	removeobject VAR_LAST_TALKED
	playfanfare MUS_OBTAIN_ITEM
	msgbox {P}Text_PrizeLeeGot, MSGBOX_DEFAULT
	waitfanfare
	release
	end
{P}PrizeChan::
	lock
	goto_if_set FLAG_POX_DOJO_PRIZE, {P}PrizeChanTaken
	goto_if_unset FLAG_BADGE07_GET, {P}PrizeChanNotYet
	showmonpic SPECIES_HITMONCHAN, 10, 3
	msgbox {P}Text_PrizeChan, MSGBOX_YESNO
	hidemonpic
	goto_if_eq VAR_RESULT, NO, {P}PrizeEnd
	givemon SPECIES_HITMONCHAN, {PRIZE_LEVEL}
	goto_if_eq VAR_RESULT, MON_CANT_GIVE, {P}PrizeChanNoRoom
	setflag FLAG_POX_DOJO_PRIZE
	removeobject VAR_LAST_TALKED
	playfanfare MUS_OBTAIN_ITEM
	msgbox {P}Text_PrizeChanGot, MSGBOX_DEFAULT
	waitfanfare
	release
	end
{P}PrizeEnd::
	release
	end
''' + ''.join(f'''{P}Prize{who}{state}::
	msgbox {P}Text_Prize{who}{state}, MSGBOX_DEFAULT
	release
	end
''' for who in ('Lee', 'Chan') for state in ('Taken', 'NotYet', 'NoRoom')) + f'''

@ ---------------------------------------------------------------- Silph
@ Rockets battle on sight. The object script opens with trainerbattle so the
@ engine can spot the player; talking to a dormant one falls through to the
@ story script in plastic_ox_story.inc.
{P}SilphGrunt1Sight::
	trainerbattle_single TRAINER_PLASTIC_OX_SILPHGRUNT1, Pox_Text_SilphGrunt1, Pox_Text_SilphGrunt1_Defeat, Pox_SilphGrunt1_Won
	goto Pox_SilphGrunt1
{P}SilphGrunt2Sight::
	trainerbattle_single TRAINER_PLASTIC_OX_SILPHGRUNT2, Pox_Text_SilphGrunt2, Pox_Text_SilphGrunt2_Defeat, Pox_SilphGrunt2_Won
	goto Pox_SilphGrunt2
{P}SilphGrunt3Sight::
	trainerbattle_single TRAINER_PLASTIC_OX_SILPHGRUNT3, Pox_Text_SilphGrunt3, Pox_Text_SilphGrunt3_Defeat, Pox_SilphGrunt3_Won
	goto Pox_SilphGrunt3
{P}GruntNotYet1::
	msgbox {P}Text_GruntNotYet1, MSGBOX_DEFAULT
	releaseall
	end
{P}GruntNotYet2::
	msgbox {P}Text_GruntNotYet2, MSGBOX_DEFAULT
	releaseall
	end
{P}GruntNotYet3::
	msgbox {P}Text_GruntNotYet3, MSGBOX_DEFAULT
	releaseall
	end

{sight(1, 'FLAG_POX_STORY_SPACE_CENTER')}{sight(2, 'FLAG_POX_HIDE_SILPH_GRUNT_1')}{sight(3, 'FLAG_POX_HIDE_SILPH_GRUNT_2')}
{P}LobbyOnTransition::
	call {P}ArmGrunt1
	end

@ The receptionist heals before and after: four OU battles in a row need it.
{P}LobbyDesk::
	lock
	faceplayer
	goto_if_set FLAG_POX_STORY_SILPH, {P}LobbyDesk_After
	msgbox {P}Text_LobbyDesk, MSGBOX_DEFAULT
	closemessage
	call Common_EventScript_OutOfCenterPartyHeal
	msgbox {P}Text_LobbyDeskHealed, MSGBOX_DEFAULT
	release
	end
{P}LobbyDesk_After::
	msgbox {P}Text_LobbyDesk_After, MSGBOX_DEFAULT
	closemessage
	call Common_EventScript_OutOfCenterPartyHeal
	msgbox {P}Text_LobbyDeskHealed_After, MSGBOX_DEFAULT
	release
	end

@ The stairs are closed on both floors: the lift is the only way up.
{P}LobbyStairs::
	lockall
	msgbox {P}Text_LobbyStairs, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_PLAYER, {P}Move_StepDown
	waitmovement 0
	releaseall
	end
{P}BoardStairs::
	lockall
	msgbox {P}Text_BoardStairs, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_PLAYER, {P}Move_StepDown
	waitmovement 0
	releaseall
	end
{P}Move_StepDown:
	walk_down
	step_end

@ 11F is two halves that only a warp pad joins: the lift side (east) and the
@ boardroom side (west). The east pad is laid on load; the west one is native.
{P}BoardOnLoad::
	setmetatile 16, 19, {PAD_METATILE}, FALSE
	end
{P}BoardOnTransition::
	call {P}ArmGrunt2
	call {P}ArmGrunt3
	call_if_unset FLAG_POX_STORY_SILPH, {P}HideStaff
	call_if_set FLAG_POX_STORY_SILPH, {P}ShowStaff
	end
{P}HideStaff::
	setflag FLAG_POX_HIDE_SILPH_STAFF
	return
{P}ShowStaff::
	clearflag FLAG_POX_HIDE_SILPH_STAFF
	return

@ Stepping into the boardroom walks the player up to GIOVANNI and starts his
@ battle. A coord trigger has no selected object event, which the ordinary
@ trainerbattle intro asserts on, so this path shows the intro itself and
@ uses trainerbattle_no_intro; the victory script is the same either way.
{P}GiovanniTriggerLeft::
	lockall
	goto_if_set FLAG_POX_HIDE_SILPH_GIOVANNI, {P}GiovanniTriggerOff
	goto_if_unset FLAG_POX_TRIGGERS_ENABLED, {P}GiovanniTriggerOff
	applymovement LOCALID_PLAYER, {P}Move_GiovanniLeft
	waitmovement 0
	goto {P}GiovanniApproach
{P}GiovanniTriggerRight::
	lockall
	goto_if_set FLAG_POX_HIDE_SILPH_GIOVANNI, {P}GiovanniTriggerOff
	goto_if_unset FLAG_POX_TRIGGERS_ENABLED, {P}GiovanniTriggerOff
	applymovement LOCALID_PLAYER, {P}Move_GiovanniRight
	waitmovement 0
{P}GiovanniApproach::
	setvar VAR_TEMP_1, 1
	goto_if_unset FLAG_POX_HIDE_SILPH_GRUNT_3, {P}GiovanniNotReady
	playbgm MUS_RG_ENCOUNTER_ROCKET, FALSE
	msgbox Pox_Text_Giovanni, MSGBOX_DEFAULT
	closemessage
	trainerbattle_no_intro TRAINER_PLASTIC_OX_GIOVANNI, Pox_Text_Giovanni_Defeat
	goto Pox_Giovanni_Won
{P}GiovanniTriggerOff::
	setvar VAR_TEMP_1, 1
	releaseall
	end
{P}Move_GiovanniLeft:
	walk_right
{P}Move_GiovanniRight:
	walk_up
	walk_up
	step_end
{P}GiovanniNotReady::
	msgbox {P}Text_GiovanniNotReady, MSGBOX_DEFAULT
	releaseall
	end
@ The victory script jumps here once FLAG_POX_HIDE_SILPH_GIOVANNI is set.
{P}GiovanniLeaves::
	msgbox {P}Text_GiovanniLeaves, MSGBOX_DEFAULT
	closemessage
	fadescreen FADE_TO_BLACK
	removeobject LOCALID_POX_SILPH_GIOVANNI
	fadescreen FADE_FROM_BLACK
	releaseall
	end

@ Reveal-ladder step 14, and the only place the system is named. The terminal
@ reports status; it never addresses the player. The merged region stays.
Pox_SilphCore::
	goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End
	lockall
	goto_if_unset FLAG_POX_HIDE_SILPH_GIOVANNI, {P}CoreLocked
	goto_if_set FLAG_POX_STORY_SILPH, {P}CoreDone
	msgbox {P}Text_Core1, MSGBOX_DEFAULT
	msgbox {P}Text_CoreAsk, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, {P}CoreNo
	playse SE_PC_OFF
	msgbox {P}Text_Core2, MSGBOX_DEFAULT
	setflag FLAG_POX_STORY_SILPH
	closemessage
	fadescreen FADE_TO_BLACK
	clearflag FLAG_POX_HIDE_SILPH_STAFF
	addobject LOCALID_POX_SILPH_PRESIDENT
	addobject LOCALID_POX_SILPH_SECRETARY
	fadescreen FADE_FROM_BLACK
	msgbox {P}Text_CoreStaff, MSGBOX_DEFAULT
	releaseall
	end
{P}CoreLocked::
	msgbox {P}Text_CoreLocked, MSGBOX_DEFAULT
	releaseall
	end
{P}CoreNo::
	msgbox {P}Text_CoreNo, MSGBOX_DEFAULT
	releaseall
	end
{P}CoreDone::
	msgbox {P}Text_CoreDone, MSGBOX_DEFAULT
	releaseall
	end

{P}President::
	lock
	faceplayer
	goto_if_set FLAG_POX_SILPH_MASTER_BALL, {P}PresidentAfter
	msgbox {P}Text_President, MSGBOX_DEFAULT
	giveitem ITEM_MASTER_BALL
	goto_if_eq VAR_RESULT, FALSE, {P}PresidentNoRoom
	setflag FLAG_POX_SILPH_MASTER_BALL
	release
	end
{P}PresidentNoRoom::
	msgbox {P}Text_PresidentNoRoom, MSGBOX_DEFAULT
	release
	end
{P}PresidentAfter::
	msgbox {P}Text_PresidentAfter, MSGBOX_DEFAULT
	release
	end
''')
    return '\n'.join(out) + '\n' + '\n'.join(texts)


def npc(gfx, x, y, script, flag='0', movement='MOVEMENT_TYPE_FACE_DOWN', elevation=3, sight=None, local_id=None):
    obj = dict(graphics_id=gfx, x=x, y=y, elevation=elevation, movement_type=movement,
               movement_range_x=0, movement_range_y=0,
               trainer_type='TRAINER_TYPE_NORMAL' if sight else 'TRAINER_TYPE_NONE',
               trainer_sight_or_berry_tree_id=str(sight or 0), script=script, flag=flag)
    return {'local_id': local_id, **obj} if local_id else obj


def sign(x, y, label):
    return dict(type='sign', x=x, y=y, elevation=0, player_facing_dir='BG_EVENT_PLAYER_FACING_ANY',
                script=P + label)


def trigger(x, y, script):
    return dict(type='trigger', x=x, y=y, elevation=3, var='VAR_TEMP_1', var_value='0', script=P + script)


def door(x, y, dest, warp, elevation=3):
    return dict(x=x, y=y, elevation=elevation, dest_map=dest, dest_warp_id=warp)


def install(read, put):
    def load(name):
        return json.loads(read(f'data/maps/{name}/map.json'))

    def save(name, data):
        put(f'data/maps/{name}/map.json', json.dumps(data, indent=2) + '\n')

    def map_scripts(name, *entries):
        body = ''.join(f'\tmap_script {kind}, {P}{label}\n' for kind, label in entries)
        put(f'data/maps/{name}/scripts.inc', f'{name}_MapScripts::\n{body}\t.byte 0\n')

    # --- flags ---
    path = 'include/constants/plastic_ox_flags.h'
    header = read(path)
    block = ''.join(f'// {comment}\n#define {name} (POX_EXT_FLAGS_START + {n})\n' for name, n, comment in EXT_FLAGS)
    begin, end = '// Saffron: Fighting Dojo and Silph Co. (plastic_ox/alpha/saffron.py).\n', '// End Saffron flags.\n'
    header = re.sub(re.escape(begin) + '.*?' + re.escape(end) + '\n?', '', header, flags=re.S)
    header = header.replace('#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H',
                            begin + block + end + '\n#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H')
    put(path, header)

    # --- the city: residents, real doors, building signs ---
    city = load(CITY)
    region_owned = lambda e: e.get('script', '').startswith('PoxRegion_')
    street = lambda gfx, x, y, script, movement='MOVEMENT_TYPE_FACE_DOWN': npc(gfx, x, y, script, movement=movement, elevation=0)
    city['object_events'] = [
        street('OBJ_EVENT_GFX_LASS_HNS', 43, 13, P + 'Queue', 'MOVEMENT_TYPE_FACE_RIGHT'),
        street('OBJ_EVENT_GFX_WOMAN_2', 35, 31, P + 'Clerk'),
        # Index 2 is the north-road walker build_story.py scripts (Pox_BlackthornRoad).
        street('OBJ_EVENT_GFX_HIKER', 27, 12, 'Pox_BlackthornRoad', 'MOVEMENT_TYPE_FACE_RIGHT'),
        street('OBJ_EVENT_GFX_FAT_MAN_HNS', 49, 23, P + 'Grocer', 'MOVEMENT_TYPE_LOOK_AROUND'),
        street('OBJ_EVENT_GFX_CYCLING_TRIATHLETE_F', 43, 34, P + 'Courier'),
        street('OBJ_EVENT_GFX_YOUNGSTER_HNS', 53, 32, P + 'Schoolkid', 'MOVEMENT_TYPE_LOOK_AROUND'),
        street('OBJ_EVENT_GFX_BOY_2_HNS', 11, 15, P + 'TrainKid'),
        street('OBJ_EVENT_GFX_WOMAN_1', 20, 39, P + 'Overtime'),
        street('OBJ_EVENT_GFX_BUG_CATCHER_HNS', 50, 13, P + 'OldHall'),
    ] + [o for o in city['object_events'] if region_owned(o)]
    city['warp_events'] = city['warp_events'][:3] + [
        door(45, 12, 'MAP_SAFFRON_CITY_DOJO', '1'),       # warp 3: the Dojo's open doorway
        door(33, 30, 'MAP_SILPH_CO_1F', '1'),              # warp 4
        door(18, 38, 'MAP_POKEMON_CENTER_KANTO_HNS', '0'),  # warp 5: shared interior, dynamic exit
    ]
    city['bg_events'] = [b for b in city['bg_events'] if region_owned(b)] + [
        sign(47, 14, 'DojoSign'), sign(54, 14, 'OldHallSign'), sign(30, 31, 'SilphSign'),
        sign(20, 15, 'StationSign'), sign(52, 12, 'OldHallDoor'), sign(17, 14, 'StationDoor'),
        sign(21, 21, 'WestHouseDoor'), sign(47, 38, 'SouthHouseDoor')]
    city['music'] = 'MUS_RG_PEWTER'  # FRLG's Saffron theme; MUS_RG_SILPH belongs inside the tower
    save(CITY, city)
    put(f'data/maps/{CITY}/scripts.inc', f'{CITY}_MapScripts::\n'
        f'\tmap_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_{CITY}\n\t.byte 0\n')

    # --- the Dojo ---
    d = load(DOJO)
    d.update(music='MUS_RG_GYM', battle_scene='MAP_BATTLE_SCENE_GYM', show_map_name=False,
             object_events=[
                 npc('OBJ_EVENT_GFX_BRUNO', 6, 5, 'Pox_Bruno'),
                 npc('OBJ_EVENT_GFX_WORKER_F', 8, 13, P + 'DojoDesk', movement='MOVEMENT_TYPE_FACE_LEFT'),
                 npc('OBJ_EVENT_GFX_BLACK_BELT_FRLG', 1, 10, P + 'Kenji', movement='MOVEMENT_TYPE_FACE_RIGHT', sight=3),
                 npc('OBJ_EVENT_GFX_BLACK_BELT_FRLG', 11, 10, P + 'Nob', movement='MOVEMENT_TYPE_FACE_LEFT', sight=3),
                 npc('OBJ_EVENT_GFX_BLACK_BELT_FRLG', 1, 8, P + 'StudentLeft', movement='MOVEMENT_TYPE_FACE_RIGHT'),
                 npc('OBJ_EVENT_GFX_BLACK_BELT_FRLG', 11, 8, P + 'StudentRight', movement='MOVEMENT_TYPE_FACE_LEFT'),
                 npc('OBJ_EVENT_GFX_ITEM_BALL', 5, 3, P + 'PrizeLee', flag='FLAG_POX_DOJO_PRIZE'),
                 npc('OBJ_EVENT_GFX_ITEM_BALL', 7, 3, P + 'PrizeChan', flag='FLAG_POX_DOJO_PRIZE'),
             ],
             warp_events=[door(x, 14, CITY_ID, WARP_DOJO) for x in (5, 6, 7)],
             coord_events=[],
             bg_events=[sign(3, 13, 'StatueLeft'), sign(9, 13, 'StatueRight'),
                        sign(5, 2, 'ScrollLeft'), sign(7, 2, 'ScrollRight')])
    save(DOJO, d)
    map_scripts(DOJO)

    # --- Silph 1F: reception, the first grunt at the lift, closed stairs ---
    d = load(LOBBY)
    d.update(object_events=[
                 npc('OBJ_EVENT_GFX_WORKER_F', 3, 7, P + 'LobbyDesk'),
                 # The lift door is only reachable from (22,4): he is the gate.
                 npc('OBJ_EVENT_GFX_ROCKET_M', 22, 4, P + 'SilphGrunt1Sight', flag='FLAG_POX_HIDE_SILPH_GRUNT_1', sight=3),
             ],
             warp_events=[door(7, 21, CITY_ID, WARP_SILPH), door(8, 20, CITY_ID, WARP_SILPH),
                          door(9, 20, CITY_ID, WARP_SILPH), door(22, 3, 'MAP_SILPH_CO_11F', '0')],
             coord_events=[trigger(31, 2, 'LobbyStairs')],
             bg_events=[sign(30, 1, 'LobbySign')])
    save(LOBBY, d)
    map_scripts(LOBBY, ('MAP_SCRIPT_ON_TRANSITION', 'LobbyOnTransition'))

    # --- Silph 11F: two grunts, GIOVANNI, the terminal, then the staff ---
    d = load(BOARD)
    d.update(object_events=[
                 # Both corridors are two or three tiles wide and each grunt's
                 # sight covers the tiles he does not stand on.
                 npc('OBJ_EVENT_GFX_ROCKET_M', 16, 12, P + 'SilphGrunt2Sight', flag='FLAG_POX_HIDE_SILPH_GRUNT_2',
                     movement='MOVEMENT_TYPE_FACE_LEFT', sight=2),
                 npc('OBJ_EVENT_GFX_ROCKET_M', 0, 12, P + 'SilphGrunt3Sight', flag='FLAG_POX_HIDE_SILPH_GRUNT_3',
                     movement='MOVEMENT_TYPE_FACE_RIGHT', sight=2),
                 npc('OBJ_EVENT_GFX_GIOVANNI', 6, 11, 'Pox_Giovanni', flag='FLAG_POX_HIDE_SILPH_GIOVANNI',
                     local_id='LOCALID_POX_SILPH_GIOVANNI'),
                 npc('OBJ_EVENT_GFX_OLD_MAN_2', 9, 9, P + 'President', flag='FLAG_POX_HIDE_SILPH_STAFF',
                     local_id='LOCALID_POX_SILPH_PRESIDENT'),
                 npc('OBJ_EVENT_GFX_WORKER_F', 11, 9, P + 'Secretary', flag='FLAG_POX_HIDE_SILPH_STAFF',
                     local_id='LOCALID_POX_SILPH_SECRETARY'),
             ],
             warp_events=[door(13, 3, 'MAP_SILPH_CO_1F', '3'),   # warp 0: lift
                          door(2, 5, 'MAP_SILPH_CO_11F', '2'),    # warp 1: west pad -> east pad
                          door(16, 19, 'MAP_SILPH_CO_11F', '1')],  # warp 2: east pad -> west pad
             coord_events=[trigger(7, 2, 'BoardStairs'), trigger(5, 14, 'GiovanniTriggerLeft'),
                           trigger(6, 14, 'GiovanniTriggerRight')],
             bg_events=[sign(8, 1, 'BoardSign'),
                        dict(type='sign', x=5, y=7, elevation=0, player_facing_dir='BG_EVENT_PLAYER_FACING_NORTH',
                             script='Pox_SilphCore')])
    save(BOARD, d)
    map_scripts(BOARD, ('MAP_SCRIPT_ON_LOAD', 'BoardOnLoad'), ('MAP_SCRIPT_ON_TRANSITION', 'BoardOnTransition'))

    # --- old teleport rooms: empty, with a way out for a save made inside ---
    for name, warps in [('PlasticOx_BrunoGym', [door(5, 19, CITY_ID, WARP_DOJO), door(6, 19, CITY_ID, WARP_DOJO)]),
                        ('PlasticOx_Silph', [door(7, 9, CITY_ID, WARP_SILPH, 0), door(8, 9, CITY_ID, WARP_SILPH, 0)])]:
        d = load(name)
        d.update(object_events=[], warp_events=warps, coord_events=[], bg_events=[])
        save(name, d)

    # --- Dojo trainers: their own ids after the existing ones ---
    path = 'include/constants/opponents.h'
    s = read(path)
    for tid, number, _name, _party in DOJO_TRAINERS:
        if f'#define {tid} ' not in s:
            s = s.replace('// End Plastic Ox story trainers.', f'#define {tid} {number}\n// End Plastic Ox story trainers.')
    top = max(number for _tid, number, _name, _party in DOJO_TRAINERS) + 1
    for constant in ['TRAINERS_COUNT_EMERALD', 'MAX_TRAINERS_COUNT_EMERALD']:
        s = re.sub(r'(#define ' + constant + r'\s+)(\d+)', lambda m: m[1] + str(max(top, int(m[2]))), s)
    put(path, s)
    path = 'src/data/trainers.party'
    s = read(path)
    for tid, _number, name, party in DOJO_TRAINERS:
        head = (f'=== {tid} ===\nName: {name}\nClass: Black Belt\nPic: Black Belt\nGender: Male\nMusic: Intense\n'
                'Double Battle: No\nAI: Basic Trainer / Smart Switching / PP Stall Prevention\n\n')
        m = re.search(r'^=== ' + tid + r' ===\n.*?\n\n', s, flags=re.M | re.S)
        if m:  # party body belongs to plastic_ox/tools/apply_trainer_teams_v2.py
            s = s[:m.start()] + head + s[m.end():]
        else:
            s = s.rstrip('\n') + '\n\n' + head + party
    put(path, s)

    put('data/scripts/plastic_ox_saffron.inc', scripts())
    path = 'data/event_scripts.s'
    s = read(path)
    line = '\t.include "data/scripts/plastic_ox_saffron.inc"\n'
    if line not in s:
        s += '\n' + line
    put(path, s)
