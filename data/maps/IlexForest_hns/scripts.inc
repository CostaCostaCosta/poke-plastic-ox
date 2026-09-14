IlexForest_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_IlexForest_hns
	.byte 0

IlexForest_EventScript_Npc1::
	lock
	faceplayer
	msgbox IlexForest_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

IlexForest_EventScript_Npc2::
	lock
	faceplayer
	msgbox IlexForest_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

IlexForest_EventScript_Npc4::
	lock
	faceplayer
	msgbox IlexForest_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

IlexForest_EventScript_Npc5::
	lock
	faceplayer
	msgbox IlexForest_EventScript_Npc5_Text, MSGBOX_NPC
	release
	end

Pox_IlexForest_EventScript_HeadbuttKey::
	lock
	faceplayer
	checkitem ITEM_HEADBUTT_KEY
	goto_if_eq VAR_RESULT, TRUE, Pox_IlexForest_EventScript_ExplainHeadbuttKey
	msgbox Pox_IlexForest_Text_HeadbuttKeyIntro, MSGBOX_DEFAULT
	giveitem ITEM_HEADBUTT_KEY
	goto_if_eq VAR_RESULT, FALSE, Pox_IlexForest_EventScript_HeadbuttKeyEnd
Pox_IlexForest_EventScript_ExplainHeadbuttKey::
	msgbox Pox_IlexForest_Text_HeadbuttKeyOwned, MSGBOX_DEFAULT
Pox_IlexForest_EventScript_HeadbuttKeyEnd::
	release
	end

IlexForest_EventScript_Npc6::
	lock
	faceplayer
	msgbox IlexForest_EventScript_Npc6_Text, MSGBOX_NPC
	release
	end

IlexForest_EventScript_Item7::
	finditem ITEM_POKE_BALL
	end

IlexForest_EventScript_Item8::
	finditem ITEM_POKE_BALL
	end

IlexForest_EventScript_Item9::
	finditem ITEM_POKE_BALL
	end

IlexForest_EventScript_Npc10::
	lock
	faceplayer
	msgbox IlexForest_EventScript_Npc10_Text, MSGBOX_NPC
	release
	end

IlexForest_EventScript_Npc11::
	lock
	faceplayer
	msgbox IlexForest_EventScript_Npc11_Text, MSGBOX_NPC
	release
	end

IlexForest_EventScript_Npc12::
	lock
	faceplayer
	msgbox IlexForest_EventScript_Npc12_Text, MSGBOX_NPC
	release
	end

IlexForest_EventScript_Item13::
	finditem ITEM_POKE_BALL
	end

IlexForest_EventScript_Sign1::
	msgbox IlexForest_EventScript_Sign1_Text, MSGBOX_SIGN
	end

IlexForest_EventScript_Sign2::
	msgbox IlexForest_EventScript_Sign2_Text, MSGBOX_SIGN
	end

IlexForest_EventScript_Npc1_Text:
	.string "The forest paths loop past each other\nnow. Some mornings I end up in KANTO\nby accident.$"

IlexForest_EventScript_Npc2_Text:
	.string "A BUG-CATCHER told me the bugs out\nwest count double. I'm going to catch\nso many.$"

IlexForest_EventScript_Npc3_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

IlexForest_EventScript_Npc4_Text:
	.string "This wood feels older than the map\nsays. The signposts disagree with\neach other.$"

IlexForest_EventScript_Npc5_Text:
	.string "I fish where the trees let me. The\nriver doesn't care which region it's\nin.$"

Pox_IlexForest_Text_HeadbuttKeyIntro:
	.string "The trees here hide all kinds of\n"
	.string "POKéMON. Take this HEADBUTT KEY!$"

Pox_IlexForest_Text_HeadbuttKeyOwned:
	.string "That HEADBUTT KEY belongs with a\n"
	.string "TRAINER who respects the forest.$"

IlexForest_EventScript_Npc6_Text:
	.string "Something in these woods isn't in any\ndex I've seen. Probably nothing!$"

IlexForest_EventScript_Npc10_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

IlexForest_EventScript_Npc11_Text:
	.string "We dance for the forest. It has been\nvery patient with all these new\nroads.$"

IlexForest_EventScript_Npc12_Text:
	.string "Two routes start at the north edge.\nNeither one is on Grandpa's map.$"

IlexForest_EventScript_Sign1_Text:
	.string "ILEX FOREST\nThe trees lean away from the new road.$"

IlexForest_EventScript_Sign2_Text:
	.string "ILEX FOREST\nShrine of the forest guardian.$"
