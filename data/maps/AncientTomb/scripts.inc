AncientTomb_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, AncientTomb_OnTransition
	.byte 0

@ Plastic Ox: an empty side cave. Its Regi and sage now wait in the Ruins of
@ Alph (plastic_ox/alpha/ruins_of_alph.py), so the inner room is open and bare.
AncientTomb_OnTransition:
	setflag FLAG_LANDMARK_ANCIENT_TOMB
	end

AncientTomb_EventScript_CaveEntranceMiddle::
AncientTomb_EventScript_CaveEntranceSide::
	msgbox AncientTomb_Text_OpenWall, MSGBOX_SIGN
	end

AncientTomb_Text_OpenWall:
	.string "A metal plate has been slid back\n"
	.string "into the wall. Beyond it is an\p"
	.string "empty platform, swept clean.$"
