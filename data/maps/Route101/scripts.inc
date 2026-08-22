Route101_MapScripts::
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
	.string "If POKéMON get tired, take them to\n"
	.string "a POKéMON CENTER.\p"
	.string "There's one in OLDALE TOWN.$"

Route101_Text_QuietGrass::
	.string "The tall grass is quiet today.\p"
	.string "No wild POKéMON are appearing.$"

Route101_Text_RouteSign::
	.string "ROUTE 101\n"
	.string "{UP_ARROW} OLDALE TOWN$"
