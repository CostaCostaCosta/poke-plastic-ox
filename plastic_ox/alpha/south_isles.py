"""Cinnabar Island, the Seafoam passage and Mossdeep City: dialogue and world pass.

Installed last by region_v7.apply_region, after cinnabar.py / seafoam.py /
lavender.py, so it owns the final wording of the stage 9-11 leg:

* Cinnabar: islanders with jobs (dock hand, greenhouse, lab), a mansion guide
  and gym regular who change with FLAG_BADGE05_GET / FLAG_POX_STORY_MANSION,
  BLAINE's own challenge, badge, key and after-mansion lines, the quiz
  trainers, the Mansion's archive files (re-readable, in period voice), the
  burglars and scientists inside, the lab and the Pokemon Center. The donor
  BILL / Seagallop props and the Center's One Island BILL are gone.
* Seafoam: an ice cutter and a swimmer at the two doors, the B4F signs, a
  fisherman and a sign on the Route 20 West landing.
* Gym guides at Cinnabar and Mossdeep check the party against the gym's
  rules special (warn, not block); the ENTEI sage waits for archive FILE 3.
* Mossdeep: the Magma people are deleted and unreachable scripts pruned; the
  houses, Steven's house and the Game Corner speak their own lines; Route 20
  West gets a UU sea table (East stays barren).
* Mossdeep: the town speaks in tides and launch windows, the SAFFRON sailor
  and the launch-board woman change with FLAG_POX_STORY_SPACE_CENTER, TATE &
  LIZA get their own challenge / refusal / badge lines, the Gym guide stops
  describing the Hoenn gym, and the Space Center's EEVEE is retired, not
  awarded.

Every edit is idempotent: the module can be run on its own over the checkout
(python3 plastic_ox/alpha/south_isles.py) or as the last step of build_story.

Story sources: plastic_ox/story/locations/cinnabarisland-frlg.md,
plasticox-route20west.md, plasticox-route20east.md, mossdeepcity.md.
"""
import json
import re
import textwrap
from pathlib import Path

P = 'PoxIsles_'
MANSION = 'FLAG_POX_STORY_MANSION'
SPACE = 'FLAG_POX_STORY_SPACE_CENTER'
UNUSED = 'FLAG_POX_HIDE_UNUSED_ACTOR'


def pages(body):
    """'|' separates message boxes; a long paragraph wraps to 32 columns and
    scrolls (\\l) past its second line, as the vanilla text does."""
    out = []
    for paragraph in body.split('|'):
        lines = textwrap.wrap(paragraph, 32)
        out.append(lines[0] + ''.join(('\\n' if i == 1 else '\\l') + line for i, line in enumerate(lines[1:], 1)))
    return '\\p'.join(out)


def raw(*boxes):
    """Hand-laid text (signs, documents): one argument per box, newline per line."""
    return ('raw', '\\p'.join(box.replace('\n', '\\n') for box in boxes))


def string(body):
    return '\t.string "' + (body[1] if isinstance(body, tuple) else pages(body)) + '$"\n'


# --------------------------------------------------------------------------
# New scripts. Each entry: label -> text, or label -> [default, (flag, text)...]
# where later stages win. Labels ending in Sign use MSGBOX_SIGN.
# --------------------------------------------------------------------------
NPCS = {
    # --- Cinnabar Island ---
    'MansionGuide': [
        "That's the old research house. Nobody has lived in it since the fire.|BLAINE keeps it locked and keeps the key on him. He'll lock a house. He won't lock a GYM.",
        ('FLAG_POX_MANSION_KEY', "So he gave you the SECRET KEY. He doesn't do that.|Mind the statues inside. Press one and half the doors shut while the other half open.|There's a SAGE in the basement who came over on the supply boat. He isn't lost. He's keeping something company."),
        (MANSION, "You were in there a long time. You came out reading the ground, the way BLAINE does.|I'll keep an eye on the door. Somebody should."),
    ],
    'GymRegular': [
        "The GYM is up the street, door wide open since spring. Six questions and a man who hates to lose.|I have a week of tomatoes on you missing question four. Everybody misses question four.",
        ('FLAG_BADGE05_GET', "Six for six, or did you fight your way through? Don't tell me. I'll say six.|BLAINE hasn't handed that key to anyone in years. Use it before he thinks better of it."),
        (MANSION, "The whole island knows you went through the house. Nobody is going to ask what was in it.|We bet on quiz doors here. We don't bet on that."),
    ],
    'DockHand': [
        "Sea's flat as a plate and I still can't take you anywhere. The ferry is off the timetable.|The east channel is for people with business east. Yours is with BLAINE first.",
        ('FLAG_BADGE05_GET', "That's BLAINE's key in your bag. His rule: nobody crosses with the house on the hill still unread.|He wants it used, not carried off the island."),
        (MANSION, "Read the lot, did you. Then the east channel is yours.|Straight out from this quay and hold for the black rock. The door into SEAFOAM is on its south face."),
    ],
    'Greenhouse': "The ash is good for one thing. Tomatoes.|We pipe the hot water under the beds. Ripe in midwinter, and they taste a little of matches.",
    'LabTech': "Coffee break. The pot in the LAB hasn't been switched off since before I was hired.|We revive fossils, mostly. It's quieter work than what they used to do up the hill.",
    # --- Seafoam Islands 1F ---
    'IceCutter': [
        "I cut ice for the MOSSDEEP boats. Thirty blocks a tide, when the cave lets me.|Shove the boulders down the holes and they dam the current below. Walk out before the job is done and the water takes the rocks back.",
        ('FLAG_POX_STOPPED_SEAFOAM_B4F_CURRENT', "Hear that? Nothing. The lower channel hasn't been this quiet since I was a boy.|It'll hold now. Good work, whoever did it."),
    ],
    'Swimmer': "I swam in from the MOSSDEEP side to get out of the sun. Flat water the whole way.|You'll see the launch tower before you see the beach.",
    # --- Route 20 West landing ---
    'Angler': "Two hours out of CINNABAR and the wind turned. My line has been dry since the turn.|The cave breathes on the ebb. If you can feel it pulling, you're already at the door.",
    'CaveSign': raw("SEAFOAM ISLANDS - WEST DOOR\nNo landing past this rock.", "Watch the swell."),
    # --- Mossdeep City ---
    'SaffronSailor': [
        "The north shore runs up ROUTE 19 to SAFFRON. The water gets you there long before the gate lets you in.|The city has been shut a good while. Nobody has said why. I just turn the boats around.",
        (SPACE, "SAFFRON is open. It came down the wire this morning and nobody here looked surprised but me.|North shore, ROUTE 19, same as ever. Only now the gate is the easy part."),
    ],
    'LaunchBoard': [
        "The launch board outside the SPACE CENTER says soon. The date under it has been pasted over three times.|When it goes, the school shuts and the boats stay in. So we all watch the board.",
        (SPACE, "They pasted a fourth date on the launch board. Then somebody took the board down.|I don't know what they found over there. They have stopped arguing about the wind, I know that."),
    ],
    'DockClerk': "You came out of the cave? Then you're the first thing I've logged all morning.|Ferry is at six and six. The GYM is up the hill, and the white roof past it is the SPACE CENTER.",
    'SchoolKid': "The board says the next launch is soon. It has said soon since my brother was little.|We get the day off when it goes. I've had my bag packed for a year.",
    # --- Mossdeep Game Corner: the link cabinets are dark (POX_LINK_ENABLED is off) ---
    'ArcadeHost': "The link cabinets have been dark since the last storm took the aerial off the roof.|We keep the lights on anyway. People come in to get out of the wind.",
    'ArcadeOldTimer': "I held the POKéMON JUMP record here six summers running. The board still says so.|Nobody can beat it while the machines are off. I've decided that counts.",
    # --- story refusals / repeats that used the global Pox_NotReady / Pox_Done ---
    'BlaineNotReady': "BLAINE: Not yet. Four BADGES and a reason to be here. That is the door charge on this island.|Come back with both.",
    'TwinsNotReady': raw("TATE: Not yet.\nLIZA: Not quite yet.", "TATE: Five BADGES, and the long\nway round by sea.", "LIZA: Then we'll play."),
    'TwinsTwoMons': raw("TATE: It takes two…\nLIZA: …on both sides.", "TATE: Bring two POKéMON that can\nstill stand.", "LIZA: We'll wait."),
    'TwinsDone': raw("TATE: You already beat us.\nLIZA: We remember. We were there.", "TATE: The SPACE CENTER is east of\nthe GYM.", "LIZA: Past the white rock."),
    'Archive1Sealed': "The cabinet is locked. The keyhole is small and brass, the same pattern as the front door.",
    'Archive2Sealed': "FILE 2 is tied shut with string. A card under the knot reads: FILE 1 FIRST.",
    'Archive3Sealed': "FILE 3 is tied shut with string. A card under the knot reads: IN SEQUENCE. NO EXCEPTIONS.",
    'SpaceBusy': "Sorry, I can't stop. It's feeding time, and then the chief wants the logs.|If you're here about the survey, he's at the big console.",
    'ReportBusy': "Not now. I'm in the middle of a count.|Come back when TATE and LIZA have signed off on you. I want someone who has walked the whole road, from the start to here.",
}
REFUSALS = ('BlaineNotReady', 'TwinsNotReady', 'TwinsTwoMons', 'TwinsDone', 'Archive1Sealed', 'Archive2Sealed',
            'Archive3Sealed', 'SpaceBusy', 'ReportBusy')

# Text-only labels used by patched story scripts.
TEXTS = {
    'VolcanoBadge': raw("{PLAYER} received the VOLCANO BADGE\nfrom BLAINE."),
    'BlaineAfter': "BLAINE: You read them. I can tell. People come out of that house walking slower.|I kept that door shut for thirty years because I didn't understand what was behind it. I still don't. Now it's your problem as well.|The east quay will take you on. Tell FUJI I kept my end.",
    'MindBadge': raw("TATE: Best game all season.\nLIZA: Take the MIND BADGE.", "{PLAYER} received the MIND BADGE\nfrom TATE and LIZA.", "TATE: The SPACE CENTER people…\nLIZA: …count things.", "TATE: Go and be counted."),
    'SeaClosed': "A sharp whistle from the quay. The DOCK HAND is waving you back to shore.|The east channel isn't open to you yet.",
    'CrossingClosed': "The crossing to SEAFOAM is running hard. Your POKéMON turns back for the beach.",
    # The Entei sage waits for the whole archive (FLAG_POX_STORY_MANSION, set by FILE 3).
    'EnteiWaits': "SAGE: Not yet, if you please. My guest is listening to the house.|There are three files in these rooms. Read them all, in their order, then come back down.|ENTEI will know whether you have. I would rather it did not have to wonder.",
    # Gym guides run the gym's rules check (CheckCinnabarGymUURules /
    # CheckMossdeepGymUUBLRules), as the greeters in the other gyms do.
    # STR_VAR_1 is the POKéMON's nickname, STR_VAR_2 the move or item.
    'CinnabarRuleMove': raw("Hold on. {STR_VAR_1} knows\n{STR_VAR_2}.", "BLAINE doesn't allow that move in\nhere. It's a house rule.", "Swap it out before you get to him.\nThe whole island will hear if not."),
    'CinnabarRuleItem': raw("Hold on. {STR_VAR_1} is holding\n{STR_VAR_2}.", "BLAINE doesn't allow that item in\nhere. It's a house rule.", "Put it in your bag before you get\nto him."),
    'CinnabarRuleSpecies': raw("Hold on. {STR_VAR_1}? A {STR_VAR_2}\nis over this GYM's weight class.", "BLAINE keeps to UU in here.\nIt's a house rule.", "Leave it in the PC before you get\nto him."),
    'CinnabarRuleDuplicate': raw("Hold on. {STR_VAR_1} is a second\n{STR_VAR_2}.", "BLAINE battles one of each in here.\nIt's a house rule.", "Leave one in the PC before you get\nto him."),
    'CinnabarRuleAbility': raw("Hold on. {STR_VAR_1} has\n{STR_VAR_2}.", "BLAINE doesn't allow that ability in\nhere. It's a house rule.", "Leave it in the PC before you get\nto him."),
    'CinnabarRuleBatonPass': raw("Hold on. {STR_VAR_1} has BATON PASS\nwith {STR_VAR_2}.", "BLAINE won't battle that pairing in\nhere. It's a house rule.", "Change its moves before you get\nto him."),
    'CinnabarRuleBoostPasser': raw("Hold on. {STR_VAR_1} passes\n{STR_VAR_2} boosts too.", "BLAINE allows one boost passer in\nhere. It's a house rule.", "Change its moves before you get\nto him."),
    'CinnabarRuleClean': "I had a look at your team on the way in. Nothing BLAINE would object to. Go on, then.",
    'TwinsRuleMove': raw("Wait. {STR_VAR_1} knows\n{STR_VAR_2}.", "TATE and LIZA won't battle against\nthat move. Twins' rule.", "Change it before you cross the\nfloor, or they'll send you back."),
    'TwinsRuleItem': raw("Wait. {STR_VAR_1} is holding\n{STR_VAR_2}.", "TATE and LIZA won't battle against\nthat item. Twins' rule.", "Bag it before you cross the floor."),
    'TwinsRuleSpecies': raw("Wait. {STR_VAR_1}? A {STR_VAR_2}\nis over the twins' weight class.", "TATE and LIZA keep to UUBL.\nTwins' rule.", "Box it before you cross the floor."),
    'TwinsRuleDuplicate': raw("Wait. {STR_VAR_1} is a second\n{STR_VAR_2}.", "TATE and LIZA face one of each.\nTwins' rule.", "Box one before you cross the floor."),
    'TwinsRuleAbility': raw("Wait. {STR_VAR_1} has\n{STR_VAR_2}.", "TATE and LIZA won't battle against\nthat ability. Twins' rule.", "Box it before you cross the floor."),
    'TwinsRuleBatonPass': raw("Wait. {STR_VAR_1} has BATON PASS\nwith {STR_VAR_2}.", "TATE and LIZA won't battle against\nthat pairing. Twins' rule.", "Swap its moves before you cross."),
    'TwinsRuleBoostPasser': raw("Wait. {STR_VAR_1} passes\n{STR_VAR_2} boosts too.", "TATE and LIZA allow one boost\npasser. Twins' rule.", "Pick one passer before you cross."),
    'TwinsRuleClean': "Your team passes the twins' rules. I checked twice, the way they would.",
}

# --------------------------------------------------------------------------
# Replacement text for labels that already exist (file -> label -> text).
# --------------------------------------------------------------------------
STORY = 'data/scripts/plastic_ox_story.inc'
REGION = 'data/scripts/plastic_ox_region.inc'
M = 'data/maps/%s/scripts.inc'
REWRITES = {
    STORY: {
        'Pox_Text_Blaine': "BLAINE: Hah! Six doors and you're still standing. Good.|I fought fires on this island before I ever kept a GYM on it. I don't pick POKéMON to match the wallpaper. I pick the ones that hold.|Come on, then. Show me what you do with a locked door.",
        'Pox_Text_Blaine_Defeat': raw("BLAINE: Out. Clean out.\nNot an ember left."),
        'Pox_Text_MansionKey': "BLAINE: FUJI sent you. He wouldn't, unless it mattered. That is the only reason you're getting this.|The SECRET KEY opens the old research house up the hill. What's left of the records is inside, and I'm not the man to explain them.|Read them. All of them. Then lock up behind you.|Take these machines too: STRENGTH and ROCK SMASH. Outside a battle they do nothing until you hold the key for each. One of my old staff in the house still has the first.",
        'Pox_Text_Archive1': "ARCHIVE, FILE 1. Typed, with corrections in ink.|We are agreed on first principles. A stored POKéMON is not a picture of one. It is the living state, held.|If the state is not kept whole, what we return is not what was given to us. We have proved this once and will not prove it again.",
        'Pox_Text_Archive2': "ARCHIVE, FILE 2.|A state recorded in one place can be reconciled with a state recorded in another. We did not expect this to work.|What comes back resembles an earlier state. It is not a copy.|We stored them as states, not specimens. That distinction cost us a year, and it is the only part of this work I would defend.",
        'Pox_Text_Archive3': "ARCHIVE, FILE 3. The last page.|Recommendation, unanimous: the controls that rebuild a habitat must never be joined to a transfer network without limits.|We have seen what one room does. We decline to imagine a region.|Pencilled in the margin, in newer handwriting: ECRUTEAK. The BURNED TOWER. The same, and so much larger.|Clipped behind the page is a shipping slip. Remaining instruments sent east by sea, via SEAFOAM, to the observatory at MOSSDEEP.",
        'Pox_Text_TateLiza': raw("TATE: You came across the water.\nLIZA: And through the cave.", "TATE: There are two of us.\nLIZA: There are two of yours.", "TATE: Everything after that…\nLIZA: …is just manners."),
        'Pox_Text_Space': "This EEVEE rode along on our observations for two years. It adapts to wherever it is put, which is what we were measuring.|The study is closed. It shouldn't spend its days in a lab because our paperwork did.|It could use a road. You seem to have one.",
        'Pox_Text_Space_GiftDone': "How is EEVEE taking to the road? Don't write it down for us. We've stopped keeping that log.",
    },
    REGION: {
        'PoxRegion_cinnabar_sea_a_Text': raw("EAST QUAY\nROUTE 20 - SEAFOAM ISLANDS", "FERRY SERVICE SUSPENDED\nThe last sailing is scratched out."),
    },
    M % 'CinnabarIsland_Gym_Frlg': {
        'CinnabarIsland_Gym_Text_ErikIntro': "I wrote question four. Nobody gets question four.",
        'CinnabarIsland_Gym_Text_ErikDefeat': "Marked down. By a tourist.",
        'CinnabarIsland_Gym_Text_ErikPostBattle': "Technically the question is fair. Technically.|I've stopped taking complaints about it.",
        'CinnabarIsland_Gym_Text_QuinnIntro': "Wrong answer. That makes you mine.|I used to take things without asking, too.",
        'CinnabarIsland_Gym_Text_QuinnDefeat': "Caught red-handed. Again.",
        'CinnabarIsland_Gym_Text_QuinnPostBattle': "BLAINE caught me in his storeroom nine years ago. He handed me a mop instead of calling anyone.|I've been on this door since.",
        'CinnabarIsland_Gym_Text_AveryIntro': "I've read every answer key this GYM ever printed. You can't win.",
        'CinnabarIsland_Gym_Text_AveryDefeat': "The key was out of date!",
        'CinnabarIsland_Gym_Text_AveryPostBattle': "Six questions, two answers each. Sixty-four ways through, and people still guess.",
        'CinnabarIsland_Gym_Text_RamonIntro': "I like the heat in here. I just do.",
        'CinnabarIsland_Gym_Text_RamonDefeat': "Ow. Warm, that.",
        'CinnabarIsland_Gym_Text_RamonPostBattle': "No challengers since spring. I've been battling the boiler.",
        'CinnabarIsland_Gym_Text_DerekIntro': "I know why BLAINE keeps this GYM.",
        'CinnabarIsland_Gym_Text_DerekDefeat': "Fine. I'll tell you.",
        'CinnabarIsland_Gym_Text_DerekPostBattle': "He was lost on the mountain once, after dark. A burning bird lit his way down.|He has been paying that back ever since. That's the story. He says it was a lamp.",
        'CinnabarIsland_Gym_Text_DustyIntro': "I've seen a lot of GYMS from the inside. This is the only one that let me stay.",
        'CinnabarIsland_Gym_Text_DustyDefeat': "Yowza. Scorched.",
        'CinnabarIsland_Gym_Text_DustyPostBattle': "Half the island bets on which door stops a challenger. I had you down for five.",
        'CinnabarIsland_Gym_Text_ZacIntro': "Last question, last TRAINER. Fire is weak against H2O. Write that down.",
        'CinnabarIsland_Gym_Text_ZacDefeat': "Extinguished.",
        'CinnabarIsland_Gym_Text_ZacPostBattle': "BLAINE is through there. He was a firefighter, you know.|He knows more ways to put a thing out than to light it.",
        'CinnabarIsland_Gym_Text_GymGuyAdvice': "Yo! Champ in the making! Forget the BURN HEALS.|BLAINE's team isn't the fire brigade you're picturing. He picks whatever holds a line: rock, water, a ghost.|He keeps to this GYM's weight class, too: nothing heavier than UU, no one-hit KO moves, no evasion tricks. Let me look at your team.|Answer the quiz right and you walk straight through. Answer wrong and you get a TRAINER and some exercise.",
        'CinnabarIsland_Gym_Text_GymGuyPostVictory': "{PLAYER}! You put the old firefighter out!|He gave you the house key? Then I'm staying down here, where it's warm.",
        'CinnabarIsland_Gym_Text_GymStatue': raw("CINNABAR ISLAND POKéMON GYM\nLEADER: BLAINE", "The Hotheaded Quiz Master!"),
        'CinnabarIsland_Gym_Text_GymStatuePlayerWon': raw("CINNABAR ISLAND POKéMON GYM\nLEADER: BLAINE", "WINNING TRAINERS:\n{PLAYER}"),
        'CinnabarIsland_Gym_Text_PokemonQuizRules': "The CINNABAR GYM quiz! A house tradition since before the fire.|Right answer, and the door opens. Wrong answer, and you face a TRAINER.|The island has tomatoes riding on you. Here we go!",
    },
    M % 'CinnabarIsland_PokemonCenter_1F_Frlg': {
        'CinnabarIsland_PokemonCenter_1F_Text_CinnabarGymLocked': "I came for the GYM and stayed for the hot spring. There isn't one. The ash filled it in years ago.|The quiz is real, though. Six doors. I got through five on brains and one on my GOLDUCK.",
        'CinnabarIsland_PokemonCenter_1F_Text_VisitUnionRoom': "I booked a return ticket. The return was scratched off the board the day I landed.|I have read every magazine in this lobby twice. The tomatoes are good, I'll say that.",
        'CinnabarIsland_PokemonCenter_1F_Text_EvolutionCanWaitForNewMoves': "Everybody here bets on the GYM quiz. Tomatoes, mostly.|I bet you'd miss one. Did you miss one?",
    },
    M % 'CinnabarIsland_Mart_Frlg': {
        'CinnabarIsland_Mart_Text_DontTheyHaveXAttack': "The shelves fill up when a boat gets in, and not before.|Buy the REVIVES while you're looking at them.",
        'CinnabarIsland_Mart_Text_ExtraItemsNeverHurt': "Two ESCAPE ROPES. I'm going back into the old house for my notebooks, and I am not walking out the long way.",
    },
    M % 'CinnabarIsland_PokemonLab_Entrance_Frlg': {
        'CinnabarIsland_PokemonLab_Entrance_Text_StudyMonsExtensively': "We study fossils here. People bring them over from MT. MOON in biscuit tins.|The older work, the work this island was known for, went up the hill and didn't come back down.",
        'CinnabarIsland_PokemonLab_Entrance_Text_PhotoOfLabFounderDrFuji': raw("A photo of the LAB's founder.\nThe plate reads: DR. FUJI.", "He is younger here, and smiling at\nsomething just out of frame."),
    },
    M % 'CinnabarIsland_PokemonLab_Lounge_Frlg': {
        'CinnabarIsland_PokemonLab_Lounge_Text_FoundFossilInMtMoon': "I found this in MT. MOON. I think it's a fossil. My colleague thinks it's a rock.|We've agreed to let the machine decide.",
    },
    M % 'CinnabarIsland_PokemonLab_ResearchRoom_Frlg': {
        'CinnabarIsland_PokemonLab_ResearchRoom_Text_EeveeCanEvolveIntroThreeMons': "They kept EEVEE here once, for the way it changes with its surroundings.|One went to LAVENDER with the founder. I heard another ended up at a launch site, of all places.",
        'CinnabarIsland_PokemonLab_ResearchRoom_Text_LegendaryBirdEmail': raw("A printed message is pinned up.", "From: FIELD TEAM", "Fishing boats east of here report\nice on their nets. At this latitude.", "We would like a boat and a week.", "Pencilled underneath:\nNo boat. Ask again in spring."),
    },
    M % 'PokemonMansion_1F_Frlg': {
        'PoxMansion_Text_StrengthKeyIntro': "Careful with that shelf. If it's brittle, it's important.|BLAINE sent word you'd be through. He asked me to give you this. It's the STRENGTH KEY, from when we still moved the big cabinets ourselves.",
        'PoxMansion_Text_StrengthKeyOwned': "With the STRENGTH KEY a POKéMON can shove boulders aside outside of battle.|You'll want that wherever the sea has been rearranging a cave.",
        'PoxMansion_Text_StrengthKeyBagFull': "Your KEY ITEMS POCKET is full. Make room and come back.|I'm not going anywhere. Clearly.",
        'PoxMansion_Text_Explorer': "I came in on a dare. It isn't even scary. It's just paper. Rooms and rooms of paper.|There's a man from the LAB further in who has been here all day. He talks to the shelves.",
    },
    M % 'PokemonMansion_2F_Frlg': {
        'PokemonMansion_1F_Text_ArnieIntro': "Nothing in here but filing cabinets! Who locks up filing cabinets!",
        'PokemonMansion_1F_Text_ArnieDefeat': "My bag of loot! It's all carbon paper!",
        'PokemonMansion_1F_Text_ArniePostBattle': "The statues work the doors. Press one and every open door shuts, and every shut one opens.",
        'PokemonMansion_1F_Text_ChristenedDiscoveredMonMew': raw("STATION LOG. Typed.", "Generator failed again at 0200.\nHolding tanks held on reserve.", "All stored states intact by the\nmorning count.", "Ordered more carbon paper."),
    },
    M % 'PokemonMansion_3F_Frlg': {
        'PokemonMansion_1F_Text_SimonIntro': "Three floors up and not one thing worth carrying!",
        'PokemonMansion_1F_Text_SimonDefeat': "Ayah! Not my day!",
        'PokemonMansion_1F_Text_SimonPostBattle': "My partner went down to the basement. He said it was warm down there. Too warm.",
        'PokemonMansion_1F_Text_BraydonIntro': "My mentor worked on this floor. Don't touch anything.",
        'PokemonMansion_1F_Text_BraydonDefeat': "Whew. Overwhelming.",
        'PokemonMansion_1F_Text_BraydonPostBattle': "If you're stuck, the floor has gone through by the far wall.|It's quicker than the stairs, and only slightly worse.",
    },
    M % 'PokemonMansion_B1F_Frlg': {
        'PokemonMansion_B1F_Text_LewisIntro': "Uh-oh. This isn't the way out.",
        'PokemonMansion_B1F_Text_LewisDefeat': "Awooh! I give!",
        'PokemonMansion_B1F_Text_LewisPostBattle': "There's an old man sitting down the hall with something enormous beside him.|Neither of them even looked at me. I have never felt so ignored.",
        'PokemonMansion_B1F_Text_IvanIntro': "The basement holds a steady temperature. Ideal for paper. Mind the shelves!",
        'PokemonMansion_B1F_Text_IvanDefeat': "What was that for?",
        'PokemonMansion_B1F_Text_IvanPostBattle': "I come down to copy what's still legible.|Whoever typed these was careful, and a little afraid. You can tell by what they underlined.",
    },
    M % 'SeafoamIslands_B4F_Frlg': {
        'SeafoamIslands_B4F_Text_BouldersMightChangeWaterFlow': raw("Scratched into the rock:", "“Two stones in the upper channel\nand the water lets go.”"),
        'SeafoamIslands_B4F_Text_DangerFastCurrent': raw("A tin plate on a rope:", "“FAST WATER. It takes you where it\nis going, not where you are.”"),
    },
    M % 'MossdeepCity': {
        'MossdeepCity_Text_WailmerWatching': "You can see WAILMER from the sea wall. I've counted eleven.|My sister says it's the same one eleven times.",
        'MossdeepCity_Text_LifeNeedsSeaToLive': "Tide comes in, tide goes out. I have watched it do that for seventy years, and it has never once asked my opinion.|The mainland looks closer than it did when I was young. My eyes are worse, so it isn't that.",
        'MossdeepCity_Text_NiceIfWorldCoveredByFlowers': "Everything grows here. Salt, wind, rocket smoke, and the flowers come up anyway.|I'd like the whole coast to look like this. I'd settle for my windowsill.",
        'MossdeepCity_Text_SurfExhilarating': "I came over on the six o'clock ferry. Six and six, they said. With the wind up it was six and whenever.|You crossed on a POKéMON? Then you kept better time than the boat.",
        'MossdeepCity_Text_SpecialSpaceCenterRock': "This white rock belongs to the SPACE CENTER. They set it here to wish their rockets safely up.|You write the wish on a tag and tie it on. I do one every launch window.|It hasn't failed yet, and neither have they.",
        'MossdeepCity_Text_ItsAWhiteRock': raw("A white rock, hung with paper tags.", "Most say SAFE FLIGHT.\nOne says PLEASE, NOT A MONDAY."),
        'MossdeepCity_Text_WantKingsRockStevenGaveMe': "STEVEN from next door gave me this. He said it was a good one. It's a rock.|I think it's called a KING'S ROCK. I can't use it for anything. Do you want it?",
        'MossdeepCity_Text_YouCanKeepIt': "Really? Okay. I'll tell him I traded it. He likes it when things get traded.|Just don't tell him what for.",
        'MossdeepCity_Text_StevensHouseOverThere': "STEVEN's house is the one right there. He's never in. He's always somewhere with rocks.",
        'MossdeepCity_Text_WhatToDoWithWeirdRock': "See, you don't want it either. It's just a rock with a name.",
        'MossdeepCity_Text_SootopolisNewGymLeader': "The waves on your feet. Best thing there is after training.|TATE and LIZA fight as a pair, so I train as a pair. My partner is the tide. It hasn't lost yet.",
        'MossdeepCity_Text_ScottSomethingWrongWithTown': "SCOTT: Hello there. Don't mind me. I travel around looking for TRAINERS with a future.|I came to see the pair at the GYM. Two LEADERS, one battle. You don't find that on every island.|You've got the look, too. I'll remember the face. That's my whole job.",
    },
    M % 'MossdeepCity_PokemonCenter_1F': {
        'MossdeepCity_PokemonCenter_1F_Text_GymLeaderDuoFormidable': "The LEADERS here are twins. They battle as one, two POKéMON at a time.|Bring two that get along. Mine didn't, and it showed.",
        'MossdeepCity_PokemonCenter_1F_Text_AbilitiesMightChangeMoves': "The nurse says the machine hums a different note on launch days.|I can't hear it. I think she just likes launch days.",
    },
    M % 'MossdeepCity_Mart': {
        'MossdeepCity_Mart_Text_ReviveIsFantastic': "Everything on this island comes over by boat, so everything costs a boat's worth more.|I buy the REVIVES anyway.",
        'MossdeepCity_Mart_Text_MaxRepelLastsLongest': "MAX REPEL lasts the longest. I timed it on the path round the SPACE CENTER.|Twice, to be sure.",
        'MossdeepCity_Mart_Text_NetAndDiveBallsRare': "NET BALLS and DIVE BALLS are made here on MOSSDEEP.|The NET ones are for anything that swims or crawls. I keep a few for whatever comes up with the catch.",
    },
    M % 'MossdeepCity_House1': {
        'MossdeepCity_House1_Text_HmmYourPokemon': raw("Hold still. Your {STR_VAR_1}…"),
        'MossdeepCity_House1_Text_ItLikesXPokeblocks': raw("It likes {STR_VAR_1}S.\nI'd bet the boat on it.", "I cook for the launch crews.\nI know a picky eater on sight."),
        'MossdeepCity_House1_Text_DoesntLikeOrDislikePokeblocks': "It would eat anything you put in front of it. Easy to feed. I like that in a POKéMON.",
        'MossdeepCity_House1_Text_HusbandCanTellPokeblockMonLikes': "My husband runs the SPACE CENTER canteen. He reads appetites the way the old sailors read weather.",
    },
    M % 'MossdeepCity_House2': {
        'MossdeepCity_House2_Text_SisterMailsBoyfriendInFortree': "My sister writes to a boy in FORTREE. The WINGULL does the flying and I do the worrying.",
        'MossdeepCity_House2_Text_PokemonCarriesMailBackAndForth': "My WINGULL takes MAIL to FORTREE and back. It knows the way better than the ferry does.|My friend writes about trees. I write about the sea. We both think the other one has it better.",
    },
    M % 'MossdeepCity_House3': {
        'MossdeepCity_House3_Text_YouWantSuperRod': "You crossed the sound with a starter rod? I have a SUPER ROD here I've outgrown.|It drops past the shelf to where the big ones sit. Do you want it?",
        'MossdeepCity_House3_Text_SuperRodIsSuper': "Good. Don't let the tide take it.",
        'MossdeepCity_House3_Text_TryDroppingRodInWater': "Try it off the east pier at the turn of the tide. That's when the deep water comes up to look.",
        'MossdeepCity_House3_Text_DontYouLikeToFish': "No? Suit yourself. It'll keep.",
        'MossdeepCity_House3_Text_GoAfterSeafloorPokemon': "Caught anything off the shelf yet? Don't tell me the size. Everybody on this island lies about the size.",
    },
    M % 'MossdeepCity_House4': {
        'MossdeepCity_House4_Text_BrotherLikesToFindBases': "My little brother finds hideouts in the bushes. He never says whose they are.",
        'MossdeepCity_House4_Text_BrotherLikesToVisitBasesAndBattle': "My brother says the hideouts all have people in them now, and every one of them wants a battle.|He comes home sunburnt and happy.",
        'MossdeepCity_House4_Text_YouMadeSecretBaseNearX': raw("Was that your hideout near\n{STR_VAR_1}? I sat in it.", "I didn't touch anything.\nMuch."),
        'MossdeepCity_House4_Text_MakeSecretBase': "You should make a hideout somewhere. A tree, a cave, a bush. I'll find it. I always do.",
    },
    M % 'MossdeepCity_StevensHouse': {
        'MossdeepCity_StevensHouse_Text_UnderwateCavernBetweenMossdeepSootopolis': "STEVEN: The neighbours call this the stone house. They aren't wrong.|I'm not home much. When I am, I sort rocks and listen for the launches.",
        'MossdeepCity_StevensHouse_Text_CollectionOfRareRocks': raw("Stones, labelled in a careful hand.\nNone of the labels say where from."),
        'MossdeepCity_StevensHouse_Text_LetterFromSteven': "It's a letter.|… … … … … …|To {PLAYER}. I've gone walking for a while. The house will keep.|The POKé BALL on the desk holds a BELDUM. It has been patient with me. I think it would do better on the road.|Take it, if you would. STEVEN",
    },
    M % 'MossdeepCity_Gym': {
        'MossdeepCity_Gym_Text_GymGuideAdvice': "Yo, {PLAYER}. This one is a double battle. Two LEADERS, and two of yours out at once.|Don't plan around a type. TATE and LIZA field whatever covers the other one's back, right at the top of this island's weight class.|The floor is part of it. Step on a switch and the arrows turn. Think of the walk as round one.",
        'MossdeepCity_Gym_Text_GymGuidePostVictory': "That's the twins beaten at their own game. They'll be pleased. They like company that can keep up.|If you haven't been yet, the SPACE CENTER wants a word with anyone who has walked the whole road.",
    },
}

# (file, start marker, end marker, [(old, new)...]): edits inside one script block.
BLOCKS = [
    (STORY, 'Pox_Blaine::', 'Pox_Text_Blaine::', [
        ('Pox_NotReady', P + 'BlaineNotReady'),
        ('goto_if_set FLAG_BADGE05_GET, Pox_MansionKey\n', f'goto_if_set FLAG_BADGE05_GET, {P}BlaineKey\n'),
        ('msgbox Pox_Text_Badge,', f'msgbox {P}Text_VolcanoBadge,'),
    ]),
    (STORY, 'Pox_TateLiza::', 'Pox_Text_TateLiza::', [
        ('Pox_NotReady', P + 'TwinsNotReady'),
        ('Pox_Done', P + 'TwinsDone'),
        ('goto_if_lt VAR_RESULT, 2, Pox_TwoMons', f'goto_if_lt VAR_RESULT, 2, {P}TwinsTwoMons'),
        ('Pox_Text_TwoMons', P + 'Text_TwinsTwoMons'),
        ('msgbox Pox_Text_Badge,', f'msgbox {P}Text_MindBadge,'),
    ]),
    (STORY, 'Pox_Archive1::', 'Pox_Text_Archive1::', [('Pox_NotReady', P + 'Archive1Sealed'), ('Pox_Done', P + 'Archive1Again')]),
    (STORY, 'Pox_Archive2::', 'Pox_Text_Archive2::', [('Pox_NotReady', P + 'Archive2Sealed'), ('Pox_Done', P + 'Archive2Again')]),
    (STORY, 'Pox_Archive3::', 'Pox_Text_Archive3::', [('Pox_NotReady', P + 'Archive3Sealed'), ('Pox_Done', P + 'Archive3Again')]),
    (STORY, 'Pox_Space::', 'Pox_Text_Space::', [('Pox_NotReady', P + 'SpaceBusy')]),
    ('data/scripts/plastic_ox_weather_institute.inc', 'Pox_SpaceReport::', 'Pox_SC_Report_After::', [('Pox_NotReady', P + 'ReportBusy')]),
    (REGION, 'PoxRegion_cinnabar_sea_a_Closed::', 'PoxRegion_cinnabar_sea_a_Sign::', [('PoxRegion_ClosedText', P + 'Text_SeaClosed')]),
    (REGION, 'PoxRegion_sea_mossdeep_b_Closed::', 'PoxRegion_mossdeep_route19_a::', [('PoxRegion_ClosedText', P + 'Text_CrossingClosed')]),
    # The Hoenn gym flags are never set here; the badge is the record.
    (M % 'MossdeepCity_Gym', 'MossdeepCity_Gym_EventScript_GymGuide::', 'MossdeepCity_Gym_EventScript_GymGuidePostVictory::',
     [('FLAG_DEFEATED_MOSSDEEP_GYM', 'FLAG_BADGE06_GET')]),
    (M % 'MossdeepCity_Gym', 'MossdeepCity_Gym_EventScript_LeftGymStatue::', 'MossdeepCity_Gym_EventScript_GymStatueCertified::',
     [('FLAG_BADGE07_GET', 'FLAG_BADGE06_GET')]),
    (M % 'CinnabarIsland_Gym_Frlg', 'CinnabarIsland_Gym_EventScript_GymStatue::', 'CinnabarIsland_Gym_EventScript_GymStatuePostVictory::',
     [('FLAG_BADGE07_GET', 'FLAG_BADGE05_GET')]),
]


# Gym guides that check the party against the gym's ADV tier rules special
# (src/field_specials.c CheckADVTierGymRules: species tier, Ubers, OHKO and
# evasion clauses). It returns 1 for a banned move, 2 for an item, 3 for a
# species over the tier, 4 for a duplicate species (Species Clause), 5 for a
# banned ability, 6 for a banned Baton Pass pairing, 7 for a second boost
# passer. A violation is reported, not enforced.
GUIDES = [
    ('CinnabarGymGuide', 'FLAG_BADGE05_GET', 'CinnabarIsland_Gym_EventScript_GymGuyPostVictory',
     'CinnabarIsland_Gym_Text_GymGuyAdvice', 'CheckCinnabarGymUURules', 'Cinnabar'),
    ('MossdeepGymGuide', 'FLAG_BADGE06_GET', 'MossdeepCity_Gym_EventScript_GymGuidePostVictory',
     'MossdeepCity_Gym_Text_GymGuideAdvice', 'CheckMossdeepGymUUBLRules', 'Twins'),
]


def guide(label, badge, after, advice, special, rules):
    return f'''
{P}{label}::
	lock
	faceplayer
	goto_if_set {badge}, {after}
	msgbox {advice}, MSGBOX_DEFAULT
	specialvar VAR_RESULT, {special}
	goto_if_eq VAR_RESULT, 1, {P}{label}_Move
	goto_if_eq VAR_RESULT, 2, {P}{label}_Item
	goto_if_eq VAR_RESULT, 3, {P}{label}_Species
	goto_if_eq VAR_RESULT, 4, {P}{label}_Duplicate
	goto_if_eq VAR_RESULT, 5, {P}{label}_Ability
	goto_if_eq VAR_RESULT, 6, {P}{label}_BatonPass
	goto_if_eq VAR_RESULT, 7, {P}{label}_BoostPasser
	msgbox {P}Text_{rules}RuleClean, MSGBOX_DEFAULT
	release
	end
{P}{label}_Move::
	msgbox {P}Text_{rules}RuleMove, MSGBOX_DEFAULT
	release
	end
{P}{label}_Item::
	msgbox {P}Text_{rules}RuleItem, MSGBOX_DEFAULT
	release
	end
{P}{label}_Species::
	msgbox {P}Text_{rules}RuleSpecies, MSGBOX_DEFAULT
	release
	end
{P}{label}_Duplicate::
	msgbox {P}Text_{rules}RuleDuplicate, MSGBOX_DEFAULT
	release
	end
{P}{label}_Ability::
	msgbox {P}Text_{rules}RuleAbility, MSGBOX_DEFAULT
	release
	end
{P}{label}_BatonPass::
	msgbox {P}Text_{rules}RuleBatonPass, MSGBOX_DEFAULT
	release
	end
{P}{label}_BoostPasser::
	msgbox {P}Text_{rules}RuleBoostPasser, MSGBOX_DEFAULT
	release
	end
'''


def scripts():
    out = ['@ Generated by plastic_ox/alpha/south_isles.py\n']
    texts = []
    for label, body in NPCS.items():
        if label in REFUSALS:
            # Reached from a story script that already holds the lock.
            out.append(f'{P}{label}::\n\tmsgbox {P}Text_{label}, MSGBOX_DEFAULT\n\treleaseall\n\tend\n')
            texts.append(f'{P}Text_{label}::\n' + string(body))
        elif label.endswith('Sign'):
            out.append(f'{P}{label}::\n\tmsgbox {P}Text_{label}, MSGBOX_SIGN\n\tend\n')
            texts.append(f'{P}Text_{label}::\n' + string(body))
        elif isinstance(body, list):
            s = f'{P}{label}::\n\tlock\n\tfaceplayer\n'
            for n in range(len(body) - 1, 0, -1):
                s += f'\tgoto_if_set {body[n][0]}, {P}{label}_{n}\n'
            s += f'\tmsgbox {P}Text_{label}, MSGBOX_DEFAULT\n\trelease\n\tend\n'
            texts.append(f'{P}Text_{label}::\n' + string(body[0]))
            for n in range(1, len(body)):
                s += f'{P}{label}_{n}::\n\tmsgbox {P}Text_{label}_{n}, MSGBOX_DEFAULT\n\trelease\n\tend\n'
                texts.append(f'{P}Text_{label}_{n}::\n' + string(body[n][1]))
            out.append(s)
        else:
            out.append(f'{P}{label}::\n\tmsgbox {P}Text_{label}, MSGBOX_NPC\n\tend\n')
            texts.append(f'{P}Text_{label}::\n' + string(body))
    for label, body in TEXTS.items():
        texts.append(f'{P}Text_{label}::\n' + string(body))
    out.append(f'''@ BLAINE after the badge: the key speech until the Mansion is read, then
@ a last word. Pox_MansionKey still re-grants a missing key or machine.
{P}BlaineKey::
	goto_if_unset {MANSION}, Pox_MansionKey
	msgbox {P}Text_BlaineAfter, MSGBOX_DEFAULT
	releaseall
	end

@ A read file can be read again; the shelves are documents, not one-shot beats.
{P}Archive1Again::
	msgbox Pox_Text_Archive1, MSGBOX_DEFAULT
	releaseall
	end
{P}Archive2Again::
	msgbox Pox_Text_Archive2, MSGBOX_DEFAULT
	releaseall
	end
{P}Archive3Again::
	msgbox Pox_Text_Archive3, MSGBOX_DEFAULT
	releaseall
	end

@ The ENTEI sage keeps his guest until the whole archive is read.
{P}EnteiSage::
	goto_if_set {MANSION}, PoxCinnabar_EnteiSage
	lock
	msgbox {P}Text_EnteiWaits, MSGBOX_DEFAULT
	release
	end
''' + ''.join(guide(*g) for g in GUIDES))
    return '\n'.join(out) + '\n' + '\n'.join(texts)


def set_text(src, label, body, path):
    pat = re.compile(r'^(' + re.escape(label) + r'::?[ \t]*\n)(?:[ \t]*\.string[^\n]*\n)+', re.M)
    if not pat.search(src):
        raise SystemExit(f'south_isles: no text label {label} in {path}')
    return pat.sub(lambda m: m[1] + string(body), src, count=1)


def patch_block(src, start, end, subs, path):
    if start not in src or end not in src[src.index(start):]:
        raise SystemExit(f'south_isles: no block {start}..{end} in {path}')
    i = src.index(start)
    j = src.index(end, i + len(start))
    block = src[i:j]
    for old, new in subs:
        if new in block:
            continue
        if old not in block:
            raise SystemExit(f'south_isles: {old!r} not found in {start} ({path})')
        block = block.replace(old, new)
    return src[:i] + block + src[j:]


def npc(gfx, x, y, script, elevation=3, movement='MOVEMENT_TYPE_FACE_DOWN'):
    return dict(graphics_id=gfx, x=x, y=y, elevation=elevation, movement_type=movement,
                movement_range_x=0, movement_range_y=0, trainer_type='TRAINER_TYPE_NONE',
                trainer_sight_or_berry_tree_id='0', script=P + script, flag='0')


# New people, by map. Coordinates were checked against the layout collision
# and elevation bits (Mossdeep's Space Center terrace is elevation 9).
ADDED = {
    'CinnabarIsland_Frlg': [
        npc('OBJ_EVENT_GFX_SAILOR', 22, 11, 'DockHand', movement='MOVEMENT_TYPE_FACE_UP'),
        npc('OBJ_EVENT_GFX_WOMAN_5', 17, 5, 'Greenhouse'),
        npc('OBJ_EVENT_GFX_SCIENTIST', 6, 10, 'LabTech'),
    ],
    'SeafoamIslands_1F_Frlg': [
        npc('OBJ_EVENT_GFX_HIKER', 4, 18, 'IceCutter', movement='MOVEMENT_TYPE_FACE_RIGHT'),
        npc('OBJ_EVENT_GFX_SWIMMER_M', 34, 18, 'Swimmer', movement='MOVEMENT_TYPE_FACE_LEFT'),
    ],
    'PlasticOx_Route20West': [
        npc('OBJ_EVENT_GFX_FISHERMAN', 58, 11, 'Angler'),
    ],
    'MossdeepCity': [
        npc('OBJ_EVENT_GFX_SAILOR', 4, 21, 'DockClerk', movement='MOVEMENT_TYPE_FACE_LEFT'),
        # Reading the Space Center's sign at (66,16), beside the door.
        npc('OBJ_EVENT_GFX_SCHOOL_KID_M', 65, 16, 'SchoolKid', elevation=9, movement='MOVEMENT_TYPE_FACE_RIGHT'),
    ],
}
# Existing objects that take a new script: map -> {old script: new script}.
REPOINT = {
    'CinnabarIsland_Frlg': {'PoxCinnabar_MansionGuide': 'MansionGuide', 'Pox_MansionGuide': 'MansionGuide',
                            'PoxCinnabar_GymGuide': 'GymRegular', 'Pox_BlaineGuide': 'GymRegular'},
    'MossdeepCity': {'Pox_SaffronRoad': 'SaffronSailor', 'MossdeepCity_EventScript_PokefanF': 'LaunchBoard'},
    'MossdeepCity_GameCorner_1F': {'MossdeepCity_GameCorner_1F_EventScript_InfoMan': 'ArcadeHost',
                                   'MossdeepCity_GameCorner_1F_EventScript_OldMan': 'ArcadeOldTimer'},
    'CinnabarIsland_Gym_Frlg': {'CinnabarIsland_Gym_EventScript_GymGuy': 'CinnabarGymGuide'},
    'MossdeepCity_Gym': {'MossdeepCity_Gym_EventScript_GymGuide': 'MossdeepGymGuide'},
    # The sage and ENTEI share one script; both now wait for FILE 3.
    'PokemonMansion_B1F_Frlg': {'PoxCinnabar_EnteiSage': 'EnteiSage'},
}
# Donor props and the two interchangeable direction-givers the new islanders replace.
REMOVED = {
    'CinnabarIsland_Frlg': lambda o: o.get('local_id') in ('LOCALID_CINNABAR_BILL', 'LOCALID_CINNABAR_SEAGALLOP')
    or o['script'] in ('Pox_MossdeepRoad', 'Pox_WhirlGuide'),
}


# Team Magma's Space Center occupation never happens here (Act V has no villain
# crisis); its people were only hidden. They and every script that becomes
# unreachable without them are removed from these maps.
MAGMA_GFX = ('OBJ_EVENT_GFX_MAGMA_MEMBER_M', 'OBJ_EVENT_GFX_MAGMA_MEMBER_F', 'OBJ_EVENT_GFX_MAXIE')
PRUNED = ('MossdeepCity', 'MossdeepCity_SpaceCenter_1F', 'MossdeepCity_SpaceCenter_2F')
_LABEL = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)::?[ \t]*(?:@.*)?$', re.M)
_WORD = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')
_STOPS = ('end', 'return', 'goto ', 'step_end', '.string', '.byte 0', '.2byte 0', 'releaseall', 'release')


def outside_refs(skip):
    """Every identifier used in the game's sources outside the files in skip."""
    words = set()
    for pattern in ('data/**/*.inc', 'data/**/*.s', 'data/maps/*/map.json', 'src/**/*.c', 'src/**/*.h'):
        for f in Path('.').glob(pattern):
            if str(f) not in skip:
                words.update(_WORD.findall(f.read_text(errors='replace')))
    return words


def prune(src, roots, path, gone_ids=()):
    """Drop label blocks of a map's scripts.inc that nothing can reach, and the
    lines of kept blocks that still move or remove a deleted person (the debug
    menu's Space Center multi battle reaches one such block)."""
    if gone_ids:
        dead = re.compile(r'^[^\n]*\b(?:' + '|'.join(map(re.escape, gone_ids)) + r')\b[^\n]*\n', re.M)
        src = dead.sub('', src)
    marks = [(m.start(), m[1]) for m in _LABEL.finditer(src)]
    if not marks:
        return src
    blocks = []
    for i, (pos, label) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(src)
        blocks.append((label, src[pos:end]))
    names = {label for label, _ in blocks}
    index = {label: i for i, (label, _) in enumerate(blocks)}
    keep = set()
    todo = [i for i, (label, _) in enumerate(blocks) if label in roots]
    while todo:
        i = todo.pop()
        if i in keep:
            continue
        keep.add(i)
        label, body = blocks[i]
        rest = body.split('\n', 1)[-1]
        todo += [index[w] for w in set(_WORD.findall(rest)) if w in index and w != label]
        code = [l.strip() for l in rest.split('\n') if l.strip() and not l.strip().startswith(('@', '//'))]
        if code and not code[-1].startswith(_STOPS) and i + 1 < len(blocks):
            todo.append(i + 1)  # falls through into the next label
    out = src[:marks[0][0]] + ''.join(body for i, (_, body) in enumerate(blocks) if i in keep)
    for gone in sorted(names - {blocks[i][0] for i in keep}):
        if re.search(r'\b' + gone + r'\b', out):
            raise SystemExit(f'south_isles: pruned {gone} is still used in {path}')
    return out.rstrip('\n') + '\n'


# Route 20 West: the open sea between CINNABAR and SEAFOAM, inside the cinnabar
# checkpoint (UU, level cap 42; counted by pox_progression as gPoxUURoute#).
# Fishing keeps the v5.5 rule: the Old Rod slot is MAGIKARP. Route 20 East stays
# barren on purpose (plasticox-route20east.md: Seafoam is the only sea content
# on that leg); install_sea_encounters drops any table there.
def _mons(rows):
    return [dict(min_level=lo, max_level=hi, species='SPECIES_' + s) for s, lo, hi in rows]


SEA = {
    'MAP_PLASTIC_OX_ROUTE20_WEST': ('gPoxUURoute20West', 4, [
        ('TENTACRUEL', 37, 40), ('PELIPPER', 37, 40), ('TENTACRUEL', 38, 41), ('LANTURN', 38, 41), ('PELIPPER', 39, 41)]),
}
BARREN = ('MAP_PLASTIC_OX_ROUTE20_EAST',)
SEA_FISHING = [('MAGIKARP', 36, 38), ('SEAKING', 36, 39), ('KINGLER', 37, 40), ('SEAKING', 37, 40), ('OCTILLERY', 38, 40),
               ('KINGLER', 38, 41), ('SEADRA', 38, 41), ('OCTILLERY', 38, 41), ('SEADRA', 39, 41), ('LANTURN', 39, 41)]


def install_sea_encounters(read, put):
    path = 'src/data/wild_encounters.json'
    data = json.loads(read(path))
    table = data['wild_encounter_groups'][0]['encounters']
    table[:] = [e for e in table if e.get('map') not in SEA and e.get('map') not in BARREN]
    for mapname, (label, rate, surf) in SEA.items():
        table.append(dict(map=mapname, base_label=label,
                          water_mons=dict(encounter_rate=rate, mons=_mons(surf)),
                          fishing_mons=dict(encounter_rate=20, mons=_mons(SEA_FISHING))))
    put(path, json.dumps(data, indent=2) + '\n')


def install(read, put):
    def load(name):
        return json.loads(read(f'data/maps/{name}/map.json'))

    def save(name, data):
        put(f'data/maps/{name}/map.json', json.dumps(data, indent=2) + '\n')

    for name in sorted(set(ADDED) | set(REPOINT) | set(REMOVED)):
        d = load(name)
        kept = {P + new for new in REPOINT.get(name, {}).values()}
        keep = []
        for o in d['object_events']:
            # Everything this module adds is re-added below, so a person who is
            # moved or dropped in a later edit does not linger at the old tile.
            if (o['script'].startswith(P) and o['script'] not in kept) or REMOVED.get(name, lambda o: False)(o):
                continue
            if o['script'] in REPOINT.get(name, {}):
                o['script'] = P + REPOINT[name][o['script']]
            keep.append(o)
        d['object_events'] = keep + [dict(o) for o in ADDED.get(name, [])]
        save(name, d)

    # The landing's signpost is already drawn into the Route 20 West layout at
    # (64,8); it only lacked words.
    d = load('PlasticOx_Route20West')
    d['bg_events'] = [b for b in d.get('bg_events', []) if b.get('script') != P + 'CaveSign']
    d['bg_events'].append(dict(type='sign', x=64, y=8, elevation=0,
                               player_facing_dir='BG_EVENT_PLAYER_FACING_ANY', script=P + 'CaveSign'))
    save('PlasticOx_Route20West', d)

    # Cinnabar Pokemon Center: FRLG's One Island BILL and the two journal props
    # hang on FRLG-only flags (0 here), so they were always on screen and BILL's
    # script still offered the Sevii ferry.
    d = load('CinnabarIsland_PokemonCenter_1F_Frlg')
    for o in d['object_events']:
        if o['script'] in ('CinnabarIsland_PokemonCenter_1F_EventScript_Bill',
                           'CinnabarIsland_PokemonCenter_1F_EventScript_PokemonJournalMrFuji'):
            o['flag'] = UNUSED
    save('CinnabarIsland_PokemonCenter_1F_Frlg', d)

    # CinnabarIsland_hns is a retired second copy of the town (no warps in or
    # out). Its leftover guides alias the live islanders' scripts; mark them as
    # the unused actors they are.
    d = load('CinnabarIsland_hns')
    for o in d['object_events']:
        o['flag'] = UNUSED
    save('CinnabarIsland_hns', d)

    # Space Center 1F: the child who wants to ride a rocket stood on the old
    # (invisible) Magma-note object, which sits on the plan table. Let people
    # see who is talking, on the floor beside it.
    d = load('MossdeepCity_SpaceCenter_1F')
    for o in d['object_events']:
        if o['script'] == 'Pox_Facility_MossdeepCity_SpaceCenter_1F_9':
            o.update(x=1, y=6, elevation=3, movement_type='MOVEMENT_TYPE_LOOK_AROUND', flag='0')
    save('MossdeepCity_SpaceCenter_1F', d)

    # Magma people out, then everything in these maps' scripts nothing reaches.
    gone_ids = set()
    for name in PRUNED:
        d = load(name)
        gone_ids |= {o['local_id'] for o in d['object_events'] if o['graphics_id'] in MAGMA_GFX and o.get('local_id')}
        d['object_events'] = [o for o in d['object_events'] if o['graphics_id'] not in MAGMA_GFX]
        save(name, d)
    # Local ids are per map, but these names are unique to the Magma people.
    gone_ids |= {'LOCALID_MOSSDEEP_MAXIE', 'LOCALID_SPACE_CENTER_MAXIE', 'LOCALID_SPACE_CENTER_TABITHA',
                 'LOCALID_SPACE_CENTER_1F_STAIR_GRUNT'} | {f'LOCALID_MOSSDEEP_GRUNT_{n}' for n in range(1, 5)} \
        | {f'LOCALID_SPACE_CENTER_GRUNT_{n}' for n in range(1, 8)}
    paths = [M % name for name in PRUNED]
    refs = outside_refs(set(paths) | {f'data/maps/{name}/map.json' for name in PRUNED})
    for name, path in zip(PRUNED, paths):
        words = set(_WORD.findall(read(f'data/maps/{name}/map.json')))
        put(path, prune(read(path), refs | words | {name + '_MapScripts'}, path, sorted(gone_ids)))
    install_sea_encounters(read, put)

    for path, labels in REWRITES.items():
        src = read(path)
        for label, body in labels.items():
            src = set_text(src, label, body, path)
        put(path, src)
    for path, start, end, subs in BLOCKS:
        put(path, patch_block(read(path), start, end, subs, path))

    put('data/scripts/plastic_ox_south_isles.inc', scripts())
    path = 'data/event_scripts.s'
    s = read(path)
    line = '\t.include "data/scripts/plastic_ox_south_isles.inc"\n'
    if line not in s:
        s += '\n' + line
    put(path, s)


if __name__ == '__main__':
    install(lambda p: Path(p).read_text(), lambda p, s: Path(p).write_text(s))
