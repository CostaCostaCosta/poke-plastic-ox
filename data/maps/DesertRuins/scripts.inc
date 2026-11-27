DesertRuins_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, DesertRuins_OnTransition
	.byte 0

@ Plastic Ox: an empty side cave. Its Regi and sage now wait in the Ruins of
@ Alph (plastic_ox/alpha/ruins_of_alph.py), so the inner room is open and bare.
DesertRuins_OnTransition:
	setflag FLAG_LANDMARK_DESERT_RUINS
	end

DesertRuins_EventScript_CaveEntranceMiddle::
DesertRuins_EventScript_CaveEntranceSide::
	msgbox DesertRuins_Text_OpenWall, MSGBOX_SIGN
	end

DesertRuins_Text_OpenWall:
	.string "The stone that sealed this wall\n"
	.string "lies in pieces. Sand has drifted\p"
	.string "through into the room behind.$"
