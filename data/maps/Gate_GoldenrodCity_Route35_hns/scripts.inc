Gate_GoldenrodCity_Route35_hns_MapScripts::
	.byte 0

Gate_GoldenrodCity_Route35_EventScript_Npc1::
	lock
	faceplayer
	msgbox Gate_GoldenrodCity_Route35_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

Gate_GoldenrodCity_Route35_EventScript_Npc2::
	lock
	faceplayer
	msgbox Gate_GoldenrodCity_Route35_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

Gate_GoldenrodCity_Route35_EventScript_Npc3::
	lock
	faceplayer
	msgbox Gate_GoldenrodCity_Route35_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

Gate_GoldenrodCity_Route35_EventScript_Portal2::
	warp MAP_GOLDENROD_CITY_HNS, 33, 8
	waitstate
	end

Gate_GoldenrodCity_Route35_EventScript_Portal3::
	warp MAP_ROUTE35_HNS, 14, 48
	waitstate
	end

Gate_GoldenrodCity_Route35_EventScript_Npc1_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Gate_GoldenrodCity_Route35_EventScript_Npc2_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Gate_GoldenrodCity_Route35_EventScript_Npc3_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

