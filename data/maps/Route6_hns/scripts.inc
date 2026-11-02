Route6_hns_MapScripts::
	.byte 0

Route6_EventScript_Npc1::
	lock
	faceplayer
	msgbox Route6_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

Route6_EventScript_Npc2::
	lock
	faceplayer
	msgbox Route6_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

Route6_EventScript_Item3::
	finditem ITEM_POKE_BALL
	end

Route6_EventScript_Npc1_Text:
	.string "Travelers heading toward SAFFRON\noften stop here for a breather.$"

Route6_EventScript_Npc2_Text:
	.string "City noise fades quickly when\nyou walk into the grass.$"
