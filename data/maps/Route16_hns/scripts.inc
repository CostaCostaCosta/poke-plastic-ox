Route16_hns_MapScripts::
	.byte 0

Route16_EventScript_Npc1::
	lock
	faceplayer
	msgbox Route16_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

Route16_EventScript_Npc1_Text:
	.string "Check your bicycle before a long\nride. Brakes matter!$"

