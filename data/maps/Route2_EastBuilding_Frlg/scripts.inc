Route2_EastBuilding_Frlg_MapScripts::
	.byte 0

Route2_EastBuilding_EventScript_Scientist::
	msgbox Route2_EastBuilding_Text_Scientist, MSGBOX_NPC
	end

Route2_EastBuilding_EventScript_Rocker::
	msgbox Route2_EastBuilding_Text_Rocker, MSGBOX_NPC
	end

Route2_EastBuilding_EventScript_Guard::
	msgbox Route2_EastBuilding_Text_Guard, MSGBOX_NPC
	end

Route2_EastBuilding_Text_Scientist::
	.string "I stop here to sort my notes\n"
	.string "out of the wind.\p"
	.string "A loose page can travel farther\n"
	.string "than the POKéMON it describes!$"

Route2_EastBuilding_Text_Rocker::
	.string "My boots sound great on the\n"
	.string "tiles, but not on that carpet.\p"
	.string "I'll spare the guard my next\n"
	.string "marching solo.$"

Route2_EastBuilding_Text_Guard::
	.string "Both doors lead to ROUTE 2.\n"
	.string "This is its eastern gate.\p"
	.string "You're welcome to rest here.\n"
	.string "Just keep the carpet clear.$"
