Route21_South_Frlg_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_Route21_South_Frlg
	.byte 0

Route21_South_Text_JackIntro::
	.string "I caught my POKéMON at sea.$"

Route21_South_Text_JackDefeat::
	.string "Diver!!\n"
	.string "Down!!$"

Route21_South_Text_JackPostBattle::
	.string "Where'd you catch your POKéMON?$"

Route21_South_Text_JeromeIntro::
	.string "Right now, I'm in a triathlon meet.$"

Route21_South_Text_JeromeDefeat::
	.string "Pant…\n"
	.string "Pant… Pant…$"

Route21_South_Text_JeromePostBattle::
	.string "I'm beat! But, I still have the\n"
	.string "bike race and marathon left!$"

Route21_South_Text_RolandIntro::
	.string "Ahh!\n"
	.string "Feel the sun and the wind!$"

Route21_South_Text_RolandDefeat::
	.string "Yow!\n"
	.string "I lost!$"

Route21_South_Text_RolandPostBattle::
	.string "I'm sunburnt to a crisp!$"

Route21_South_Text_ClaudeIntro::
	.string "Hey, don't scare away the fish!$"

Route21_South_Text_ClaudeDefeat::
	.string "Sorry! I'm just so frustrated from\n"
	.string "not catching anything.$"

Route21_South_Text_ClaudePostBattle::
	.string "Sheesh, I haven't caught a thing.\n"
	.string "Could this place actually be a\l"
	.string "giant pool or something?$"

Route21_South_Text_NolanIntro::
	.string "Keep me company till I get a hit.$"

Route21_South_Text_NolanDefeat::
	.string "That burned some time.$"

Route21_South_Text_NolanPostBattle::
	.string "Oh wait!\n"
	.string "I got a bite! Yeah!$"

Route21_North_Text_LilIntro::
	.string "LIL: Huh? A battle?\n"
	.string "IAN, can't you do it alone?$"

Route21_North_Text_LilDefeat::
	.string "LIL: Oh, see?\n"
	.string "We lost. Happy now?$"

Route21_North_Text_LilPostBattle::
	.string "LIL: I'm tired.\n"
	.string "Can't we go home already?$"

Route21_North_Text_LilNotEnoughMons::
	.string "LIL: Huh? A battle?\n"
	.string "I can't be bothered to do it alone.\l"
	.string "Bring two POKéMON, won't you?$"

Route21_North_Text_IanIntro::
	.string "IAN: My sis doesn't get enough\n"
	.string "exercise, so I made her come.$"

Route21_North_Text_IanDefeat::
	.string "IAN: Awww, Sis!\n"
	.string "Get it together!$"

Route21_North_Text_IanPostBattle::
	.string "IAN: Come on, Sis!\p"
	.string "You're not going to lose weight\n"
	.string "like this!$"

Route21_North_Text_IanNotEnoughMons::
	.string "IAN: We want a two-on-two battle.\n"
	.string "So can you bring two POKéMON?$"

@ Cinnabar seam: the sea road opens once the Mansion archives are read.
@ Only a southbound step (entering Cinnabar) is refused; a player already in
@ Cinnabar may always walk north onto the route. Refusal walks the player one
@ tile back up, onto row 48 of this map.
Route21_South_EventScript_CinnabarSeam::
	goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Route21_South_EventScript_CinnabarSeam_Open
	goto_if_set FLAG_POX_STORY_MANSION, Route21_South_EventScript_CinnabarSeam_Open
	specialvar VAR_RESULT, GetPlayerFacingDirection
	goto_if_ne VAR_RESULT, DIR_SOUTH, Route21_South_EventScript_CinnabarSeam_Open
	lockall
	msgbox Route21_South_Text_CinnabarSeam, MSGBOX_DEFAULT
	applymovement LOCALID_PLAYER, Common_Movement_WalkUp
	waitmovement 0
	releaseall
	end

Route21_South_EventScript_CinnabarSeam_Open::
	end

Route21_South_Text_CinnabarSeam::
	.string "A hard current runs off the island.\n"
	.string "You cannot cross here.$"
