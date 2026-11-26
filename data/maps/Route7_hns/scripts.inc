Route7_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_Route7_hns
	.byte 0

Route7_EventScript_Sign1::
	msgbox Route7_EventScript_Sign1_Text, MSGBOX_SIGN
	end

Route7_EventScript_Sign1_Text:
	.string "UNDERGROUND PATH\nROUTE 7 - ROUTE 8$"
