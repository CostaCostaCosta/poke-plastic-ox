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

IlexForest_EventScript_BugcatcherWayne::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE_ILEX, IlexForest_Text_BugCatcherWayneSeen, IlexForest_Text_BugCatcherWayneBeaten
	msgbox IlexForest_Text_BugCatcherWayneAfter, MSGBOX_AUTOCLOSE
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
	.string "I train by walking this trail.\n"
	.string "My legs quit before my POKéMON!$"

IlexForest_EventScript_Npc2_Text:
	.string "My net keeps catching twigs.\n"
	.string "The bugs make it look so easy!$"

IlexForest_EventScript_Npc3_Text:
	.string "I stop here to hear the leaves.\n"
	.string "Go on. The road can wait.$"

IlexForest_EventScript_Npc4_Text:
	.string "I packed a lunch for the walk.\n"
	.string "A leaf landed in my sandwich!\p"
	.string "I came here for the scenery,\n"
	.string "not to eat it.$"

IlexForest_EventScript_Npc5_Text:
	.string "I found a fine fishing spot.\n"
	.string "The branches caught my line.\p"
	.string "Well, I said it was fine.\n"
	.string "I didn't say it was roomy!$"

Pox_IlexForest_Text_HeadbuttKeyIntro:
	.string "Hear that rustle overhead?\n"
	.string "POKéMON hide in the branches.\p"
	.string "Take this HEADBUTT KEY.\n"
	.string "Keep it safe on your travels!$"

Pox_IlexForest_Text_HeadbuttKeyOwned:
	.string "Take care of that HEADBUTT KEY.\n"
	.string "These trees have plenty of life.\p"
	.string "I could sit here all afternoon\n"
	.string "just listening to the branches.$"

IlexForest_Text_BugCatcherWayneSeen:
	.string "Don't sneak up on me like that!\p"
	.string "You frightened a POKéMON away!$"

IlexForest_Text_BugCatcherWayneBeaten:
	.string "I hadn't seen that POKéMON before…$"

IlexForest_Text_BugCatcherWayneAfter:
	.string "A POKéMON I've never seen before\n"
	.string "fell out of the tree when I used\l"
	.string "HEADBUTT.\p"
	.string "I ought to use HEADBUTT in other\n"
	.string "places too.$"

IlexForest_EventScript_Npc10_Text:
	.string "These trees have stood here\n"
	.string "longer than I've been alive.\p"
	.string "Give their roots some room.\n"
	.string "They were on this path first.$"

IlexForest_EventScript_Npc11_Text:
	.string "I practice my steps here.\n"
	.string "The leaves are my audience.\p"
	.string "They rustle at every turn.\n"
	.string "I call that applause.$"

IlexForest_EventScript_Npc12_Text:
	.string "I tried counting all the trees.\n"
	.string "I ran out of numbers back there!\p"
	.string "Now I'm counting mushrooms.\n"
	.string "Don't tell me the answer!$"

IlexForest_EventScript_Sign1_Text:
	.string "ILEX FOREST\n"
	.string "Please stay on the worn path.$"

IlexForest_EventScript_Sign2_Text:
	.string "FOREST GUARDIAN'S SHRINE\n"
	.string "Please keep the clearing quiet.$"
