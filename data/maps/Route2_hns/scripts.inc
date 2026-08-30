Route2_hns_MapScripts::
	.byte 0

Route2_EventScript_Item1::
	finditem ITEM_POKE_BALL
	end

Route2_EventScript_Item5::
	finditem ITEM_POKE_BALL
	end

Route2_EventScript_Sign2::
	msgbox Route2_EventScript_Sign2_Text, MSGBOX_SIGN
	end

Route2_EventScript_Sign3::
	msgbox Route2_EventScript_Sign3_Text, MSGBOX_SIGN
	end

Route2_EventScript_Npc2_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route2_EventScript_Npc3_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route2_EventScript_Npc4_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route2_EventScript_Npc6_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route2_EventScript_Npc7_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

Route2_EventScript_Sign2_Text:
	.string "ROUTE 2\nVIRIDIAN FOREST ahead. Probably.$"

Route2_EventScript_Sign3_Text:
	.string "ROUTE 2\nSouth: RUSTBORO CITY. Yes, really.$"
