PlasticOx_WhitneyGym_MapScripts::
	.byte 0

PlasticOx_WhitneyGym_EventScript_Greeter::
	lock
	faceplayer
	msgbox PlasticOx_WhitneyGym_Text_Greeter, MSGBOX_DEFAULT
	specialvar VAR_RESULT, CheckGoldenrodGymPURules
	goto_if_eq VAR_RESULT, 1, PlasticOx_WhitneyGym_EventScript_GreeterBannedMove
	goto_if_eq VAR_RESULT, 2, PlasticOx_WhitneyGym_EventScript_GreeterBannedItem
	release
	end

PlasticOx_WhitneyGym_EventScript_GreeterBannedMove::
	msgbox PlasticOx_WhitneyGym_Text_GreeterBannedMove, MSGBOX_DEFAULT
	release
	end

PlasticOx_WhitneyGym_EventScript_GreeterBannedItem::
	msgbox PlasticOx_WhitneyGym_Text_GreeterBannedItem, MSGBOX_DEFAULT
	release
	end

PlasticOx_WhitneyGym_Text_Greeter:
	.string "Yo! Champ in the making!\n"
	.string "Welcome to GOLDENROD GYM.\p"
	.string "This GYM follows PU tier rules.\p"
	.string "Bring your best PU-tier POKéMON!$"

PlasticOx_WhitneyGym_Text_GreeterBannedMove:
	.string "This GYM follows PU rules.\p"
	.string "That move is banned here.\n"
	.string "Please change it before entering.$"

PlasticOx_WhitneyGym_Text_GreeterBannedItem:
	.string "This GYM follows PU rules.\p"
	.string "That item is banned here.\n"
	.string "Please remove it before entering.$"
