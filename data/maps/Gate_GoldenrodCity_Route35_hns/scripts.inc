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

Gate_GoldenrodCity_Route35_EventScript_Npc1_Text:
	.string "Gate's open and the road is clear.\nMind the ledges once you're out\nthere.$"

Gate_GoldenrodCity_Route35_EventScript_Npc2_Text:
	.string "I cut through this gatehouse on my\nway to the park. It saves me the\nhill.$"

Gate_GoldenrodCity_Route35_EventScript_Npc3_Text:
	.string "The water is a long walk from here.\nI carry the rod anyway, just in\ncase.$"
