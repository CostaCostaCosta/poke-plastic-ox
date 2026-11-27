MossdeepCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_MossdeepCity
	.byte 0

MossdeepCity_EventScript_NinjaBoy::
	msgbox MossdeepCity_Text_WailmerWatching, MSGBOX_NPC
	end

MossdeepCity_EventScript_ExpertM::
	msgbox MossdeepCity_Text_LifeNeedsSeaToLive, MSGBOX_NPC
	end

MossdeepCity_EventScript_Girl::
	msgbox MossdeepCity_Text_NiceIfWorldCoveredByFlowers, MSGBOX_NPC
	end

MossdeepCity_EventScript_Woman::
	msgbox MossdeepCity_Text_SpecialSpaceCenterRock, MSGBOX_NPC
	end

MossdeepCity_EventScript_WhiteRock::
	msgbox MossdeepCity_Text_ItsAWhiteRock, MSGBOX_SIGN
	end

MossdeepCity_EventScript_GymSign::
	msgbox MossdeepCity_Text_GymSign, MSGBOX_SIGN
	end

MossdeepCity_EventScript_CitySign::
	msgbox MossdeepCity_Text_CitySign, MSGBOX_SIGN
	end

MossdeepCity_EventScript_SpaceCenterSign::
	msgbox MossdeepCity_Text_SpaceCenterSign, MSGBOX_SIGN
	end

MossdeepCity_EventScript_Man::
	lock
	faceplayer
	msgbox MossdeepCity_Text_SurfExhilarating, MSGBOX_DEFAULT
	applymovement VAR_LAST_TALKED, Common_Movement_FaceOriginalDirection
	waitmovement 0
	release
	end

MossdeepCity_EventScript_KingsRockBoy::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_KINGS_ROCK, MossdeepCity_EventScript_ReceivedKingsRock
	msgbox MossdeepCity_Text_WantKingsRockStevenGaveMe, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, MossdeepCity_EventScript_DeclineKingsRock
	msgbox MossdeepCity_Text_YouCanKeepIt, MSGBOX_DEFAULT
	giveitem ITEM_KINGS_ROCK
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_KINGS_ROCK
	release
	end

MossdeepCity_EventScript_ReceivedKingsRock::
	msgbox MossdeepCity_Text_StevensHouseOverThere, MSGBOX_DEFAULT
	release
	end

MossdeepCity_EventScript_DeclineKingsRock::
	msgbox MossdeepCity_Text_WhatToDoWithWeirdRock, MSGBOX_DEFAULT
	release
	end

MossdeepCity_EventScript_OldRodFisherman::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_OLD_ROD, MossdeepCity_EventScript_OldRodAlreadyGave
	goto_if_unset FLAG_BADGE06_GET, MossdeepCity_EventScript_OldRodNotReady
	msgbox MossdeepCity_Text_OldRodFisherman, MSGBOX_DEFAULT
	giveitem ITEM_OLD_ROD
	goto_if_eq VAR_RESULT, FALSE, MossdeepCity_EventScript_OldRodBagFull
	setflag FLAG_RECEIVED_OLD_ROD
	msgbox MossdeepCity_Text_ReceivedOldRod, MSGBOX_DEFAULT
	release
	end

MossdeepCity_EventScript_OldRodAlreadyGave::
	msgbox MossdeepCity_Text_OldRodAfter, MSGBOX_DEFAULT
	release
	end

MossdeepCity_EventScript_OldRodNotReady::
	msgbox MossdeepCity_Text_OldRodNotReady, MSGBOX_DEFAULT
	release
	end

MossdeepCity_EventScript_OldRodBagFull::
	msgbox MossdeepCity_Text_OldRodBagFull, MSGBOX_DEFAULT
	release
	end

MossdeepCity_EventScript_BlackBelt::
	msgbox MossdeepCity_Text_SootopolisNewGymLeader, MSGBOX_NPC
	end

MossdeepCity_EventScript_Scott::
	lock
	faceplayer
	msgbox MossdeepCity_Text_ScottSomethingWrongWithTown, MSGBOX_DEFAULT
	closemessage
	call_if_eq VAR_FACING, DIR_NORTH, MossdeepCity_EventScript_ScottExitNorth
	call_if_eq VAR_FACING, DIR_EAST, MossdeepCity_EventScript_ScottExitEast
	addvar VAR_SCOTT_STATE, 1
	removeobject LOCALID_MOSSDEEP_SCOTT
	release
	end

MossdeepCity_EventScript_ScottExitNorth::
	applymovement LOCALID_PLAYER, MossdeepCity_Movement_PlayerWatchScottExit
	applymovement LOCALID_MOSSDEEP_SCOTT, MossdeepCity_Movement_ScottExitNorth
	waitmovement 0
	return

MossdeepCity_EventScript_ScottExitEast::
	applymovement LOCALID_PLAYER, MossdeepCity_Movement_PlayerWatchScottExit
	applymovement LOCALID_MOSSDEEP_SCOTT, MossdeepCity_Movement_ScottExitEast
	waitmovement 0
	return

MossdeepCity_Movement_PlayerWatchScottExit:
	delay_16
	delay_16
	walk_in_place_faster_left
	step_end

MossdeepCity_Movement_ScottExitNorth:
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	step_end

MossdeepCity_Movement_ScottExitEast:
	walk_down
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	step_end

MossdeepCity_Text_WantKingsRockStevenGaveMe:
	.string "STEVEN from next door gave me\nthis. He said it was a good one.\lIt's a rock.\pI think it's called a KING'S\nROCK. I can't use it for\lanything. Do you want it?$"

MossdeepCity_Text_YouCanKeepIt:
	.string "Really? Okay. I'll tell him I\ntraded it. He likes it when\lthings get traded.\pJust don't tell him what for.$"

MossdeepCity_Text_StevensHouseOverThere:
	.string "STEVEN's house is the one right\nthere. He's never in. He's\lalways somewhere with rocks.$"

MossdeepCity_Text_WhatToDoWithWeirdRock:
	.string "See, you don't want it either.\nIt's just a rock with a name.$"

MossdeepCity_Text_OldRodFisherman:
	.string "Thirty years I've fished these\n"
	.string "steps, and I've caught mostly\n"
	.string "MAGNEMITE.\p"
	.string "The fellow two doors down is always\n"
	.string "showing off his SUPER ROD.\p"
	.string "You don't need the fuss.\n"
	.string "Take this OLD ROD off my hands.$"

MossdeepCity_Text_ReceivedOldRod:
	.string "{PLAYER} received the OLD ROD!$"

MossdeepCity_Text_OldRodBagFull:
	.string "Make room in your KEY ITEMS pocket,\n"
	.string "then come back for the OLD ROD.$"

MossdeepCity_Text_OldRodAfter:
	.string "Try it in the tide pools past the\n"
	.string "SPACE CENTER. Watch your footing.$"

MossdeepCity_Text_OldRodNotReady:
	.string "Hold on there.\p"
	.string "A man can fish before he has proven\n"
	.string "anything at the GYM.\p"
	.string "TATE & LIZA live above the sign.$"

MossdeepCity_Text_WailmerWatching:
	.string "You can see WAILMER from the sea\nwall. I've counted eleven.\pMy sister says it's the same one\neleven times.$"

MossdeepCity_Text_NiceIfWorldCoveredByFlowers:
	.string "Everything grows here. Salt,\nwind, rocket smoke, and the\lflowers come up anyway.\pI'd like the whole coast to look\nlike this. I'd settle for my\lwindowsill.$"

MossdeepCity_Text_LifeNeedsSeaToLive:
	.string "Tide comes in, tide goes out. I\nhave watched it do that for\lseventy years, and it has never\lonce asked my opinion.\pThe mainland looks closer than\nit did when I was young. My eyes\lare worse, so it isn't that.$"

MossdeepCity_Text_SurfExhilarating:
	.string "I came over on the six o'clock\nferry. Six and six, they said.\lWith the wind up it was six and\lwhenever.\pYou crossed on a POKéMON? Then\nyou kept better time than the\lboat.$"

MossdeepCity_Text_SpecialSpaceCenterRock:
	.string "This white rock belongs to the\nSPACE CENTER. They set it here\lto wish their rockets safely up.\pYou write the wish on a tag and\ntie it on. I do one every launch\lwindow.\pIt hasn't failed yet, and\nneither have they.$"

MossdeepCity_Text_ItsAWhiteRock:
	.string "A white rock, hung with paper tags.\pMost say SAFE FLIGHT.\nOne says PLEASE, NOT A MONDAY.$"

MossdeepCity_Text_GymSign:
	.string "MOSSDEEP CITY POKéMON GYM\n"
	.string "LEADERS: LIZA & TATE\p"
	.string "“The mystic combination!”$"

MossdeepCity_Text_CitySign:
	.string "MOSSDEEP CITY\n"
	.string "“Our slogan: Cherish POKéMON!”$"

MossdeepCity_Text_SpaceCenterSign:
	.string "MOSSDEEP SPACE CENTER\n"
	.string "“The closest place to space.”$"

MossdeepCity_Text_ScottSomethingWrongWithTown:
	.string "SCOTT: Hello there. Don't mind\nme. I travel around looking for\lTRAINERS with a future.\pI came to see the pair at the\nGYM. Two LEADERS, one battle.\lYou don't find that on every\lisland.\pYou've got the look, too. I'll\nremember the face. That's my\lwhole job.$"

MossdeepCity_Text_SootopolisNewGymLeader:
	.string "The waves on your feet. Best\nthing there is after training.\pTATE and LIZA fight as a pair,\nso I train as a pair. My partner\lis the tide. It hasn't lost yet.$"
