NationalPark_Normal_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_NationalPark_Normal_hns
	.byte 0

NationalPark_Normal_EventScript_Npc1::
	lock
	faceplayer
	msgbox NationalPark_Normal_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

NationalPark_Normal_EventScript_Npc3::
	lock
	faceplayer
	msgbox NationalPark_Normal_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

NationalPark_Normal_EventScript_Npc4::
	lock
	faceplayer
	msgbox NationalPark_Normal_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

NationalPark_Normal_EventScript_Npc5::
	lock
	faceplayer
	msgbox NationalPark_Normal_EventScript_Npc5_Text, MSGBOX_NPC
	release
	end

NationalPark_Normal_EventScript_Npc6::
	lock
	faceplayer
	msgbox NationalPark_Normal_EventScript_Npc6_Text, MSGBOX_NPC
	release
	end

NationalPark_Normal_EventScript_Npc7::
	lock
	faceplayer
	msgbox NationalPark_Normal_EventScript_Npc7_Text, MSGBOX_NPC
	release
	end

NationalPark_Normal_EventScript_Npc8::
	lock
	faceplayer
	msgbox NationalPark_Normal_EventScript_Npc8_Text, MSGBOX_NPC
	release
	end

NationalPark_Normal_EventScript_Npc9::
	lock
	faceplayer
	msgbox NationalPark_Normal_EventScript_Npc9_Text, MSGBOX_NPC
	release
	end

NationalPark_Normal_EventScript_Npc10::
	lock
	faceplayer
	msgbox NationalPark_Normal_EventScript_Npc10_Text, MSGBOX_NPC
	release
	end

NationalPark_Normal_EventScript_Npc11::
	lock
	faceplayer
	msgbox NationalPark_Normal_EventScript_Npc11_Text, MSGBOX_NPC
	release
	end

NationalPark_Normal_EventScript_Npc12::
	lock
	faceplayer
	msgbox NationalPark_Normal_EventScript_Npc12_Text, MSGBOX_NPC
	release
	end

NationalPark_Normal_EventScript_Npc1_Text:
	.string "Travelers from Goldenrod and\nEcruteak meet here.\pThe gardeners planted both\ncities' favorite flowers\paround the fountain.$"

NationalPark_Normal_EventScript_Npc2_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

NationalPark_Normal_EventScript_Npc3_Text:
	.string "I record bird calls on my\nlittle radio.\pAfter sundown, HOOTHOOT\nanswers from beyond the fence.$"

NationalPark_Normal_EventScript_Npc4_Text:
	.string "I teach my class beneath these\ntrees.\pThe children remember a real\ncaterpillar better than a\ppicture in a book.$"

NationalPark_Normal_EventScript_Npc5_Text:
	.string "My partner knows every shady\nbench in this park.$"

NationalPark_Normal_EventScript_Npc6_Text:
	.string "The gardeners leave fallen\nleaves where the bugs can\pshelter.$"

NationalPark_Normal_EventScript_Npc7_Text:
	.string "The flowerbeds draw different\nbugs as the seasons turn.$"

NationalPark_Normal_EventScript_Npc8_Text:
	.string "The park gives us room to slow\ndown and enjoy the day.$"

NationalPark_Normal_EventScript_Npc9_Text:
	.string "My husband helped plant this\ngrove when we were young.\pThose little saplings now\nshade our grandchildren.$"

NationalPark_Normal_EventScript_Npc10_Text:
	.string "A sturdy tree grows beside the\nfence.$"

NationalPark_Normal_EventScript_Npc11_Text:
	.string "Someone left supplies beside\nthe walking path.$"

NationalPark_Normal_EventScript_Npc12_Text:
	.string "A small keepsake lies beside\nthe flowerbeds.$"

NationalPark_EventScript_Beverly::
	trainerbattle_single TRAINER_PLASTIC_OX_JOHTO_BEVERLY, NationalPark_EventScript_Beverly_Intro, NationalPark_EventScript_Beverly_Defeat
	msgbox NationalPark_EventScript_Beverly_After, MSGBOX_AUTOCLOSE
	end
NationalPark_EventScript_Beverly_Intro:
	.string "A stroll and a battle keep my\npartners happy. Shall we?$"
NationalPark_EventScript_Beverly_Defeat:
	.string "We need a little rest!$"
NationalPark_EventScript_Beverly_After:
	.string "Goldenrod feels so busy after\nan afternoon here.\pMy Pokemon always vote for one\nmore lap.$"

NationalPark_EventScript_Jack::
	trainerbattle_single TRAINER_PLASTIC_OX_JOHTO_JACK, NationalPark_EventScript_Jack_Intro, NationalPark_EventScript_Jack_Defeat
	msgbox NationalPark_EventScript_Jack_After, MSGBOX_AUTOCLOSE
	end
NationalPark_EventScript_Jack_Intro:
	.string "My homework is to observe\nPokemon in action. Help me\pwith a battle!$"
NationalPark_EventScript_Jack_Defeat:
	.string "That was quite a lesson!$"
NationalPark_EventScript_Jack_After:
	.string "The fountain attracts birds,\nand the grass attracts bugs.\pA good field notebook needs\nboth.$"

NationalPark_EventScript_Krise::
	trainerbattle_single TRAINER_PLASTIC_OX_JOHTO_KRISE, NationalPark_EventScript_Krise_Intro, NationalPark_EventScript_Krise_Defeat
	msgbox NationalPark_EventScript_Krise_After, MSGBOX_AUTOCLOSE
	end
NationalPark_EventScript_Krise_Intro:
	.string "I came for the flowers, but my\nteam came for a challenge!$"
NationalPark_EventScript_Krise_Defeat:
	.string "You made us bloom!$"
NationalPark_EventScript_Krise_After:
	.string "The gardeners ask us to battle\naway from the flowerbeds.\pEven a small Pokemon can\nflatten a whole row.$"
