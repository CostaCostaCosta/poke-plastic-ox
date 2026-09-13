Route24_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_Route24_hns
	.byte 0

Route24_EventScript_Npc1::
	lock
	faceplayer
	msgbox Route24_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

Route24_EventScript_Npc2::
	lock
	faceplayer
	msgbox Route24_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

Route24_EventScript_Npc3::
	lock
	faceplayer
	msgbox Route24_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

Route24_EventScript_Npc4::
	lock
	faceplayer
	msgbox Route24_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

Route24_EventScript_Npc1_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route24_EventScript_Npc2_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route24_EventScript_Npc3_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route24_EventScript_Npc4_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"
