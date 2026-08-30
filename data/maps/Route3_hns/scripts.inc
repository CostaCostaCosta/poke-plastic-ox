Route3_hns_MapScripts::
	.byte 0

Route3_EventScript_Npc1::
	lock
	faceplayer
	msgbox Route3_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

Route3_EventScript_Npc2::
	lock
	faceplayer
	msgbox Route3_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

Route3_EventScript_Npc3::
	lock
	faceplayer
	msgbox Route3_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

Route3_EventScript_Npc4::
	lock
	faceplayer
	msgbox Route3_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

Route3_EventScript_Npc1_Text:
	.string "Trainers come through the tunnel east\nspeaking UNOVAN. It's a whole thing.$"

Route3_EventScript_Npc2_Text:
	.string "MT.MOON's east. There's a cave in it,\nand a region somewhere in that cave.$"

Route3_EventScript_Npc3_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route3_EventScript_Npc4_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"
