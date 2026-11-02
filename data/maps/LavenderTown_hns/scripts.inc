LavenderTown_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_LavenderTown_hns
	.byte 0

LavenderTown_EventScript_Npc1::
	lock
	faceplayer
	msgbox LavenderTown_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

LavenderTown_EventScript_Npc2::
	lock
	faceplayer
	msgbox LavenderTown_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

LavenderTown_EventScript_Npc3::
	lock
	faceplayer
	msgbox LavenderTown_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

LavenderTown_EventScript_Npc4::
	lock
	faceplayer
	msgbox LavenderTown_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

LavenderTown_EventScript_Sign1::
	msgbox LavenderTown_EventScript_Sign1_Text, MSGBOX_SIGN
	end

LavenderTown_EventScript_Sign2::
	msgbox LavenderTown_EventScript_Sign2_Text, MSGBOX_SIGN
	end

LavenderTown_EventScript_Sign3::
	msgbox LavenderTown_EventScript_Sign3_Text, MSGBOX_SIGN
	end

LavenderTown_EventScript_Sign4::
	msgbox LavenderTown_EventScript_Sign4_Text, MSGBOX_SIGN
	end

LavenderTown_EventScript_Npc1_Text:
	.string "People come here to remember the\nPOKéMON they loved.$"

LavenderTown_EventScript_Npc2_Text:
	.string "Speak softly near the tower.\nSome visitors are grieving.$"

LavenderTown_EventScript_Npc3_Text:
	.string "People come here to remember the\nPOKéMON they loved.$"

LavenderTown_EventScript_Npc4_Text:
	.string "Speak softly near the tower.\nSome visitors are grieving.$"

LavenderTown_EventScript_Sign1_Text:
	.string "A sign from the old routes.$"

LavenderTown_EventScript_Sign2_Text:
	.string "A sign from the old routes.$"

LavenderTown_EventScript_Sign3_Text:
	.string "A sign from the old routes.$"

LavenderTown_EventScript_Sign4_Text:
	.string "A sign from the old routes.$"

LavenderTown_EventScript_SouthRoadClosed::
	msgbox LavenderTown_EventScript_SouthRoadClosed_Text, MSGBOX_NPC
	end

LavenderTown_EventScript_SouthRoadClosed_Text:
	.string "The southern road is closed.\nPlease use another route.$"
