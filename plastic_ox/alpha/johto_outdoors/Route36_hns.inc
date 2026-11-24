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

Route36_EventScript_Sleeper::
	lock
	goto_if_set FLAG_BADGE04_GET, Route36_EventScript_SleeperWakes
	msgbox Route36_Text_SleeperSnoring, MSGBOX_DEFAULT
	release
	end

Route36_EventScript_SleeperWakes::
	playse SE_PIN
	applymovement VAR_LAST_TALKED, Common_Movement_ExclamationMark
	waitmovement 0
	applymovement VAR_LAST_TALKED, Common_Movement_FacePlayer
	waitmovement 0
	msgbox Route36_Text_SleeperWakes, MSGBOX_DEFAULT
	closemessage
	specialvar VAR_RESULT, GetPlayerFacingDirection
	goto_if_eq VAR_RESULT, DIR_EAST, Route36_EventScript_SleeperLeavesEast
	applymovement VAR_LAST_TALKED, Route36_Movement_SleeperLeavesWest
	goto Route36_EventScript_SleeperGone

Route36_EventScript_SleeperLeavesEast::
	applymovement VAR_LAST_TALKED, Route36_Movement_SleeperLeavesEast
Route36_EventScript_SleeperGone::
	waitmovement 0
	removeobject VAR_LAST_TALKED
	setflag FLAG_POX_ROUTE36_SLEEPER_MOVED
	release
	end

Route36_Movement_SleeperLeavesEast:
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

Route36_Movement_SleeperLeavesWest:
	walk_left
	walk_left
	walk_left
	walk_left
	walk_up
	walk_up
	walk_up
	step_end

Route36_Text_SleeperSnoring:
	.string "Zzz… Zzz…\p"
	.string "A hiker is fast asleep right\n"
	.string "across the eastern road.\p"
	.string "He mumbles without waking:\n"
	.string "“…not till somebody shows me…\l"
	.string "…the feather one…”$"

Route36_Text_SleeperWakes:
	.string "Hnh? Wha-?\p"
	.string "That badge… that's the feather\n"
	.string "one! So somebody finally beat\l"
	.string "the lady with the birds.\p"
	.string "I told my brother I'd nap here\n"
	.string "until I saw it with my own eyes.\p"
	.string "Ow, my back. I'm going home for\n"
	.string "a proper bed. The road's yours.$"

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
