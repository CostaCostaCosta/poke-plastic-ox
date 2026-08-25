Gate_AzaleaTown_IlexForest_hns_MapScripts::
	.byte 0

Gate_AzaleaTown_IlexForest_EventScript_Npc1::
	lock
	faceplayer
	msgbox Gate_AzaleaTown_IlexForest_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

Gate_AzaleaTown_IlexForest_EventScript_Npc2::
	lock
	faceplayer
	msgbox Gate_AzaleaTown_IlexForest_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

Gate_AzaleaTown_IlexForest_EventScript_Npc1_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Gate_AzaleaTown_IlexForest_EventScript_Npc2_Text:
	.string "In my day this gate went two places,\nnot wherever you felt like walking.$"
Gate_AzaleaTown_IlexForest_EventScript_ToIlex::
	warp MAP_ILEX_FOREST_HNS, 22, 63
	waitstate
	end
Gate_AzaleaTown_IlexForest_EventScript_ToR31::
	warp MAP_ROUTE31_HNS, 1
	waitstate
	end
