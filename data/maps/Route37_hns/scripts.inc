Route37_hns_MapScripts::
	.byte 0

Route37_EventScript_Npc1::
	lock
	faceplayer
	msgbox Route37_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

Route37_EventScript_Npc2::
	lock
	faceplayer
	msgbox Route37_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

Route37_EventScript_Npc3::
	lock
	faceplayer
	msgbox Route37_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

Route37_EventScript_Npc4::
	lock
	faceplayer
	msgbox Route37_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

Route37_EventScript_Npc1_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route37_EventScript_Npc2_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route37_EventScript_Npc3_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route37_EventScript_Npc4_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"









Route37_EventScript_PoxPortal12_18_39::
	warp MAP_ROUTE36_HNS, 16, 20
	waitstate
	end

Route37_EventScript_PoxPortal12_16_39::
	warp MAP_ECRUTEAK_CITY_HNS, 15, 33
	waitstate
	end

Route37_EventScript_PoxPortal14_18_39::
	warp MAP_ROUTE36_HNS, 16, 20
	waitstate
	end

Route37_EventScript_PoxPortal14_16_39::
	warp MAP_ECRUTEAK_CITY_HNS, 15, 33
	waitstate
	end
