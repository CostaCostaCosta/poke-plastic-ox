Route4_hns_MapScripts::
	.byte 0

Route4_EventScript_Item1::
	finditem ITEM_POKE_BALL
	end

Route4_EventScript_Npc2::
	lock
	faceplayer
	msgbox Route4_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

Route4_EventScript_Npc3::
	lock
	faceplayer
	msgbox Route4_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

Route4_EventScript_Npc4::
	lock
	faceplayer
	msgbox Route4_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

Route4_EventScript_Item5::
	finditem ITEM_POKE_BALL
	end

Route4_EventScript_Npc6::
	lock
	faceplayer
	msgbox Route4_EventScript_Npc6_Text, MSGBOX_NPC
	release
	end

Route4_EventScript_Npc2_Text:
	.string "CERULEAN's east. BLACKTHORN's... also\nsort of east. Long story.$"

Route4_EventScript_Npc3_Text:
	.string "Everything east of here is new since\nlast spring. Even the mountains.$"

Route4_EventScript_Npc4_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route4_EventScript_Npc6_Text:
	.string "Mountains keep showing up where fields\nused to be. Good training though.$"
