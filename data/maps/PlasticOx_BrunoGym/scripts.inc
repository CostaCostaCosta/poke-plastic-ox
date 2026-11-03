PlasticOx_BrunoGym_MapScripts::
	.byte 0

PlasticOx_BrunoGym_EventScript_Greeter::
	lock
	faceplayer
	msgbox PlasticOx_BrunoGym_Text_Greeter, MSGBOX_DEFAULT
	specialvar VAR_RESULT, CheckSaffronGymOURules
	goto_if_eq VAR_RESULT, 1, PlasticOx_BrunoGym_EventScript_GreeterBannedMove
	goto_if_eq VAR_RESULT, 2, PlasticOx_BrunoGym_EventScript_GreeterBannedItem
	release
	end

PlasticOx_BrunoGym_EventScript_GreeterBannedMove::
	msgbox PlasticOx_BrunoGym_Text_GreeterBannedMove, MSGBOX_DEFAULT
	release
	end

PlasticOx_BrunoGym_EventScript_GreeterBannedItem::
	msgbox PlasticOx_BrunoGym_Text_GreeterBannedItem, MSGBOX_DEFAULT
	release
	end

PlasticOx_BrunoGym_Text_Greeter:
	.string "Yo! Champ in the making!\n"
	.string "Welcome to SAFFRON DOJO GYM.\p"
	.string "This GYM follows OU tier rules.\p"
	.string "Bring your best OU-tier POKéMON!$"

PlasticOx_BrunoGym_Text_GreeterBannedMove:
	.string "This GYM follows OU rules.\p"
	.string "That move is banned here.\n"
	.string "Please change it before entering.$"

PlasticOx_BrunoGym_Text_GreeterBannedItem:
	.string "This GYM follows OU rules.\p"
	.string "That item is banned here.\n"
	.string "Please remove it before entering.$"
