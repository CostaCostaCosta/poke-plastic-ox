Route36_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_Route36_hns
	.byte 0

Route36_EventScript_Npc1::
	lock
	faceplayer
	msgbox Route36_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

Route36_EventScript_Npc2::
	lock
	faceplayer
	msgbox Route36_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

Route36_EventScript_Npc3::
	lock
	faceplayer
	msgbox Route36_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

Route36_EventScript_Npc4::
	lock
	faceplayer
	msgbox Route36_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

Route36_EventScript_Npc5::
	lock
	faceplayer
	msgbox Route36_EventScript_Npc5_Text, MSGBOX_NPC
	release
	end

Route36_EventScript_Npc1_Text:
	.string "Goldenrod florists trade seeds\nwith the park gardeners.\pSome flowers now bloom a whole\nseason earlier. Nobody knows\pwhy.$"

Route36_EventScript_Npc2_Text:
	.string "My family meets here every\nThursday.\pEven when the roads change, we\nkeep coming back to the same\pold trees.$"

Route36_EventScript_Npc3_Text:
	.string "The stone walls were laid\nwithout mortar.\pI repair them by fitting each\nrock against its neighbors,\plike a puzzle.$"

Route36_EventScript_Npc4_Text:
	.string "Birds nest in these old trees.\nA quiet traveler hears more\pthan a noisy one.$"

Route36_EventScript_Npc5_Text:
	.string "I sketch the crossroads for\nschool. The landmarks matter\pmore than the names on the\nsigns.$"

Route36_EventScript_Snorlax::
	lockall
	checkitem ITEM_POKE_FLUTE
	goto_if_eq VAR_RESULT, FALSE, Route36_EventScript_SnorlaxSleeping
	call EventScript_AwakenSnorlax
	setwildbattle SPECIES_SNORLAX, 30, ITEM_NONE
	dowildbattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, Route36_EventScript_SnorlaxCleared
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, Route36_EventScript_SnorlaxCleared
	msgbox Route36_Text_SnorlaxSleepingAgain, MSGBOX_DEFAULT
	releaseall
	end

Route36_EventScript_SnorlaxCleared::
	setflag FLAG_POX_ROUTE36_SNORLAX_CLEARED
	removeobject VAR_LAST_TALKED
	releaseall
	end

Route36_EventScript_SnorlaxSleeping::
	msgbox Route36_Text_SnorlaxSleeping, MSGBOX_DEFAULT
	releaseall
	end

Route36_Text_SnorlaxSleeping:
	.string "SNORLAX blocks the eastern road.\n"
	.string "A POKé FLUTE might wake it.$"

Route36_Text_SnorlaxSleepingAgain:
	.string "SNORLAX went back to sleep,\n"
	.string "blocking the road again.$"

Route36_EventScript_Alan::
	trainerbattle_single TRAINER_PLASTIC_OX_JOHTO_ALAN, Route36_EventScript_Alan_Intro, Route36_EventScript_Alan_Defeat
	msgbox Route36_EventScript_Alan_After, MSGBOX_AUTOCLOSE
	end
Route36_EventScript_Alan_Intro:
	.string "I study the plants on this\nroad. Let's compare field\pnotes in a battle!$"
Route36_EventScript_Alan_Defeat:
	.string "I missed a detail!$"
Route36_EventScript_Alan_After:
	.string "The odd tree has no leaves to\npress in my notebook.\pMaybe I should study Pokemon\nas well as plants.$"
