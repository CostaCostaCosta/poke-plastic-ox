"""Battle Frontier (bible: Postgame — Lavender South Opens).

Each Frontier house holds one ADV tier. Its attendant runs a seven-battle round
against teams drawn at random from plastic_ox/frontier/ (compiled into
src/data/plastic_ox_frontier_teams.h by plastic_ox/tools/build_frontier_teams.py;
src/plastic_ox_frontier.c builds the parties). The house checks the player's
party with the same tier rules as the gyms.

Access: after the Hall of Fame, MOM calls the player over on returning to
Pallet (or when spoken to at home); OAK hands over ITEM_FRONTIER_INVITE and sets
FLAG_POX_FRONTIER_INVITE, which opens Lavender's south harbor and the harbor's
Frontier gangway (region_v7.py PORTS).

This module installs:
* TRAINER_PLASTIC_OX_FRONTIER_<TIER> (one opponent per house; the party block
  is a placeholder, replaced at battle time);
* the attendants in each house lobby, hiding the vanilla doubles/multis desks;
* data/scripts/plastic_ox_frontier.inc;
* hooks in OAK's lab, MOM's house, Pallet's arrival and Lavender's road crew.
Runs after region generation (it patches the Pallet arrival callback).
"""
import json
import re
from pathlib import Path

FIRST_TRAINER_ID = 968

# New persistent flags (POX_EXT pool; see the plastic-ox-flags skill).
EXT_FLAGS = [
    ('FLAG_POX_FRONTIER_INVITE', 27, "OAK gave the FRONTIER INVITE; opens Lavender's south harbor and the Frontier gangway."),
    ('FLAG_POX_FRONTIER_MOM_TOLD', 28, "MOM has sent the new Champion to OAK's lab (Pallet arrival or a talk at home)."),
] + [(f'FLAG_POX_FRONTIER_CLEARED_{key}', 29 + i, f'Frontier: first seven-win {key} round.')
     for i, key in enumerate(['LC', 'PU', 'NU', 'RU', 'UU', 'OU', 'UBERS'])]
AI = 'Basic Trainer / Smart Switching / PP Stall Prevention'

# (tier key, display name, house map, house name, attendant, vanilla desks to hide,
#  trainer name, class, pic, gender)
HOUSES = [
    ('LC', 'LITTLE CUP', 'BattleFrontier_BattlePyramidLobby', 'BATTLE PYRAMID',
     'LOCALID_PYRAMID_LOBBY_ATTENDANT', ['LOCALID_PYRAMID_LOBBY_HINT_GIVER'],
     'TIMMY', 'Youngster', 'Youngster', 'Male'),
    ('PU', 'PU', 'BattleFrontier_BattlePikeLobby', 'BATTLE PIKE',
     'LOCALID_PIKE_LOBBY_ATTENDANT', [],
     'BRANT', 'Hiker', 'Hiker', 'Male'),
    ('NU', 'NU', 'BattleFrontier_BattleFactoryLobby', 'BATTLE FACTORY',
     'LOCALID_FACTORY_ATTENDANT_SINGLES', ['LOCALID_FACTORY_ATTENDANT_DOUBLES'],
     'NOELLE', 'Pkmn Breeder', 'Pokemon Breeder F', 'Female'),
    ('RU', 'RU', 'BattleFrontier_BattleArenaLobby', 'BATTLE ARENA',
     'LOCALID_ARENA_ATTENDANT', [],
     'RIKU', 'Black Belt', 'Black Belt', 'Male'),
    ('UU', 'UU', 'BattleFrontier_BattlePalaceLobby', 'BATTLE PALACE',
     'LOCALID_PALACE_ATTENDANT_SINGLES', ['LOCALID_PALACE_ATTENDANT_DOUBLES'],
     'UMA', 'Cooltrainer', 'Cooltrainer F', 'Female'),
    ('UBERS', 'UBERS', 'BattleFrontier_BattleDomeLobby', 'BATTLE DOME',
     'LOCALID_DOME_ATTENDANT_SINGLES', ['LOCALID_DOME_ATTENDANT_DOUBLES'],
     'DOMINIC', 'Cooltrainer', 'Cooltrainer M', 'Male'),
    ('OU', 'OU', 'BattleFrontier_BattleTowerLobby', 'BATTLE TOWER',
     'LOCALID_TOWER_ATTENDANT_SINGLES', ['LOCALID_TOWER_ATTENDANT_DOUBLES',
     'LOCALID_TOWER_ATTENDANT_MULTIS', 'LOCALID_TOWER_ATTENDANT_LINK_MULTIS'],
     'ALDOUS', 'Gentleman', 'Gentleman', 'Male'),
]

# One welcome per house (no two NPCs share dialogue).
WELCOME = {
    'LC': 'Welcome to the BATTLE PYRAMID.\nThis house holds LITTLE CUP rounds.',
    'PU': 'Welcome to the BATTLE PIKE.\nThis house holds PU rounds.',
    'NU': 'Welcome to the BATTLE FACTORY.\nThis house holds NU rounds.',
    'RU': 'Welcome to the BATTLE ARENA.\nThis house holds RU rounds.',
    'UU': 'Welcome to the BATTLE PALACE.\nThis house holds UU rounds.',
    'UBERS': 'Welcome to the BATTLE DOME.\nThis house holds UBERS rounds.\\pAnything goes here, legends too.',
    'OU': 'Welcome to the BATTLE TOWER.\nThis house holds OU rounds.\\pThe standard game, no legends\nfrom the UBERS list.',
}
CLEARED = {
    'LC': "Your name's already on the\nPYRAMID board. Back for more?",
    'PU': 'The PIKE remembers your\nseven-win round. Again?',
    'NU': 'You cleared the FACTORY once.\nShall we see if it holds?',
    'RU': 'The ARENA crowd still talks\nabout your round. Another?',
    'UU': 'The PALACE has your clear\non record. One more round?',
    'UBERS': 'You conquered the DOME.\nCare to prove it twice?',
    'OU': 'Your TOWER clear is posted\nby the door. Ready again?',
}
TRAINER_DEFEAT = {
    'LC': 'Small team, big lesson.',
    'PU': 'Not bad. Not bad at all.',
    'NU': 'You read every switch.',
    'RU': 'Clean hits. I yield.',
    'UU': 'Your team was the better one.',
    'UBERS': 'Even legends fall, it seems.',
    'OU': 'Beaten fair and square.',
}
GUARDS = [
    ('LavenderTown_EventScript_SouthRoadClosed', "The FRONTIER harbor's open now.\nWatch your step on the gangway."),
    ('LavenderTown_EventScript_SouthRoadClosed_2', 'The embankment held. Ferries run\nto the FRONTIER all day now.'),
    ('LavenderTown_EventScript_SouthRoadClosed_3', "PROF. OAK's letter, huh?\nGo on through, Champion."),
]


def esc(text):
    """Python newlines -> the script compiler's \\n."""
    return text.replace('\n', '\\n')


def trainer_block(i, house):
    key, _, _, _, _, _, name, cls, pic, gender = house
    return (f'=== TRAINER_PLASTIC_OX_FRONTIER_{key} ===\nName: {name}\nClass: {cls}\nPic: {pic}\n'
            f'Gender: {gender}\nMusic: Intense\nDouble Battle: No\nAI: {AI}\n\n'
            'Magikarp\nLevel: 5\n- Splash\n')


def house_script(i, house):
    """One house's desk. Every line names the house, so no two attendants share text."""
    key, tier, _, name = house[:4]
    t = f'PoxFrontier_{key}'
    texts = {
        'Welcome': WELCOME[key],
        'Again': CLEARED[key],
        'Rules': f'Seven straight wins clears the\n{name}.\\pEvery POKéMON must be {tier}-\nlegal, with the ADV clauses.\\pYou are healed after each win.\nShall we begin?',
        'Declined': f'The {name} is open\nwhenever you are ready.',
        'Begin': f'Your first {name}\nopponent is on the way.',
        'Opponent': f'{name}, battle {{STR_VAR_1}}\nof seven. Good luck!',
        'Continue': f"That's {{STR_VAR_1}} {name} wins.\nYour POKéMON have been healed.\\pTake on the next opponent?",
        'Lost': f'That ends your {name}\nround. Your POKéMON are healed.\\pCome back and try again!',
        'Retire': f"You've retired from the\n{name} round. Come again!",
        'Cleared': f"Seven straight wins! You've\ncleared the {name}.\\pYour name goes up on the\nboard by the door.",
        'Defeat': TRAINER_DEFEAT[key],
        'RefuseMove': f'The {name} uses\n{tier} rules.\\p{{STR_VAR_1}}\'s {{STR_VAR_2}}\nis banned here.',
        'RefuseItem': f"The {name} uses\n{tier} rules.\\p{{STR_VAR_1}} can't hold\n{{STR_VAR_2}} here.",
        'RefuseSpecies': f'The {name} uses\n{tier} rules.\\p{{STR_VAR_2}} is over the tier.\nPlease leave {{STR_VAR_1}} in the PC.',
        'RefuseDuplicate': f'The {name} uses\n{tier} rules.\\p{{STR_VAR_1}} is a second\n{{STR_VAR_2}}. Only one each.',
        'RefuseAbility': f'The {name} uses\n{tier} rules.\\p{{STR_VAR_1}} has {{STR_VAR_2}}.\nThat ability is banned here.',
        'RefuseBatonPass': f"The {name} uses\n{tier} rules.\\p{{STR_VAR_1}}'s BATON PASS set\nbreaks the Baton Pass clause.",
    }
    end = '\trelease\n\tend\n'
    refuse = ''.join(f'\tgoto_if_eq VAR_RESULT, {n}, {t}_{r}\n' for n, r in
                     [(1, 'RefuseMove'), (2, 'RefuseItem'), (3, 'RefuseSpecies'), (4, 'RefuseDuplicate'), (5, 'RefuseAbility')])
    body = f'''{t}_Attendant::
	lock
	faceplayer
	call_if_set FLAG_POX_FRONTIER_CLEARED_{key}, {t}_Again
	call_if_unset FLAG_POX_FRONTIER_CLEARED_{key}, {t}_Welcome
	goto_if_eq VAR_RESULT, NO, {t}_Declined
	setvar VAR_0x8004, {i}
	specialvar VAR_RESULT, PoxFrontier_CheckRules
	goto_if_ne VAR_RESULT, 0, {t}_Refuse
	setvar VAR_0x8004, {i}
	special PoxFrontier_Begin
	msgbox {t}_Text_Begin, MSGBOX_DEFAULT
{t}_Next::
	special PoxFrontier_NextOpponent
	msgbox {t}_Text_Opponent, MSGBOX_DEFAULT
	closemessage
	cleartrainerflag TRAINER_PLASTIC_OX_FRONTIER_{key}
	trainerbattle_no_intro TRAINER_PLASTIC_OX_FRONTIER_{key}, {t}_Text_Defeat
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_ne VAR_RESULT, B_OUTCOME_WON, {t}_Lost
	special HealPlayerParty
	specialvar VAR_RESULT, PoxFrontier_RecordWin
	goto_if_eq VAR_RESULT, TRUE, {t}_Cleared
	msgbox {t}_Text_Continue, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, {t}_Retire
	goto {t}_Next
{t}_Cleared::
	setflag FLAG_POX_FRONTIER_CLEARED_{key}
	special PoxFrontier_End
	playfanfare MUS_OBTAIN_SYMBOL
	msgbox {t}_Text_Cleared, MSGBOX_DEFAULT
	waitfanfare
{end}{t}_Lost::
	special PoxFrontier_End
	special HealPlayerParty
	msgbox {t}_Text_Lost, MSGBOX_DEFAULT
{end}{t}_Retire::
	special PoxFrontier_End
	msgbox {t}_Text_Retire, MSGBOX_DEFAULT
{end}{t}_Declined::
	msgbox {t}_Text_Declined, MSGBOX_DEFAULT
{end}{t}_Welcome::
	msgbox {t}_Text_Welcome, MSGBOX_DEFAULT
	msgbox {t}_Text_Rules, MSGBOX_YESNO
	return
{t}_Again::
	msgbox {t}_Text_Again, MSGBOX_YESNO
	return
{t}_Refuse::
{refuse}	msgbox {t}_Text_RefuseBatonPass, MSGBOX_DEFAULT
{end}'''
    for r in ('RefuseMove', 'RefuseItem', 'RefuseSpecies', 'RefuseDuplicate', 'RefuseAbility'):
        body += f'{t}_{r}::\n\tmsgbox {t}_Text_{r}, MSGBOX_DEFAULT\n{end}'
    body += '\n' + ''.join(f'{t}_Text_{k}::\n\t.string "{esc(v)}$"\n' for k, v in texts.items()) + '\n'
    return body


COMMON = r'''@ Battle Frontier scripts. Generated by plastic_ox/alpha/frontier.py.

@ Postgame hand-off: MOM -> OAK -> FRONTIER INVITE -> Lavender's south harbor.
PoxFrontier_PalletArrival::
	goto_if_unset FLAG_SYS_GAME_CLEAR, PoxFrontier_Return
	goto_if_set FLAG_POX_FRONTIER_MOM_TOLD, PoxFrontier_Return
	goto_if_set FLAG_POX_FRONTIER_INVITE, PoxFrontier_Return
	setvar VAR_POX_MOM_STATE, 2
PoxFrontier_Return::
	return

PoxFrontier_PalletFrameTable::
	map_script_2 VAR_POX_MOM_STATE, 2, PoxFrontier_MomCalls
	.2byte 0

PoxFrontier_MomCalls::
	lockall
	setvar VAR_POX_MOM_STATE, 1
	setflag FLAG_POX_FRONTIER_MOM_TOLD
	msgbox PoxFrontier_Text_MomCalls, MSGBOX_DEFAULT
	releaseall
	end

PoxFrontier_MomAtHome::
	goto_if_unset FLAG_SYS_GAME_CLEAR, PoxFrontier_Return
	goto_if_set FLAG_POX_FRONTIER_INVITE, PoxFrontier_Return
	setflag FLAG_POX_FRONTIER_MOM_TOLD
	msgbox PoxFrontier_Text_MomAtHome, MSGBOX_DEFAULT
	return

PoxFrontier_Oak::
	goto_if_set FLAG_POX_FRONTIER_INVITE, PoxFrontier_OakAfter
	msgbox PoxFrontier_Text_OakInvite, MSGBOX_DEFAULT
	giveitem ITEM_FRONTIER_INVITE
	goto_if_eq VAR_RESULT, FALSE, PoxFrontier_OakBagFull
	setflag FLAG_POX_FRONTIER_INVITE
	setflag FLAG_POX_FRONTIER_MOM_TOLD
	msgbox PoxFrontier_Text_OakDirections, MSGBOX_DEFAULT
	release
	end
PoxFrontier_OakBagFull::
	msgbox PoxFrontier_Text_OakBagFull, MSGBOX_DEFAULT
	release
	end
PoxFrontier_OakAfter::
	msgbox PoxFrontier_Text_OakAfter, MSGBOX_DEFAULT
	setvar VAR_0x8004, 0
	call PoxProf_Talk
	release
	end

PoxFrontier_Text_MomCalls::
	.string "MOM: {PLAYER}! Over here!\p"
	.string "The CHAMPION, my own child!\n"
	.string "I watched it all on TV!\p"
	.string "PROFESSOR OAK called, too.\n"
	.string "He wants to see you at his lab.$"

PoxFrontier_Text_MomAtHome::
	.string "MOM: Oh, before I forget!\n"
	.string "PROFESSOR OAK wants to see you.\p"
	.string "He said it was about something\n"
	.string "past LAVENDER TOWN.$"

PoxFrontier_Text_OakInvite::
	.string "OAK: {PLAYER}! CHAMPION!\n"
	.string "I knew you had it in you.\p"
	.string "A champion shouldn't run out of\n"
	.string "challengers. So, take this.$"

PoxFrontier_Text_OakBagFull::
	.string "OAK: Your BAG is full!\n"
	.string "Make some room and come back.$"

PoxFrontier_Text_OakDirections::
	.string "OAK: That's an invitation to the\n"
	.string "BATTLE FRONTIER.\p"
	.string "Head south of LAVENDER TOWN.\n"
	.string "Show it at the harbor there.\p"
	.string "Each house there holds a\n"
	.string "different tier. Try them all!$"

PoxFrontier_Text_OakAfter::
	.string "OAK: The FRONTIER harbor is south\n"
	.string "of LAVENDER TOWN. Off you go!$"

PoxFrontier_Text_HarborClosed::
	.string "The harbor ahead is for BATTLE\n"
	.string "FRONTIER guests only.\p"
	.string "You need an invitation to board.$"
'''


def guard_script(i, label, text):
    return (f'PoxFrontier_LavenderGuard{i}::\n\tmsgbox PoxFrontier_LavenderGuard{i}_Text, MSGBOX_NPC\n\tend\n'
            f'PoxFrontier_LavenderGuard{i}_Text::\n\t.string "{esc(text)}$"\n\n')


def insert_after(text, anchor, line, path):
    if line in text:
        return text
    if anchor not in text:
        raise SystemExit(f'{path}: no {anchor.strip()!r}')
    return text.replace(anchor, anchor + line, 1)


def install(read, put):
    path = 'include/constants/plastic_ox_flags.h'
    header = read(path)
    block = ''.join(f'// {comment}\n#define {name} (POX_EXT_FLAGS_START + {n})\n' for name, n, comment in EXT_FLAGS)
    begin, end = '// Battle Frontier (plastic_ox/alpha/frontier.py).\n', '// End Battle Frontier flags.\n'
    header = re.sub(re.escape(begin) + '.*?' + re.escape(end) + '\n?', '', header, flags=re.S)
    header = header.replace('#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H',
                            begin + block + end + '\n#endif // GUARD_CONSTANTS_PLASTIC_OX_FLAGS_H')
    put(path, header)

    # Opponents.
    path = 'include/constants/opponents.h'
    text = re.sub(r'#define TRAINER_PLASTIC_OX_FRONTIER_\w+ \d+\n', '', read(path))
    for i, house in enumerate(HOUSES):
        define = f'#define TRAINER_PLASTIC_OX_FRONTIER_{house[0]} {FIRST_TRAINER_ID + i}\n'
        if define not in text:
            text = text.replace('// End Plastic Ox story trainers.', define + '// End Plastic Ox story trainers.')
    last = FIRST_TRAINER_ID + len(HOUSES)
    for constant in ['TRAINERS_COUNT_EMERALD', 'MAX_TRAINERS_COUNT_EMERALD']:
        text = re.sub(r'(#define ' + constant + r'\s+)(\d+)',
                      lambda m: m[1] + str(max(last, int(m[2]))), text)
    put(path, text)

    path = 'src/data/trainers.party'
    text = re.sub(r'=== TRAINER_PLASTIC_OX_FRONTIER_\w+ ===\n.*?(?=\n=== |\Z)', '', read(path), flags=re.S)
    put(path, text.rstrip() + '\n\n' + '\n'.join(trainer_block(i, h) for i, h in enumerate(HOUSES)))

    # House lobbies: the singles desk runs the tier; the other desks close.
    for key, _, house_map, _, attendant, hide, *_ in HOUSES:
        path = f'data/maps/{house_map}/map.json'
        lobby = json.loads(read(path))
        found = set()
        for obj in lobby['object_events']:
            if obj.get('local_id') == attendant:
                obj['script'] = f'PoxFrontier_{key}_Attendant'
                found.add(attendant)
            elif obj.get('local_id') in hide:
                obj['flag'] = 'FLAG_SYS_GAME_CLEAR'
                found.add(obj['local_id'])
        missing = {attendant, *hide} - found
        if missing:
            raise SystemExit(f'{path}: no {sorted(missing)}')
        put(path, json.dumps(lobby, indent=2) + '\n')

    # Scripts.
    body = COMMON + '\n' + ''.join(house_script(i, h) for i, h in enumerate(HOUSES))
    body += ''.join(guard_script(i + 1, label, text) for i, (label, text) in enumerate(GUARDS))
    put('data/scripts/plastic_ox_frontier.inc', body)
    text = read('data/event_scripts.s')
    line = '\t.include "data/scripts/plastic_ox_frontier.inc"\n'
    if line not in text:
        text = text.rstrip('\n') + '\n' + line
    put('data/event_scripts.s', text)

    # Pallet: MOM calls on arrival (region callback + frame table).
    path = 'data/scripts/plastic_ox_region.inc'
    put(path, insert_after(read(path), 'PoxRegion_Arrival_PalletTown_Frlg::\n',
                           '\tcall PoxFrontier_PalletArrival\n', path))
    path = 'data/maps/PalletTown_Frlg/scripts.inc'
    put(path, insert_after(read(path), '\tmap_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_PalletTown_Frlg\n',
                           '\tmap_script MAP_SCRIPT_ON_FRAME_TABLE, PoxFrontier_PalletFrameTable\n', path))
    # MOM at home, before her usual rest.
    path = 'data/maps/PalletTown_PlayersHouse_1F_Frlg/scripts.inc'
    put(path, insert_after(read(path), '\tgoto_if_unset FLAG_POX_STORY_STARTER, PalletTown_Mom_BeforeStarter\n',
                           '\tcall PoxFrontier_MomAtHome\n', path))
    # OAK hands over the invite once the player is Champion.
    path = 'data/scripts/plastic_ox_pallet.inc'
    put(path, insert_after(read(path), 'Pox_Oak::\n    goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End\n    lock\n    faceplayer\n    call Pox_LabIntroduction\n',
                           '    goto_if_set FLAG_SYS_GAME_CLEAR, PoxFrontier_Oak\n', path))
    # Lavender's south road crew stand aside for invite holders.
    path = 'data/maps/LavenderTown_hns/scripts.inc'
    text = read(path)
    for i, (label, _) in enumerate(GUARDS):
        text = insert_after(text, f'{label}::\n', f'\tgoto_if_set FLAG_POX_FRONTIER_INVITE, PoxFrontier_LavenderGuard{i + 1}\n', path)
    put(path, text)


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    install(lambda p: (root / p).read_text(),
            lambda p, s: ((root / p).parent.mkdir(parents=True, exist_ok=True),
                          (root / p).write_text(s)))
