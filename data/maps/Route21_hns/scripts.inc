Route21_hns_MapScripts::
	.byte 0

Route21_EventScript_Npc1::
	lock
	faceplayer
	msgbox Route21_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

Route21_EventScript_Npc2::
	lock
	faceplayer
	msgbox Route21_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

Route21_EventScript_Npc3::
	lock
	faceplayer
	msgbox Route21_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

Route21_EventScript_Npc1_Text:
	.string "The current pulls west near the\nislands. Swim with it and you'll\psave your strength.$"

Route21_EventScript_Npc2_Text:
	.string "I always check my supplies\nbefore heading into the trees.$"

Route21_EventScript_Npc3_Text:
	.string "TENTACOOL keep snagging my line.\nI came for the big fish out past\pthe reef.$"

