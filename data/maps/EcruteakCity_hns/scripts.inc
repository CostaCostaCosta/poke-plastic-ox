EcruteakCity_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_EcruteakCity_hns
	.byte 0

EcruteakCity_EventScript_Npc1::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_KimonoRoadblock::
	lock
	faceplayer
	msgbox EcruteakCity_Text_KimonoRoadblock, MSGBOX_NPC
	release
	end

EcruteakCity_Text_KimonoRoadblock:
	.string "MORTY must approve your passage.\nEarn ECRUTEAK GYM's BADGE first.$"

EcruteakCity_EventScript_Npc2::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc3::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc4::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc5::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc5_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc6::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc6_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc7::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc7_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc1_Text:
	.string "The KIMONO dancers rehearse\nwhile the bells ring across\ptown.$"

EcruteakCity_EventScript_Npc2_Text:
	.string "The BURNED TOWER remembers the fire. The fire remembers nothing.$"

EcruteakCity_EventScript_Npc3_Text:
	.string "The BURNED TOWER still stands.\nWe keep its history alive.$"

EcruteakCity_EventScript_Npc4_Text:
	.string "MORTY studies GHOST POKéMON.\nBring a team that can face them.$"

EcruteakCity_EventScript_Npc5_Text:
	.string "The west gate leads toward the\nLEAGUE. The guard checks BADGES\pthere.$"

EcruteakCity_EventScript_Npc6_Text:
	.string "Our old wooden houses have heard\ngenerations of POKéMON stories.$"

EcruteakCity_EventScript_Npc7_Text:
	.string "At dusk, the tower casts a long\nshadow across the rooftops.$"

PoxEcruteak_WestEntrance::
	lockall
	warp MAP_GATE_ECRUTEAK_CITY_ROUTE38_HNS, 10, 5
	waitstate
	releaseall
	end

PoxEcruteak_EastExit::
	lockall
	goto_if_unset FLAG_POX_TRIGGERS_ENABLED, PoxEcruteak_EastExit_Open
	goto_if_unset FLAG_POX_STORY_BURNED_TOWER, PoxEcruteak_EastExit_Closed
PoxEcruteak_EastExit_Open::
	warp MAP_ROUTE119, 5, 124
	waitstate
	releaseall
	end
PoxEcruteak_EastExit_Closed::
	msgbox PoxEcruteak_Text_EastExitClosed, MSGBOX_DEFAULT
	releaseall
	end

PoxEcruteak_Text_EastExitClosed::
	.string "The east road is shut.\pNo one goes past the last lamp\nwhile MORTY is under the tower.$"

PoxEcruteak_EastWatch::
	lock
	faceplayer
	goto_if_set FLAG_POX_STORY_BURNED_TOWER, PoxEcruteak_EastWatch_Open
	msgbox PoxEcruteak_Text_EastWatch, MSGBOX_NPC
	release
	end

PoxEcruteak_EastWatch_Open::
	msgbox PoxEcruteak_Text_EastWatchOpen, MSGBOX_NPC
	release
	end

PoxEcruteak_Text_EastWatch::
	.string "ROUTE 119 runs east of here.\pThe watch keeps the road shut\nuntil MORTY comes back up.$"

PoxEcruteak_Text_EastWatchOpen::
	.string "ROUTE 119 is open.\pThe decks are wet, so mind the\nriver on the way down.$"
