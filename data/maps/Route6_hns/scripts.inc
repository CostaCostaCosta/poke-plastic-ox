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
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route6_EventScript_Npc2_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"
Route6_EventScript_P41_6::
	warp MAP_SAFFRON_CITY_HNS, 29, 6
	waitstate
	end
