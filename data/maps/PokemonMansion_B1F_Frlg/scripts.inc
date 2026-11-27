PokemonMansion_B1F_Frlg_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, PokemonMansion_B1F_OnLoad
	.byte 0

PokemonMansion_B1F_OnLoad::
	call_if_set FLAG_POKEMON_MANSION_SWITCH_STATE, PokemonMansion_EventScript_PressSwitch_B1F
	end

PokemonMansion_B1F_EventScript_Statue::
	lockall
	setvar VAR_0x8004, 3
	call PokemonMansion_EventScript_SecretSwitch
	playse SE_UNLOCK
	special DrawWholeMapView
	waitse
	releaseall
	end

PokemonMansion_B1F_EventScript_DiarySep1st::
	msgbox PokemonMansion_B1F_Text_MewtwoIsFarTooPowerful, MSGBOX_SIGN
	end

PokemonMansion_B1F_EventScript_Lewis::
	trainerbattle_single TRAINER_BURGLAR_LEWIS, PokemonMansion_B1F_Text_LewisIntro, PokemonMansion_B1F_Text_LewisDefeat
	msgbox PokemonMansion_B1F_Text_LewisPostBattle, MSGBOX_AUTOCLOSE
	end

PokemonMansion_B1F_EventScript_Ivan::
	trainerbattle_single TRAINER_SCIENTIST_IVAN, PokemonMansion_B1F_Text_IvanIntro, PokemonMansion_B1F_Text_IvanDefeat
	msgbox PokemonMansion_B1F_Text_IvanPostBattle, MSGBOX_AUTOCLOSE
	end

PokemonMansion_B1F_Text_LewisIntro::
	.string "Uh-oh. This isn't the way out.$"

PokemonMansion_B1F_Text_LewisDefeat::
	.string "Awooh! I give!$"

PokemonMansion_B1F_Text_LewisPostBattle::
	.string "There's an old man sitting down\nthe hall with something enormous\lbeside him.\pNeither of them even looked at\nme. I have never felt so\lignored.$"

PokemonMansion_B1F_Text_IvanIntro::
	.string "The basement holds a steady\ntemperature. Ideal for paper.\lMind the shelves!$"

PokemonMansion_B1F_Text_IvanDefeat::
	.string "What was that for?$"

PokemonMansion_B1F_Text_IvanPostBattle::
	.string "I come down to copy what's still\nlegible.\pWhoever typed these was careful,\nand a little afraid. You can\ltell by what they underlined.$"

PokemonMansion_B1F_Text_MewtwoIsFarTooPowerful::
	.string "Diary: Sept. 1\n"
	.string "MEWTWO is far too powerful.\p"
	.string "We have failed to curb its vicious\n"
	.string "tendencies…$"

