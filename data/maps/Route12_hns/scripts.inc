Route12_hns_MapScripts::
	.byte 0

Route12_EventScript_Npc1::
	lock
	faceplayer
	msgbox Route12_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

Route12_EventScript_Npc2::
	lock
	faceplayer
	msgbox Route12_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

Route12_EventScript_Npc3::
	lock
	faceplayer
	msgbox Route12_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

Route12_EventScript_Npc4::
	lock
	faceplayer
	msgbox Route12_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

Route12_EventScript_Npc5::
	lock
	faceplayer
	msgbox Route12_EventScript_Npc5_Text, MSGBOX_NPC
	release
	end

Route12_EventScript_Npc6::
	lock
	faceplayer
	msgbox Route12_EventScript_Npc6_Text, MSGBOX_NPC
	release
	end

Route12_EventScript_Item7::
	finditem ITEM_POKE_BALL
	end

Route12_EventScript_Npc8::
	lock
	faceplayer
	msgbox Route12_EventScript_Npc8_Text, MSGBOX_NPC
	release
	end

Route12_EventScript_Item9::
	finditem ITEM_POKE_BALL
	end

Route12_EventScript_Sign3::
	msgbox Route12_EventScript_Sign3_Text, MSGBOX_SIGN
	end

Route12_EventScript_Sign4::
	msgbox Route12_EventScript_Sign4_Text, MSGBOX_SIGN
	end

Route12_EventScript_Npc1_Text:
	.string "Fishing takes patience. Watch\nyour line, not the clock.$"

Route12_EventScript_Npc2_Text:
	.string "The water brings a cool breeze\nalong this path.$"

Route12_EventScript_Npc3_Text:
	.string "I've fished this bank since\ndawn. Two MAGIKARP and a sunburn\pso far.$"

Route12_EventScript_Npc4_Text:
	.string "The boardwalk planks creak when\nthe tide comes in. Keeps the\pfish nervous, I reckon.$"

Route12_EventScript_Npc5_Text:
	.string "I swap bait tips with the\nfellows up the pier. Nobody ever\padmits what they really use.$"

Route12_EventScript_Npc6_Text:
	.string "A slender tree leans out over\nthe water. Its roots grip the\pbank.$"

Route12_EventScript_Npc8_Text:
	.string "A tangle of fishing line hangs\nin this tree. Somebody's lost\plure dangles from a branch.$"

Route12_EventScript_Sign3_Text:
	.string "A sign from the old routes.$"

Route12_EventScript_Sign4_Text:
	.string "A sign from the old routes.$"

