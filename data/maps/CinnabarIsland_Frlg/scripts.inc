CinnabarIsland_Frlg_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_CinnabarIsland_Frlg
	.byte 0

CinnabarIsland_EventScript_IslandSign::
	msgbox CinnabarIsland_Text_IslandSign, MSGBOX_SIGN
	end
CinnabarIsland_Text_IslandSign::
	.string "CINNABAR ISLAND\nThe Fiery Town of Burning Desire$"

CinnabarIsland_EventScript_PokemonLabSign::
	msgbox CinnabarIsland_Text_PokemonLabSign, MSGBOX_SIGN
	end
CinnabarIsland_Text_PokemonLabSign::
	.string "POKéMON LAB$"

CinnabarIsland_EventScript_GymSign::
	msgbox CinnabarIsland_Text_GymSign, MSGBOX_SIGN
	end
CinnabarIsland_Text_GymSign::
	.string "CINNABAR ISLAND POKéMON GYM$"
