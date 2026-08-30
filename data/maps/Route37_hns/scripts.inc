Route37_hns_MapScripts::
	.byte 0

Route37_EventScript_Npc1::
	lock
	faceplayer
	msgbox Route37_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

Route37_EventScript_Npc2::
	lock
	faceplayer
	msgbox Route37_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

Route37_EventScript_Npc3::
	lock
	faceplayer
	msgbox Route37_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

Route37_EventScript_Npc4::
	lock
	faceplayer
	msgbox Route37_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

Route37_EventScript_Npc1_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route37_EventScript_Npc2_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route37_EventScript_Npc3_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route37_EventScript_Npc4_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

