Route7_hns_MapScripts::
	.byte 0

Route7_EventScript_Sign1::
	msgbox Route7_EventScript_Sign1_Text, MSGBOX_SIGN
	end

Route7_EventScript_Sign2::
	msgbox Route7_EventScript_Sign2_Text, MSGBOX_SIGN
	end

Route7_EventScript_Sign1_Text:
	.string "A sign from the old routes.$"

Route7_EventScript_Sign2_Text:
	.string "A sign from the old routes.$"


Route7_EventScript_PoxPortal12_2_25::
	warp MAP_ROUTE24_HNS, 10, 3
	waitstate
	end

Route7_EventScript_PoxPortal12_4_22::
	warp MAP_LAVENDER_TOWN_HNS, 1, 10
	waitstate
	end

Route7_EventScript_PoxPortal12_5_25::
	warp MAP_ECRUTEAK_CITY_HNS, 15, 31
	waitstate
	end
