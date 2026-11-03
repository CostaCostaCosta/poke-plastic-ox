PlasticOx_BlaineGym_MapScripts::
	.byte 0

PlasticOx_BlaineGym_EventScript_Greeter::
	lock
	faceplayer
	msgbox PlasticOx_BlaineGym_Text_Greeter, MSGBOX_DEFAULT
	specialvar VAR_RESULT, CheckCinnabarGymUURules
	goto_if_eq VAR_RESULT, 1, PlasticOx_BlaineGym_EventScript_GreeterBannedMove
	goto_if_eq VAR_RESULT, 2, PlasticOx_BlaineGym_EventScript_GreeterBannedItem
	release
	end

PlasticOx_BlaineGym_EventScript_GreeterBannedMove::
	msgbox PlasticOx_BlaineGym_Text_GreeterBannedMove, MSGBOX_DEFAULT
	release
	end

PlasticOx_BlaineGym_EventScript_GreeterBannedItem::
	msgbox PlasticOx_BlaineGym_Text_GreeterBannedItem, MSGBOX_DEFAULT
	release
	end

PlasticOx_BlaineGym_Text_Greeter:
	.string "Yo! Champ in the making!\n"
	.string "Welcome to CINNABAR GYM.\p"
	.string "This GYM follows UU tier rules.\p"
	.string "Bring your best UU-tier POKéMON!$"

PlasticOx_BlaineGym_Text_GreeterBannedMove:
	.string "This GYM follows UU rules.\p"
	.string "That move is banned here.\n"
	.string "Please change it before entering.$"

PlasticOx_BlaineGym_Text_GreeterBannedItem:
	.string "This GYM follows UU rules.\p"
	.string "That item is banned here.\n"
	.string "Please remove it before entering.$"
