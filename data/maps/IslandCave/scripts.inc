IslandCave_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, IslandCave_OnTransition
	.byte 0

@ Plastic Ox: an empty side cave. Its Regi and sage now wait in the Ruins of
@ Alph (plastic_ox/alpha/ruins_of_alph.py), so the inner room is open and bare.
IslandCave_OnTransition:
	setflag FLAG_LANDMARK_ISLAND_CAVE
	end

IslandCave_EventScript_CaveEntranceMiddle::
IslandCave_EventScript_CaveEntranceSide::
	msgbox IslandCave_Text_OpenWall, MSGBOX_SIGN
	end

@ Still referenced by the vanilla braille step puzzle in field_control_avatar.c;
@ Plastic Ox never starts that puzzle, so it only needs to exist.
IslandCave_EventScript_OpenRegiEntrance::
	end

IslandCave_Text_OpenWall:
	.string "Meltwater drips where a slab once\n"
	.string "closed this wall. The room behind\p"
	.string "it is bare and damp.$"
