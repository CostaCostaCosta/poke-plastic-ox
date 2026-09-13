Route7_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_Route7_hns
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
