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
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route12_EventScript_Npc2_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route12_EventScript_Npc3_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route12_EventScript_Npc4_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route12_EventScript_Npc5_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route12_EventScript_Npc6_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route12_EventScript_Npc8_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route12_EventScript_Sign3_Text:
	.string "A sign from the old routes.$"

Route12_EventScript_Sign4_Text:
	.string "A sign from the old routes.$"

