Gate_SaffronCity_Route6_hns_MapScripts::
	.byte 0

Gate_SaffronCity_Route6_EventScript_Npc1::
	lock
	faceplayer
	msgbox Gate_SaffronCity_Route6_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

Gate_SaffronCity_Route6_EventScript_Npc1_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

