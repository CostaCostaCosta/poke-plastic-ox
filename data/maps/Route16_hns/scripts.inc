Route16_hns_MapScripts::
	.byte 0

Route16_EventScript_Npc1::
	lock
	faceplayer
	msgbox Route16_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

Route16_EventScript_Npc1_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

