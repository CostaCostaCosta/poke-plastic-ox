PlasticOx_BurnedTowerB1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxTower_InitGraphics
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

PoxTower_InitGraphics::
	setvar VAR_OBJ_GFX_ID_0, OBJ_EVENT_GFX_ENTEI
	setvar VAR_OBJ_GFX_ID_1, OBJ_EVENT_GFX_RAIKOU
	setvar VAR_OBJ_GFX_ID_2, OBJ_EVENT_GFX_SUICUNE
	end
