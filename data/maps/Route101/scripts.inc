Route101_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_Route101
	.byte 0

Route101_EventScript_Youngster::
	msgbox Route101_Text_TakeTiredPokemonToPokeCenter, MSGBOX_NPC
	end

Route101_EventScript_Boy::
	msgbox Route101_Text_QuietGrass, MSGBOX_NPC
	end

Route101_EventScript_RouteSign::
	msgbox Route101_Text_RouteSign, MSGBOX_SIGN
	end

Route101_Text_TakeTiredPokemonToPokeCenter::
	.string "The TRAINERS on the routes ahead are\n"
	.string "strong!\p"
	.string "Catch more POKéMON before you take\n"
	.string "them on.$"

Route101_Text_QuietGrass::
	.string "Wild POKéMON hide in the tall grass.\p"
	.string "Walk through it and one may appear.$"

Route101_Text_RouteSign::
	.string "ROUTE 101\n"
	.string "{UP_ARROW} OLDALE TOWN$"
