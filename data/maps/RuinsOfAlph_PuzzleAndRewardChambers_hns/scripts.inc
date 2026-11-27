RuinsOfAlph_PuzzleAndRewardChambers_hns_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, PoxRuins_Chambers_OnLoad
	.byte 0

@ Plastic Ox: a chamber's back wall opens only while the player carries its
@ tablet. No sliding puzzle, Unown report or fossil callbacks. The Regis and
@ their sages (PoxTournament_Regirock/_Regice/_Registeel) wait in the back rooms.
@ Behind each Regi is a floor hole down to a Words Room; it is solid in the
@ layout and opens here once that Regi is caught. The west chamber has no
@ Regi: its wall and its hole are always open.
PoxRuins_Chambers_OnLoad:
	checkitem ITEM_ANCIENT_ROCK_TABLET
	call_if_eq VAR_RESULT, TRUE, PoxRuins_Chambers_OpenRock
	checkitem ITEM_ANCIENT_STEEL_TABLET
	call_if_eq VAR_RESULT, TRUE, PoxRuins_Chambers_OpenSteel
	checkitem ITEM_ANCIENT_ICE_TABLET
	call_if_eq VAR_RESULT, TRUE, PoxRuins_Chambers_OpenIce
	call_if_set FLAG_POX_CAUGHT_REGIROCK, PoxRuins_Chambers_OpenRockHole
	call_if_set FLAG_POX_CAUGHT_REGISTEEL, PoxRuins_Chambers_OpenSteelHole
	call_if_set FLAG_POX_CAUGHT_REGICE, PoxRuins_Chambers_OpenIceHole
	end

@ 0x302/0x303 are the two halves of the floor hole.
PoxRuins_Chambers_OpenRockHole:
	setmetatile 20, 36, 0x302, FALSE
	setmetatile 21, 36, 0x303, FALSE
	return

PoxRuins_Chambers_OpenSteelHole:
	setmetatile 4, 53, 0x302, FALSE
	setmetatile 5, 53, 0x303, FALSE
	return

PoxRuins_Chambers_OpenIceHole:
	setmetatile 20, 53, 0x302, FALSE
	setmetatile 21, 53, 0x303, FALSE
	return

@ 0x308 is the writing tileset's open doorway.
PoxRuins_Chambers_OpenRock:
	setmetatile 21, 1, 0x308, FALSE
	return

PoxRuins_Chambers_OpenSteel:
	setmetatile 5, 18, 0x308, FALSE
	return

PoxRuins_Chambers_OpenIce:
	setmetatile 21, 18, 0x308, FALSE
	return

PoxRuins_RockWall::
	lockall
	checkitem ITEM_ANCIENT_ROCK_TABLET
	goto_if_eq VAR_RESULT, TRUE, PoxRuins_RockWallOpen
	msgbox PoxRuins_Text_RockSealed, MSGBOX_DEFAULT
	releaseall
	end

PoxRuins_RockWallOpen::
	msgbox PoxRuins_Text_RockOpen, MSGBOX_DEFAULT
	releaseall
	end

PoxRuins_Text_RockSealed:
	.string "Weathered stone seals the back\n"
	.string "wall. A tablet-shaped hollow is\p"
	.string "cut into it, rough as split\n"
	.string "boulder.$"

PoxRuins_Text_RockOpen:
	.string "The ANCIENT ROCK TABLET is heavy\n"
	.string "in your BAG. Grit has fallen\p"
	.string "away from an open doorway.$"

PoxRuins_SteelWall::
	lockall
	checkitem ITEM_ANCIENT_STEEL_TABLET
	goto_if_eq VAR_RESULT, TRUE, PoxRuins_SteelWallOpen
	msgbox PoxRuins_Text_SteelSealed, MSGBOX_DEFAULT
	releaseall
	end

PoxRuins_SteelWallOpen::
	msgbox PoxRuins_Text_SteelOpen, MSGBOX_DEFAULT
	releaseall
	end

PoxRuins_Text_SteelSealed:
	.string "A dark metal plate seals the back\n"
	.string "wall. At its center is a polished\p"
	.string "recess the size of a tablet.$"

PoxRuins_Text_SteelOpen:
	.string "The ANCIENT STEEL TABLET rings\n"
	.string "faintly in the BAG. The metal\p"
	.string "plate has slid aside.$"

PoxRuins_IceWall::
	lockall
	checkitem ITEM_ANCIENT_ICE_TABLET
	goto_if_eq VAR_RESULT, TRUE, PoxRuins_IceWallOpen
	msgbox PoxRuins_Text_IceSealed, MSGBOX_DEFAULT
	releaseall
	end

PoxRuins_IceWallOpen::
	msgbox PoxRuins_Text_IceOpen, MSGBOX_DEFAULT
	releaseall
	end

PoxRuins_Text_IceSealed:
	.string "A slab of frozen stone seals the\n"
	.string "back wall. Frost rims a hollow\p"
	.string "shaped like a tablet.$"

PoxRuins_Text_IceOpen:
	.string "The ANCIENT ICE TABLET is cold\n"
	.string "even through the BAG. The frost\p"
	.string "has drawn back from the doorway.$"

PoxRuins_PanelNorth::
	msgbox PoxRuins_Text_PanelNorth, MSGBOX_SIGN
	end

PoxRuins_Text_PanelNorth:
	.string "A panel of sliding stone tiles.\n"
	.string "The pieces are worn smooth and\p"
	.string "no longer move.$"

PoxRuins_PanelWest::
	msgbox PoxRuins_Text_PanelWest, MSGBOX_SIGN
	end

PoxRuins_Text_PanelWest:
	.string "A tile panel under a dust sheet.\n"
	.string "The tag on it reads DO NOT SLIDE.$"

PoxRuins_PanelSouthWest::
	msgbox PoxRuins_Text_PanelSouthWest, MSGBOX_SIGN
	end

PoxRuins_Text_PanelSouthWest:
	.string "A tile panel. Someone has chalked\n"
	.string "a survey number on every piece.$"

PoxRuins_PanelSouthEast::
	msgbox PoxRuins_Text_PanelSouthEast, MSGBOX_SIGN
	end

PoxRuins_Text_PanelSouthEast:
	.string "Stone tiles set in a frame. Most\n"
	.string "of the picture has flaked away.$"
