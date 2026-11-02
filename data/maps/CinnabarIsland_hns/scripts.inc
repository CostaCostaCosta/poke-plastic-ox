CinnabarIsland_hns_MapScripts::
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
	.string "The sea is calm today, but this\nisland was shaped by fire.$"

CinnabarIsland_EventScript_Npc2_Text:
	.string "Our researchers study the traces\nleft by ancient POKéMON.$"

CinnabarIsland_EventScript_Sign1_Text:
	.string "A sign from the old routes.$"

CinnabarIsland_EventScript_Sign2_Text:
	.string "A sign from the old routes.$"
