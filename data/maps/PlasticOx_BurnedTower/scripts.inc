PlasticOx_BurnedTower_MapScripts::
	.byte 0

PoxBurnedTower_Sage::
	goto_if_set FLAG_POX_STORY_BURNED_TOWER, PoxBurnedTower_SageAfter
	msgbox PoxBurnedTower_SageBeforeText, MSGBOX_NPC
	end

PoxBurnedTower_SageAfter::
	msgbox PoxBurnedTower_SageAfterText, MSGBOX_NPC
	end

PoxBurnedTower_SageBeforeText::
	.string "MORTY went down the ladder. He\nasked us to mind the old beams.$"

PoxBurnedTower_SageAfterText::
	.string "MORTY sent our sages across the\nregion to find and help the\plegendary POKéMON displaced by\nthe convergence.\pI will tend the tower while\nthey care for those POKéMON.$"

PoxBurnedTower_Memorial::
	msgbox PoxBurnedTower_MemorialText, MSGBOX_SIGN
	end

PoxBurnedTower_MemorialText::
	.string "A memorial to the tower before\nthe fire. Some names are lost.$"

PoxBurnedTower_FireStone::
	finditem ITEM_FIRE_STONE
	end

PoxBurnedTower_Ether::
	finditem ITEM_ETHER
	end
