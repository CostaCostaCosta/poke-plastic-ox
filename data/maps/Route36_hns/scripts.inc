Route36_hns_MapScripts::
	.byte 0

Route36_EventScript_Npc1::
	lock
	faceplayer
	msgbox Route36_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

Route36_EventScript_Npc2::
	lock
	faceplayer
	msgbox Route36_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

Route36_EventScript_Npc3::
	lock
	faceplayer
	msgbox Route36_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

Route36_EventScript_Npc4::
	lock
	faceplayer
	msgbox Route36_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

Route36_EventScript_Npc5::
	lock
	faceplayer
	msgbox Route36_EventScript_Npc5_Text, MSGBOX_NPC
	release
	end

Route36_EventScript_Portal4::
	warp MAP_ROUTE35_HNS, 17, 5
	waitstate
	end

Route36_EventScript_Portal5::
	warp MAP_NATIONAL_PARK_NORMAL_HNS, 40, 19
	waitstate
	end

Route36_EventScript_Portal6::
	warp MAP_NATIONAL_PARK_NORMAL_HNS, 40, 19
	waitstate
	end

Route36_EventScript_Npc1_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route36_EventScript_Npc2_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route36_EventScript_Npc3_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route36_EventScript_Npc4_Text:
	.string "There used to be a weird tree blocking the road. One day it just moved.$"

Route36_EventScript_Npc5_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"


Route36_EventScript_TEMPDIVE::
	warp MAP_ROUTE37_HNS, 13, 40
	waitstate
	end
Route36_EventScript_ReturnStone::
	warp MAP_PALLET_TOWN, 10, 4
	waitstate
	end
Route36_EventScript_ToJohto::
	warp MAP_SAFFRON_CITY_HNS, 29, 6
	waitstate
	end
