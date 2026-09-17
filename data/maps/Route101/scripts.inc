Route101_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_Route101
	.byte 0

Route101_EventScript_Youngster::
	msgbox Route101_Text_StrongTrainersAhead, MSGBOX_NPC
	end

Route101_EventScript_Boy::
	msgbox Route101_Text_PoochyenaSniffedShoes, MSGBOX_NPC
	end

Route101_EventScript_RouteSign::
	msgbox Route101_Text_RouteSign, MSGBOX_SIGN
	end

Route101_Text_StrongTrainersAhead::
	.string "I thought one POKéMON was enough.\n"
	.string "The next route changed my mind!\p"
	.string "The TRAINERS ahead are strong.\n"
	.string "Catch more POKéMON before you go!$"

Route101_Text_PoochyenaSniffedShoes::
	.string "A POOCHYENA sniffed my shoes\n"
	.string "all the way up from PALLET!\p"
	.string "Do I smell different to the\n"
	.string "POKéMON here?$"

Route101_Text_RouteSign::
	.string "ROUTE 101\n"
	.string "{UP_ARROW} OLDALE TOWN$"
