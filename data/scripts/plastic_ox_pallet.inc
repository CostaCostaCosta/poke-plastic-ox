@ Pallet opening for the Plastic Ox story build.

Pox_LabEntrance::
    setvar VAR_TEMP_1, 1
    goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End
    goto_if_set FLAG_POX_LAB_INTRO, Pox_End
    lockall
    call Pox_LabApproach
    call Pox_LabIntroduction
    releaseall
    end

@ Center the player in the entrance aisle, then walk up to Oak.
Pox_LabApproach::
    getplayerxy VAR_0x8004, VAR_0x8005
    goto_if_eq VAR_0x8004, 6, Pox_LabApproachNorth
    goto_if_lt VAR_0x8004, 6, Pox_LabApproachRight
    applymovement LOCALID_PLAYER, Pox_StepLeft
    waitmovement 0
    goto Pox_LabApproach
Pox_LabApproachRight::
    applymovement LOCALID_PLAYER, Pox_StepRight
    waitmovement 0
    goto Pox_LabApproach
Pox_LabApproachNorth::
    goto_if_le VAR_0x8005, 6, Pox_LabApproachDone
    applymovement LOCALID_PLAYER, Pox_StepUp
    waitmovement 0
    goto Pox_LabApproach
Pox_LabApproachDone::
    @ Story Oak, Elm, and Birch are objects 11, 12, and 13.
    applymovement 11, Common_Movement_FacePlayer
    applymovement 12, Common_Movement_FacePlayer
    applymovement 13, Common_Movement_FacePlayer
    waitmovement 0
    applymovement LOCALID_PLAYER, Common_Movement_FaceUp
    waitmovement 0
    return
Pox_StepLeft:
    walk_left
    step_end
Pox_StepRight:
    walk_right
    step_end
Pox_StepUp:
    walk_up
    step_end

Pox_LabIntroduction::
    goto_if_set FLAG_POX_LAB_INTRO, Pox_LabIntroductionDone
    msgbox Pox_Text_OakIntro, MSGBOX_DEFAULT
    msgbox Pox_Text_ElmIntro, MSGBOX_DEFAULT
    msgbox Pox_Text_BirchIntro, MSGBOX_DEFAULT
    msgbox Pox_Text_ChoosePartner, MSGBOX_DEFAULT
    setflag FLAG_POX_LAB_INTRO
Pox_LabIntroductionDone::
    return

Pox_Treecko::
    goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End
    lockall
    goto_if_set FLAG_POX_STORY_STARTER, Pox_StarterAlreadyChosen
    call Pox_LabIntroduction
    showmonpic SPECIES_TREECKO, 10, 3
    playmoncry SPECIES_TREECKO, CRY_MODE_NORMAL
    waitmoncry
    msgbox Pox_Text_Treecko, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, Pox_StarterDeclined
    hidemonpic
    givemon SPECIES_TREECKO, 5
    goto_if_eq VAR_RESULT, MON_CANT_GIVE, Pox_NoRoom
    bufferspeciesname STR_VAR_1, SPECIES_TREECKO
    goto Pox_StarterReceived

Pox_Text_Treecko::
	.string "BIRCH: TREECKO is a nimble\nGRASS-type from HOENN. It can\pclimb even the tallest trees!\pWill you choose TREECKO as\nyour first partner?$"

Pox_Squirtle::
    goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End
    lockall
    goto_if_set FLAG_POX_STORY_STARTER, Pox_StarterAlreadyChosen
    call Pox_LabIntroduction
    showmonpic SPECIES_SQUIRTLE, 10, 3
    playmoncry SPECIES_SQUIRTLE, CRY_MODE_NORMAL
    waitmoncry
    msgbox Pox_Text_Squirtle, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, Pox_StarterDeclined
    hidemonpic
    givemon SPECIES_SQUIRTLE, 5
    goto_if_eq VAR_RESULT, MON_CANT_GIVE, Pox_NoRoom
    bufferspeciesname STR_VAR_1, SPECIES_SQUIRTLE
    goto Pox_StarterReceived

Pox_Text_Squirtle::
	.string "OAK: SQUIRTLE is a WATER-type\nfrom KANTO. Its sturdy shell\pkeeps it safe as it learns.\pWill you choose SQUIRTLE as\nyour first partner?$"

Pox_Cyndaquil::
    goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End
    lockall
    goto_if_set FLAG_POX_STORY_STARTER, Pox_StarterAlreadyChosen
    call Pox_LabIntroduction
    showmonpic SPECIES_CYNDAQUIL, 10, 3
    playmoncry SPECIES_CYNDAQUIL, CRY_MODE_NORMAL
    waitmoncry
    msgbox Pox_Text_Cyndaquil, MSGBOX_YESNO
    goto_if_eq VAR_RESULT, NO, Pox_StarterDeclined
    hidemonpic
    givemon SPECIES_CYNDAQUIL, 5
    goto_if_eq VAR_RESULT, MON_CANT_GIVE, Pox_NoRoom
    bufferspeciesname STR_VAR_1, SPECIES_CYNDAQUIL
    goto Pox_StarterReceived

Pox_Text_Cyndaquil::
	.string "ELM: CYNDAQUIL is a gentle\nFIRE-type from JOHTO. When\pstartled, its back bursts into\nflame!\pWill you choose CYNDAQUIL as\nyour first partner?$"

Pox_StarterDeclined::
    hidemonpic
    msgbox Pox_Text_TakeYourTime, MSGBOX_DEFAULT
    releaseall
    end

Pox_StarterAlreadyChosen::
    msgbox Pox_Text_AlreadyChosen, MSGBOX_DEFAULT
    releaseall
    end

Pox_StarterReceived::
    setflag FLAG_POX_STORY_STARTER
    setflag FLAG_SYS_POKEMON_GET
    setflag FLAG_SYS_POKEDEX_GET
    special EnableNationalPokedex
    setflag FLAG_POX_HIDE_R29_GUARD
    playfanfare MUS_OBTAIN_ITEM
    msgbox Pox_Text_ReceivedStarter, MSGBOX_DEFAULT
    waitfanfare
    playfanfare MUS_RG_OBTAIN_KEY_ITEM
    msgbox Pox_Text_Assignment, MSGBOX_DEFAULT
    waitfanfare
    call Pox_StarterSupplies
    msgbox Pox_Text_ElmAdvice, MSGBOX_DEFAULT
    call Pox_ElmExpAll
    call Pox_ElmLeave
    msgbox Pox_Text_BirchAdvice, MSGBOX_DEFAULT
    call Pox_ElmTMs
    call Pox_BirchLeave
    msgbox Pox_Text_OakAfter, MSGBOX_DEFAULT
    releaseall
    end

Pox_StarterSupplies::
    goto_if_set FLAG_POX_STARTER_SUPPLIES, Pox_StarterSuppliesDone
    additem ITEM_POKE_BALL, 5
    goto_if_eq VAR_RESULT, FALSE, Pox_StarterSuppliesFull
    setflag FLAG_POX_STARTER_SUPPLIES
    playfanfare MUS_OBTAIN_ITEM
    msgbox Pox_Text_Supplies, MSGBOX_DEFAULT
    waitfanfare
Pox_StarterSuppliesDone::
    return
Pox_StarterSuppliesFull::
    msgbox Pox_Text_SuppliesFull, MSGBOX_DEFAULT
    return

Pox_Oak::
    goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End
    lock
    faceplayer
    call Pox_LabIntroduction
    goto_if_set FLAG_POX_STORY_STARTER, Pox_OakAfter
    msgbox Pox_Text_OakBefore, MSGBOX_DEFAULT
    release
    end
Pox_OakAfter::
    call Pox_StarterSupplies
    msgbox Pox_Text_OakAfter, MSGBOX_DEFAULT
    release
    end

Pox_Elm::
    goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End
    lock
    faceplayer
    call Pox_LabIntroduction
    goto_if_set FLAG_POX_STORY_STARTER, Pox_ElmAfter
    msgbox Pox_Text_ElmBefore, MSGBOX_DEFAULT
    release
    end
Pox_ElmAfter::
    call Pox_ElmExpAll
    goto_if_set FLAG_POX_ELM_EXP_ALL, Pox_ElmDepartAfterTalk
    release
    end
Pox_ElmDepartAfterTalk::
    call Pox_ElmLeave
    release
    end

Pox_ElmExpAll::
    goto_if_set FLAG_POX_ELM_EXP_ALL, Pox_ElmExpAllDone
    additem ITEM_EXP_SHARE
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmExpAllFull
    setflag FLAG_POX_ELM_EXP_ALL
    setflag FLAG_POX_EXP_ALL
    playfanfare MUS_OBTAIN_ITEM
    msgbox Pox_Text_ElmExpAll, MSGBOX_DEFAULT
    waitfanfare
Pox_ElmExpAllDone::
    return
Pox_ElmExpAllFull::
    msgbox Pox_Text_ElmExpAllFull, MSGBOX_DEFAULT
    return

Pox_Text_ElmExpAll::
    .string "ELM: Take this EXP. SHARE. Every\nPOKéMON in your party will receive\pthe full Exp. from battle!$"

Pox_Text_ElmExpAllFull::
    .string "ELM: Make room in your KEY ITEMS\npocket, then speak to me again. I\pstill have your EXP. SHARE.$"

Pox_Birch::
    goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End
    lock
    faceplayer
    call Pox_LabIntroduction
    goto_if_set FLAG_POX_STORY_STARTER, Pox_BirchAfter
    msgbox Pox_Text_BirchBefore, MSGBOX_DEFAULT
    release
    end
Pox_BirchAfter::
    call Pox_ElmTMs
    goto_if_set FLAG_POX_ELM_TMS, Pox_BirchDepartAfterTalk
    release
    end
Pox_BirchDepartAfterTalk::
    call Pox_BirchLeave
    release
    end

Pox_Text_OakIntro::
	.string "OAK: Ah, {PLAYER}! Welcome!\nToday you get to choose your\pfirst POKéMON.\pMy colleagues have come a long\nway to meet you.\pThe geography of KANTO, JOHTO,\nand HOENN changed suddenly.\pRoads now lead to unfamiliar\nplaces.\pWe're still trying to\nunderstand it. Here in PALLET,\pthough, life goes on!$"

Pox_Text_ElmIntro::
	.string "ELM: Hello! I'm PROFESSOR ELM,\nfrom JOHTO.\pI study how POKéMON grow.\nThere's so much we can learn\pby caring for them every day.\pI've brought CYNDAQUIL. A\nlittle patience will help it\pfeel at home.$"

Pox_Text_BirchIntro::
	.string "BIRCH: And I'm PROFESSOR\nBIRCH, from HOENN! I study\pPOKéMON out in the field.\pThe habitats along these new\nroads have given me plenty to\pexplore.\pTREECKO came with me. It's\nalways ready for a walk!$"

Pox_Text_ChoosePartner::
	.string "OAK: I've brought SQUIRTLE\nfrom KANTO. That's one partner\pfrom each of our regions!\pThe three POKé BALLS are on\nthe table to the right.\pTake a look at each one.\nChoose the POKéMON you'd like\pto travel with.$"

Pox_Text_TakeYourTime::
	.string "OAK: No hurry! Get to know all\nthree before you decide.$"

Pox_Text_AlreadyChosen::
	.string "OAK: You've chosen your\npartner. The other two are safe\pin their POKé BALLS here.$"

Pox_Text_ReceivedStarter::
	.string "{PLAYER} received {STR_VAR_1}!$"

Pox_Text_Assignment::
	.string "OAK: And this is your POKéDEX!\nIt records the POKéMON you see\pand catch.\p{PLAYER} received the POKéDEX!\pIt can record species from all\nthree regions.\pWould you help us learn which\nPOKéMON live along the new\proads?\pMeet POKéMON, visit towns, and\nchallenge GYMS if you like.\pCome tell us what you find!$"

Pox_Text_ElmAdvice::
	.string "ELM: Watch how your partner\ngrows. Even a short journey\pcan teach you both a great\ndeal.\pI brought something that will\nhelp your whole team grow.$"

Pox_Text_BirchAdvice::
	.string "BIRCH: Wild POKéMON live in\ntall grass. Weaken one in\pbattle, then try a POKé BALL!\pTake these TMs and my MOVE\nCOMPENDIUM. They'll help you\pexperiment with new moves!$"

Pox_Text_Supplies::
	.string "OAK: Here are five POKé BALLS\nto get you started!\p{PLAYER} put the POKé BALLS in\nthe BAG.$"

Pox_Text_SuppliesFull::
	.string "OAK: Your POKé BALL pocket is\nfull. Make some space and\pspeak to me again. I'll keep\nfive balls for you.$"

Pox_Text_OakBefore::
	.string "OAK: TREECKO, SQUIRTLE, or\nCYNDAQUIL... Which will it be?\pExamine the POKé BALLS on the\ntable to the right.$"

Pox_Text_ElmBefore::
	.string "ELM: CYNDAQUIL is in the\nrightmost ball. It's shy, but\pvery affectionate once it\ntrusts you.$"

Pox_Text_BirchBefore::
	.string "BIRCH: TREECKO is in the\nleftmost ball. The middle one\pholds OAK's SQUIRTLE.\pChoose whichever makes you\ncurious!$"

Pox_Text_OakAfter::
	.string "OAK: Head north through ROUTE\n101 to OLDALE TOWN.\pThe road west of OLDALE leads\ntoward CHERRYGROVE.\pOur lab is always open. Enjoy\nyour journey, {PLAYER}!$"

Pox_Text_ElmAfter::
	.string "ELM: I should return to my own\nlab in JOHTO. Take good care of\pyour new partner!$"

Pox_Text_BirchAfter::
	.string "BIRCH: Time for me to get back\nto fieldwork in HOENN! Record\pevery unexpected habitat you\nfind.$"

Pox_ElmTMs::
    goto_if_set FLAG_POX_ELM_TMS, Pox_ElmTMsDone
    checkitem ITEM_MOVE_COMPENDIUM, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNextCompendium
    additem ITEM_MOVE_COMPENDIUM, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmCompendiumFull
Pox_ElmTMNextCompendium::
    checkitem ITEM_TM_FOCUS_PUNCH, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext0
    additem ITEM_TM_FOCUS_PUNCH, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext0::
    checkitem ITEM_TM_DRAGON_CLAW, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext1
    additem ITEM_TM_DRAGON_CLAW, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext1::
    checkitem ITEM_TM_WATER_PULSE, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext2
    additem ITEM_TM_WATER_PULSE, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext2::
    checkitem ITEM_TM_CALM_MIND, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext3
    additem ITEM_TM_CALM_MIND, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext3::
    checkitem ITEM_TM_ROAR, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext4
    additem ITEM_TM_ROAR, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext4::
    checkitem ITEM_TM_TOXIC, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext5
    additem ITEM_TM_TOXIC, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext5::
    checkitem ITEM_TM_HAIL, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext6
    additem ITEM_TM_HAIL, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext6::
    checkitem ITEM_TM_BULK_UP, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext7
    additem ITEM_TM_BULK_UP, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext7::
    checkitem ITEM_TM_BULLET_SEED, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext8
    additem ITEM_TM_BULLET_SEED, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext8::
    checkitem ITEM_TM_HIDDEN_POWER, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext9
    additem ITEM_TM_HIDDEN_POWER, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext9::
    checkitem ITEM_TM_SUNNY_DAY, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext10
    additem ITEM_TM_SUNNY_DAY, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext10::
    checkitem ITEM_TM_TAUNT, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext11
    additem ITEM_TM_TAUNT, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext11::
    checkitem ITEM_TM_ICE_BEAM, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext12
    additem ITEM_TM_ICE_BEAM, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext12::
    checkitem ITEM_TM_BLIZZARD, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext13
    additem ITEM_TM_BLIZZARD, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext13::
    checkitem ITEM_TM_HYPER_BEAM, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext14
    additem ITEM_TM_HYPER_BEAM, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext14::
    checkitem ITEM_TM_LIGHT_SCREEN, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext15
    additem ITEM_TM_LIGHT_SCREEN, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext15::
    checkitem ITEM_TM_PROTECT, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext16
    additem ITEM_TM_PROTECT, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext16::
    checkitem ITEM_TM_RAIN_DANCE, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext17
    additem ITEM_TM_RAIN_DANCE, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext17::
    checkitem ITEM_TM_GIGA_DRAIN, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext18
    additem ITEM_TM_GIGA_DRAIN, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext18::
    checkitem ITEM_TM_SAFEGUARD, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext19
    additem ITEM_TM_SAFEGUARD, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext19::
    checkitem ITEM_TM_FRUSTRATION, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext20
    additem ITEM_TM_FRUSTRATION, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext20::
    checkitem ITEM_TM_SOLAR_BEAM, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext21
    additem ITEM_TM_SOLAR_BEAM, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext21::
    checkitem ITEM_TM_IRON_TAIL, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext22
    additem ITEM_TM_IRON_TAIL, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext22::
    checkitem ITEM_TM_THUNDERBOLT, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext23
    additem ITEM_TM_THUNDERBOLT, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext23::
    checkitem ITEM_TM_THUNDER, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext24
    additem ITEM_TM_THUNDER, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext24::
    checkitem ITEM_TM_EARTHQUAKE, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext25
    additem ITEM_TM_EARTHQUAKE, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext25::
    checkitem ITEM_TM_RETURN, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext26
    additem ITEM_TM_RETURN, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext26::
    checkitem ITEM_TM_DIG, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext27
    additem ITEM_TM_DIG, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext27::
    checkitem ITEM_TM_PSYCHIC, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext28
    additem ITEM_TM_PSYCHIC, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext28::
    checkitem ITEM_TM_SHADOW_BALL, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext29
    additem ITEM_TM_SHADOW_BALL, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext29::
    checkitem ITEM_TM_BRICK_BREAK, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext30
    additem ITEM_TM_BRICK_BREAK, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext30::
    checkitem ITEM_TM_SUBSTITUTE, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext31
    additem ITEM_TM_SUBSTITUTE, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext31::
    checkitem ITEM_TM_REFLECT, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext32
    additem ITEM_TM_REFLECT, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext32::
    checkitem ITEM_TM_BODY_SLAM, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext33
    additem ITEM_TM_BODY_SLAM, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext33::
    checkitem ITEM_TM_FLAMETHROWER, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext34
    additem ITEM_TM_FLAMETHROWER, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext34::
    checkitem ITEM_TM_SLUDGE_BOMB, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext35
    additem ITEM_TM_SLUDGE_BOMB, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext35::
    checkitem ITEM_TM_SANDSTORM, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext36
    additem ITEM_TM_SANDSTORM, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext36::
    checkitem ITEM_TM_FIRE_BLAST, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext37
    additem ITEM_TM_FIRE_BLAST, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext37::
    checkitem ITEM_TM_ROCK_TOMB, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext38
    additem ITEM_TM_ROCK_TOMB, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext38::
    checkitem ITEM_TM_AERIAL_ACE, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext39
    additem ITEM_TM_AERIAL_ACE, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext39::
    checkitem ITEM_TM_TORMENT, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext40
    additem ITEM_TM_TORMENT, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext40::
    checkitem ITEM_TM_FACADE, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext41
    additem ITEM_TM_FACADE, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext41::
    checkitem ITEM_TM_SECRET_POWER, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext42
    additem ITEM_TM_SECRET_POWER, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext42::
    checkitem ITEM_TM_REST, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext43
    additem ITEM_TM_REST, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext43::
    checkitem ITEM_TM_ATTRACT, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext44
    additem ITEM_TM_ATTRACT, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext44::
    checkitem ITEM_TM_THIEF, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext45
    additem ITEM_TM_THIEF, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext45::
    checkitem ITEM_TM_EXPLOSION, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext46
    additem ITEM_TM_EXPLOSION, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext46::
    checkitem ITEM_TM_ROCK_SLIDE, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext47
    additem ITEM_TM_ROCK_SLIDE, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext47::
    checkitem ITEM_TM_SNATCH, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext48
    additem ITEM_TM_SNATCH, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext48::
    checkitem ITEM_TM_OVERHEAT, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmTMNext49
    additem ITEM_TM_OVERHEAT, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmTMNext49::
    setflag FLAG_POX_ELM_TMS
    playfanfare MUS_OBTAIN_ITEM
    msgbox Pox_Text_ElmTMs, MSGBOX_DEFAULT
    waitfanfare
Pox_ElmTMsDone::
    return
Pox_ElmTMsFull::
    msgbox Pox_Text_ElmTMsFull, MSGBOX_DEFAULT
    return
Pox_ElmCompendiumFull::
    msgbox Pox_Text_ElmCompendiumFull, MSGBOX_DEFAULT
    return
Pox_Text_ElmTMs::
    .string "BIRCH: Here is a full set of TMs!\nI've included a MOVE COMPENDIUM\pfor level, Egg, and tutor moves.\p{PLAYER} received every TM and the\nMOVE COMPENDIUM!$"
Pox_Text_ElmTMsFull::
    .string "BIRCH: Make room in your TM\npocket, then speak to me.\pI'll give you the rest!$"
Pox_Text_ElmCompendiumFull::
    .string "BIRCH: Make room in your KEY ITEMS\npocket, then speak to me again.$"

Pox_ElmLeave::
    goto_if_unset FLAG_POX_ELM_EXP_ALL, Pox_ElmLeaveDone
    msgbox Pox_Text_ElmAfter, MSGBOX_DEFAULT
    applymovement 12, Pox_ElmLeaveMovement
    waitmovement 0
    removeobject 12
Pox_ElmLeaveDone::
    return

Pox_BirchLeave::
    goto_if_unset FLAG_POX_ELM_TMS, Pox_BirchLeaveDone
    msgbox Pox_Text_BirchAfter, MSGBOX_DEFAULT
    applymovement 13, Pox_BirchLeaveMovement
    waitmovement 0
    removeobject 13
Pox_BirchLeaveDone::
    return

Pox_ElmLeaveMovement:
    walk_right
    walk_right
    walk_down
    walk_down
    walk_down
    walk_down
    walk_down
    walk_down
    walk_down
    step_end

Pox_BirchLeaveMovement:
    walk_left
    walk_left
    walk_left
    walk_left
    walk_down
    walk_down
    walk_down
    walk_down
    walk_down
    walk_down
    walk_down
    step_end
