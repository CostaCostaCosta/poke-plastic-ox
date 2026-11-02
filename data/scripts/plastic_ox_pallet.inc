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
    goto_if_le VAR_0x8005, 5, Pox_LabApproachDone
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

@ Gifts are explained face-to-face along the clear aisle below the professors.
Pox_ApproachOak::
    setvar VAR_0x8006, 6
    setvar VAR_0x8007, 11
    goto Pox_ApproachProfessor
Pox_ApproachElm::
    setvar VAR_0x8006, 5
    setvar VAR_0x8007, 12
    goto Pox_ApproachProfessor
Pox_ApproachBirch::
    setvar VAR_0x8006, 7
    setvar VAR_0x8007, 13
Pox_ApproachProfessor::
    closemessage
    getplayerxy VAR_0x8004, VAR_0x8005
    @ A player inspecting a ball from above must go around the table.
    goto_if_lt VAR_0x8005, 4, Pox_ApproachProfessorUpper
    goto_if_lt VAR_0x8005, 5, Pox_ApproachProfessorDown
    goto_if_gt VAR_0x8005, 5, Pox_ApproachProfessorUp
    goto_if_lt VAR_0x8004, VAR_0x8006, Pox_ApproachProfessorRight
    goto_if_gt VAR_0x8004, VAR_0x8006, Pox_ApproachProfessorLeft
    applymovement LOCALID_PLAYER, Common_Movement_FaceUp
    waitmovement 0
    applymovement VAR_0x8007, Common_Movement_FaceDown
    waitmovement 0
    return
Pox_ApproachProfessorUpper::
    goto_if_lt VAR_0x8004, 11, Pox_ApproachProfessorRight
    goto Pox_ApproachProfessorDown
Pox_ApproachProfessorDown::
    applymovement LOCALID_PLAYER, Pox_StepDown
    waitmovement 0
    goto Pox_ApproachProfessor
Pox_ApproachProfessorUp::
    applymovement LOCALID_PLAYER, Pox_StepUp
    waitmovement 0
    goto Pox_ApproachProfessor
Pox_ApproachProfessorRight::
    applymovement LOCALID_PLAYER, Pox_StepRight
    waitmovement 0
    goto Pox_ApproachProfessor
Pox_ApproachProfessorLeft::
    applymovement LOCALID_PLAYER, Pox_StepLeft
    waitmovement 0
    goto Pox_ApproachProfessor
Pox_StepDown:
    walk_down
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
    setflag FLAG_POX_HIDE_TREECKO_BALL
    removeobject 5
    bufferspeciesname STR_VAR_1, SPECIES_TREECKO
    goto Pox_StarterReceived

Pox_Text_Treecko::
	.string "BIRCH: TREECKO is a nimble\nGRASS-type. Choose TREECKO?$"

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
    setflag FLAG_POX_HIDE_SQUIRTLE_BALL
    removeobject 6
    bufferspeciesname STR_VAR_1, SPECIES_SQUIRTLE
    goto Pox_StarterReceived

Pox_Text_Squirtle::
	.string "OAK: SQUIRTLE is a sturdy\nWATER-type. Choose SQUIRTLE?$"

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
    setflag FLAG_POX_HIDE_CYNDAQUIL_BALL
    removeobject 7
    bufferspeciesname STR_VAR_1, SPECIES_CYNDAQUIL
    goto Pox_StarterReceived

Pox_Text_Cyndaquil::
	.string "ELM: CYNDAQUIL is a shy\nFIRE-type. Choose CYNDAQUIL?$"

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
    call Pox_ApproachOak
    playfanfare MUS_RG_OBTAIN_KEY_ITEM
    msgbox Pox_Text_Assignment, MSGBOX_DEFAULT
    waitfanfare
    call Pox_StarterSupplies
    call Pox_ApproachElm
    call Pox_ElmExpAll
    call Pox_ElmLeave
    call Pox_ApproachBirch
    msgbox Pox_Text_BirchAdvice, MSGBOX_DEFAULT
    call Pox_ElmTMs
    call Pox_BirchLeave
    call Pox_ApproachOak
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
    call Pox_ApproachElm
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
	.string "ELM: This EXP. SHARE gives your\nwhole party full Exp. from battles!$"

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
    call Pox_ApproachBirch
    call Pox_ElmTMs
    goto_if_set FLAG_POX_ELM_TMS, Pox_BirchDepartAfterTalk
    release
    end
Pox_BirchDepartAfterTalk::
    call Pox_BirchLeave
    release
    end

Pox_Text_OakIntro::
	.string "OAK: Welcome, {PLAYER}!\nYour first partner is waiting.$"

Pox_Text_ElmIntro::
	.string "ELM: I'm PROFESSOR ELM.\nI brought CYNDAQUIL from JOHTO!$"

Pox_Text_BirchIntro::
	.string "BIRCH: Good to see you again!\nTREECKO came with me from HOENN.$"

Pox_Text_ChoosePartner::
	.string "OAK: And SQUIRTLE is from KANTO.\nCheck the three balls on the right.\pTake your time choosing a partner!$"

Pox_Text_TakeYourTime::
	.string "OAK: No hurry! Get to know all\nthree before you decide.$"

Pox_Text_AlreadyChosen::
	.string "OAK: I'll look after the other two.\nTake good care of your partner!$"

Pox_Text_ReceivedStarter::
	.string "{PLAYER} received {STR_VAR_1}!$"

Pox_Text_Assignment::
	.string "OAK: Take this POKéDEX. It records\nthe POKéMON you see and catch.\pCome tell us what you discover!$"

Pox_Text_ElmAdvice::
	.string "ELM: Watch how your partner\ngrows. Even a short journey\pcan teach you both a great\ndeal.\pI brought something that will\nhelp your whole team grow.$"

Pox_Text_BirchAdvice::
	.string "BIRCH: Weaken wild POKéMON, then\nthrow a POKé BALL to catch them!$"

Pox_Text_Supplies::
	.string "{PLAYER} received five POKé BALLS!$"

Pox_Text_SuppliesFull::
	.string "OAK: Your POKé BALL pocket is\nfull. Make some space and\pspeak to me again. I'll keep\nfive balls for you.$"

Pox_Text_OakBefore::
	.string "OAK: Check the balls on the right.\nWhich partner catches your eye?$"

Pox_Text_ElmBefore::
	.string "ELM: CYNDAQUIL is on the right.\nGive it time to warm up to you!$"

Pox_Text_BirchBefore::
	.string "BIRCH: TREECKO is on the left.\nKeeping up with it keeps me fit!$"

Pox_Text_OakAfter::
	.string "OAK: Follow ROUTE 101 north to\nOLDALE. Safe travels, {PLAYER}!$"

Pox_Text_ElmAfter::
	.string "ELM: I'm off to GOLDENROD CITY.\nLook after each other!$"

Pox_Text_BirchAfter::
	.string "BIRCH: I'm heading to FORTREE.\nSee you out in the field!$"

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
    checkitem ITEM_HM_CUT, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmHMNext1
    additem ITEM_HM_CUT, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmHMNext1::
    checkitem ITEM_HM_FLY, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmHMNext2
    additem ITEM_HM_FLY, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmHMNext2::
    checkitem ITEM_HM_SURF, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmHMNext3
    additem ITEM_HM_SURF, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmHMNext3::
    checkitem ITEM_HM_STRENGTH, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmHMNext4
    additem ITEM_HM_STRENGTH, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmHMNext4::
    @ HM Flash is retired and rejected by SanitizeItemId.
    checkitem ITEM_HM_ROCK_SMASH, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmHMNext6
    additem ITEM_HM_ROCK_SMASH, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmHMNext6::
    checkitem ITEM_HM_WATERFALL, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmHMNext7
    additem ITEM_HM_WATERFALL, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmHMNext7::
    checkitem ITEM_HM_DIVE, 1
    goto_if_eq VAR_RESULT, TRUE, Pox_ElmAllMachinesDone
    additem ITEM_HM_DIVE, 1
    goto_if_eq VAR_RESULT, FALSE, Pox_ElmTMsFull
Pox_ElmAllMachinesDone::
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
	.string "BIRCH: Take these TMs and HMs!\nThe MOVE COMPENDIUM also teaches\plevel-up, Egg, and tutor moves.$"
Pox_Text_ElmTMsFull::
    .string "BIRCH: Make room in your TM\npocket, then speak to me.\pI'll give you the rest!$"
Pox_Text_ElmCompendiumFull::
    .string "BIRCH: Make room in your KEY ITEMS\npocket, then speak to me again.$"

Pox_ElmLeave::
    goto_if_unset FLAG_POX_ELM_EXP_ALL, Pox_ElmLeaveDone
    msgbox Pox_Text_ElmAfter, MSGBOX_DEFAULT
    closemessage
    applymovement LOCALID_PLAYER, Pox_GiveProfessorRoom
    waitmovement 0
    applymovement 12, Pox_ElmLeaveMovement
    waitmovement 0
    removeobject 12
Pox_ElmLeaveDone::
    return

Pox_BirchLeave::
    goto_if_unset FLAG_POX_ELM_TMS, Pox_BirchLeaveDone
    msgbox Pox_Text_BirchAfter, MSGBOX_DEFAULT
    closemessage
    applymovement LOCALID_PLAYER, Pox_GiveProfessorRoom
    waitmovement 0
    applymovement 13, Pox_BirchLeaveMovement
    waitmovement 0
    removeobject 13
Pox_BirchLeaveDone::
    return

Pox_ElmLeaveMovement:
    walk_down
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
    walk_down
    walk_left
    walk_down
    walk_down
    walk_down
    walk_down
    walk_down
    walk_down
    walk_down
    step_end

Pox_GiveProfessorRoom:
    walk_down
    face_up
    step_end
