CinnabarIsland_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_CinnabarIsland_hns
	.byte 0

CinnabarIsland_EventScript_Npc1::
	lock
	faceplayer
	msgbox CinnabarIsland_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

CinnabarIsland_EventScript_Npc2::
	lock
	faceplayer
	msgbox CinnabarIsland_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

CinnabarIsland_EventScript_Sign1::
	msgbox CinnabarIsland_EventScript_Sign1_Text, MSGBOX_SIGN
	end

CinnabarIsland_EventScript_Sign2::
	msgbox CinnabarIsland_EventScript_Sign2_Text, MSGBOX_SIGN
	end

CinnabarIsland_EventScript_Npc1_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

CinnabarIsland_EventScript_Npc2_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

CinnabarIsland_EventScript_Sign1_Text:
	.string "A sign from the old routes.$"

CinnabarIsland_EventScript_Sign2_Text:
	.string "A sign from the old routes.$"
