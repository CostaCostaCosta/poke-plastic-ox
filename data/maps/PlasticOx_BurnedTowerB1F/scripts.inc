PlasticOx_BurnedTowerB1F_MapScripts::
	.byte 0

PoxBurnedTower_AssembledSage::
	msgbox PoxBurnedTower_AssembledSageText, MSGBOX_NPC
	end

PoxBurnedTower_AssembledSageText::
	.string "We came to speak with MORTY.\n"
	.string "There are reports of legendary\p"
	.string "POKéMON far from their homes.\n"
	.string "They must be frightened.$"

PoxBurnedTower_UltraBall::
	finditem ITEM_ULTRA_BALL
	end

PoxBurnedTower_TM12::
	finditem ITEM_TM12
	end
