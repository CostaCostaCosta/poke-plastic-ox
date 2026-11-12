FortreeCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_FortreeCity
	.byte 0

FortreeCity_EventScript_Man::
	msgbox FortreeCity_Text_SawGiganticPokemonInSky, MSGBOX_NPC
	end

FortreeCity_EventScript_GabbyRoadblock::
	lock
	faceplayer
	msgbox FortreeCity_Text_GabbyRoadblock, MSGBOX_NPC
	release
	end

FortreeCity_EventScript_TyRoadblock::
	lock
	faceplayer
	msgbox FortreeCity_Text_TyRoadblock, MSGBOX_NPC
	release
	end

FortreeCity_Text_GabbyRoadblock:
	.string "GABBY: Champion interview, right\nhere! Beat WINONA and we're live\lbefore you can leave town.$"

FortreeCity_Text_TyRoadblock:
	.string "TY: Camera's been up since dawn.\nTake your time.\pI'm paid by the day, not by the\ninterview.$"

FortreeCity_EventScript_Woman::
	lock
	faceplayer
	msgbox FortreeCity_Text_GymQueue, MSGBOX_DEFAULT
	release
	end

FortreeCity_EventScript_Girl::
	msgbox FortreeCity_Text_TreesGrowByDrinkingRainwater, MSGBOX_NPC
	end

FortreeCity_EventScript_OldMan::
	msgbox FortreeCity_Text_EveryoneHealthyAndLively, MSGBOX_NPC
	end

FortreeCity_EventScript_Boy::
	msgbox FortreeCity_Text_BugPokemonComeThroughWindow, MSGBOX_NPC
	end

FortreeCity_EventScript_GameboyKid::
	msgbox FortreeCity_Text_PokemonThatEvolveWhenTraded, MSGBOX_NPC
	end

FortreeCity_EventScript_CitySign::
	msgbox FortreeCity_Text_CitySign, MSGBOX_SIGN
	end

FortreeCity_EventScript_GymSign::
	msgbox FortreeCity_Text_GymSign, MSGBOX_SIGN
	end

FortreeCity_EventScript_WestGantrySign::
	msgbox FortreeCity_Text_WestGantrySign, MSGBOX_SIGN
	end

FortreeCity_EventScript_EastJunctionSign::
	msgbox FortreeCity_Text_EastJunctionSign, MSGBOX_SIGN
	end

FortreeCity_EventScript_Kecleon::
	lock
	faceplayer
	goto_if_set FLAG_BADGE04_GET, FortreeCity_EventScript_KecleonReveal
	msgbox FortreeCity_Text_SomethingInvisibleInTheWay, MSGBOX_DEFAULT
	release
	end

FortreeCity_EventScript_KecleonReveal::
	msgbox FortreeCity_Text_KecleonRevealed, MSGBOX_DEFAULT
	closemessage
	waitse
	playmoncry SPECIES_KECLEON, CRY_MODE_ENCOUNTER
	delay 30
	waitmoncry
	setflag FLAG_KECLEON_FLED_FORTREE
	removeobject VAR_LAST_TALKED
	release
	end

FortreeCity_Text_SawGiganticPokemonInSky:
	.string "No one believes me, but I saw this\n"
	.string "gigantic POKéMON in the sky.\p"
	.string "It seemed to squirm as it flew toward\n"
	.string "ROUTE 131.\p"
	.string "By the way… Sniff…\n"
	.string "Um… You, uh…smell singed.\p"
	.string "Were you at a volcano or something?$"

FortreeCity_Text_GymQueue:
	.string "Challenge days, the GYM queue runs\n"
	.string "down the ladder and out onto the\l"
	.string "walkway.\p"
	.string "Nobody minds. WINONA is worth\n"
	.string "the wait.$"

FortreeCity_Text_TreesGrowByDrinkingRainwater:
	.string "The ground absorbs rainwater, and\n"
	.string "trees grow by drinking that water…\p"
	.string "Our FORTREE CITY exists because\n"
	.string "there's both water and soil.$"

FortreeCity_Text_EveryoneHealthyAndLively:
	.string "The CITY consists of homes built on\n"
	.string "trees.\p"
	.string "Perhaps because of that lifestyle,\n"
	.string "everyone is healthy and lively.\p"
	.string "Why, even myself--I feel as if I've\n"
	.string "grown thirty years younger.$"

FortreeCity_Text_BugPokemonComeThroughWindow:
	.string "Living on top of trees is okay.\p"
	.string "But sometimes BUG POKéMON come in\n"
	.string "through windows.\l"
	.string "It can be really startling.$"

FortreeCity_Text_PokemonThatEvolveWhenTraded:
	.string "There are POKéMON that evolve when\n"
	.string "you trade them! That's what I heard.$"

FortreeCity_Text_SomethingInvisibleInTheWay:
	.string "Something invisible is in the way.\p"
	.string "You push. It pushes back.\n"
	.string "It isn't going to move.$"

FortreeCity_Text_KecleonRevealed:
	.string "The shape in the walkway shivers\n"
	.string "and comes into view.\p"
	.string "It's a KECLEON!\p"
	.string "Startled, it scrambles off along\n"
	.string "the ropes.$"

FortreeCity_Text_CitySign:
	.string "FORTREE CITY\n"
	.string "“The treetop city that frolics with\l"
	.string "nature.”$"

FortreeCity_Text_GymSign:
	.string "FORTREE CITY POKéMON GYM\n"
	.string "LEADER: WINONA\p"
	.string "“The bird user taking flight into\n"
	.string "the world.”$"

FortreeCity_Text_WestGantrySign:
	.string "WEST GANTRY\n"
	.string "One person at a time.\p"
	.string "No loads over forty kilos.$"

FortreeCity_Text_EastJunctionSign:
	.string "EAST JUNCTION\n"
	.string "Coast road below.\p"
	.string "Cycling deck above.\n"
	.string "Mind the rope on the turn.$"
