Route25_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_Route25_hns
	.byte 0

Route25_EventScript_Npc1::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE25_DUDLEY, Route25_DudleyChallenge_Text, Route25_DudleyDefeat_Text
	msgbox Route25_EventScript_Npc1_Text, MSGBOX_AUTOCLOSE
	end

Route25_EventScript_Npc2::
	lock
	faceplayer
	msgbox Route25_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

Route25_EventScript_Npc3::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE25_JOE, Route25_JoeChallenge_Text, Route25_JoeDefeat_Text
	msgbox Route25_EventScript_Npc3_Text, MSGBOX_AUTOCLOSE
	end

Route25_EventScript_Npc4::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE25_LAURA, Route25_LauraChallenge_Text, Route25_LauraDefeat_Text
	msgbox Route25_EventScript_Npc4_Text, MSGBOX_AUTOCLOSE
	end

Route25_EventScript_Npc5::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE25_LLOYD, Route25_LloydChallenge_Text, Route25_LloydDefeat_Text
	msgbox Route25_EventScript_Npc5_Text, MSGBOX_AUTOCLOSE
	end

Route25_EventScript_Npc6::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE25_ELLEN, Route25_EllenChallenge_Text, Route25_EllenDefeat_Text
	msgbox Route25_EventScript_Npc6_Text, MSGBOX_AUTOCLOSE
	end

Route25_EventScript_Npc7::
	lock
	faceplayer
	msgbox Route25_EventScript_Npc7_Text, MSGBOX_NPC
	release
	end

Route25_EventScript_Npc8::
	lock
	faceplayer
	msgbox Route25_EventScript_Npc8_Text, MSGBOX_NPC
	release
	end

Route25_EventScript_Npc9::
	lock
	faceplayer
	msgbox Route25_EventScript_Npc9_Text, MSGBOX_NPC
	release
	end

Route25_EventScript_Npc10::
	lock
	faceplayer
	msgbox Route25_EventScript_Npc10_Text, MSGBOX_NPC
	release
	end

Route25_EventScript_Npc11::
	lock
	faceplayer
	msgbox Route25_EventScript_Npc11_Text, MSGBOX_NPC
	release
	end

Route25_EventScript_Npc12::
	lock
	faceplayer
	msgbox Route25_EventScript_Npc12_Text, MSGBOX_NPC
	release
	end

Route25_EventScript_Npc1_Text:
	.string "I counted every turn from the\nbridge. Then I lost count.\pOn the way back, I'm counting\nwith pebbles in my pocket.$"

Route25_EventScript_Npc2_Text:
	.string "The cape is my favorite spot\nfor a walk with my POKéMON.$"

Route25_EventScript_Npc3_Text:
	.string "I came up from ROUTE 24 with\nmy shoelace dragging.\pMy POKéMON kept stepping on it.\nI thought it wanted a battle!$"

Route25_EventScript_Npc4_Text:
	.string "We practice turns together.\nI turn left, my POKéMON follows.\pIt spotted a bug once\nand left me marching alone.$"

Route25_EventScript_Npc5_Text:
	.string "I packed lunch for the cape.\nMy POKéMON packed an appetite.\pNext time, I'm bringing enough\nfor two lunches each.$"

Route25_EventScript_Npc6_Text:
	.string "My son says a walk is boring.\nThen he races ahead at each turn.\pI wish he'd lend me some of\nthat energy for the trip home.$"

Route25_EventScript_Npc7_Text:
	.string "The little tree's branches\nrustle in the breeze.$"

Route25_EventScript_Npc8_Text:
	.string "I stop here after training.\nA quiet walk settles my team.\pThey still race me to the cape.\nApparently, that doesn't count.$"

Route25_EventScript_Npc9_Text:
	.string "Look at that water sparkle!\nI'd stay here all afternoon.\pDon't tell me the time.\nI'm enjoying not knowing.$"

Route25_EventScript_Npc10_Text:
	.string "I practiced a clever greeting\nall the way up here.\pThen I said, 'Nice water.'\nThat was the whole greeting.$"

Route25_EventScript_Npc11_Text:
	.string "A fine place to take the air!\nI wore my best shoes for it.\pA little dust never hurt them.\nAt least, I hope it hasn't.$"

Route25_EventScript_Npc12_Text:
	.string "BILL's grandfather is looking\nafter the cottage while he's out.\pHe was brushing an EEVEE when\nI visited. There was fur on him!$"

Route25_EventScript_Pat::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE25_PAT, Route25_PatChallenge_Text, Route25_PatDefeat_Text
	msgbox Route25_EventScript_Pat_Text, MSGBOX_AUTOCLOSE
	end

Route25_DudleyChallenge_Text::
	.string "I counted every bend on this\nroute. Now I'll count your turns!$"

Route25_DudleyDefeat_Text::
	.string "I lost count again!$"

Route25_JoeChallenge_Text::
	.string "My POKéMON tripped me once.\nLet's see how they battle!$"

Route25_JoeDefeat_Text::
	.string "At least I stayed on my feet!$"

Route25_LauraChallenge_Text::
	.string "One step at a time. Show me\nhow you lead your POKéMON!$"

Route25_LauraDefeat_Text::
	.string "Your team kept perfect pace.$"

Route25_LloydChallenge_Text::
	.string "I brought lunch for the cape.\nFirst, let's work up an appetite!$"

Route25_LloydDefeat_Text::
	.string "Now I really need that lunch.$"

Route25_EllenChallenge_Text::
	.string "My son ran ahead again.\nKeep me company with a battle!$"

Route25_EllenDefeat_Text::
	.string "You have his energy, too!$"

Route25_PatChallenge_Text::
	.string "I've been studying the POKéMON\nhere. Let's test my notes!$"

Route25_PatDefeat_Text::
	.string "Back to the notebook, then.$"

Route25_EventScript_Pat_Text::
	.string "I study the POKéMON here\nbetween battles.$"
