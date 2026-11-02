Gate_SaffronCity_Route6_hns_MapScripts::
	.byte 0

Gate_SaffronCity_Route6_EventScript_Npc1::
	lock
	faceplayer
	msgbox Gate_SaffronCity_Route6_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

Gate_SaffronCity_Route6_EventScript_Npc1_Text:
	.string "Keep the doorway clear so\ntravelers can pass safely.$"

