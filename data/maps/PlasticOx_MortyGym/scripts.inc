PlasticOx_MortyGym_MapScripts::
	.byte 0

PlasticOx_MortyGym_EventScript_Greeter::
	lock
	faceplayer
	msgbox PlasticOx_MortyGym_Text_Greeter, MSGBOX_DEFAULT
	specialvar VAR_RESULT, CheckEcruteakGymNURules
	goto_if_eq VAR_RESULT, 1, PlasticOx_MortyGym_EventScript_GreeterBannedMove
	goto_if_eq VAR_RESULT, 2, PlasticOx_MortyGym_EventScript_GreeterBannedItem
	goto_if_eq VAR_RESULT, 3, PlasticOx_MortyGym_EventScript_GreeterBannedSpecies
	release
	end

PlasticOx_MortyGym_EventScript_GreeterBannedMove::
	msgbox PlasticOx_MortyGym_Text_GreeterBannedMove, MSGBOX_DEFAULT
	release
	end

PlasticOx_MortyGym_EventScript_GreeterBannedItem::
	msgbox PlasticOx_MortyGym_Text_GreeterBannedItem, MSGBOX_DEFAULT
	release
	end

PlasticOx_MortyGym_EventScript_GreeterBannedSpecies::
	msgbox PlasticOx_MortyGym_Text_GreeterBannedSpecies, MSGBOX_DEFAULT
	release
	end

PlasticOx_MortyGym_Text_Greeter:
	.string "Yo! Champ in the making!\n"
	.string "Welcome to ECRUTEAK GYM.\p"
	.string "This GYM follows NU tier rules.\p"
	.string "Bring your best NU-tier POKéMON!$"

PlasticOx_MortyGym_Text_GreeterBannedMove:
	.string "This GYM follows NU rules.\p"
	.string "That move is banned here.\n"
	.string "Please change it before entering.$"

PlasticOx_MortyGym_Text_GreeterBannedItem:
	.string "This GYM follows NU rules.\p"
	.string "That item is banned here.\n"
	.string "Please remove it before entering.$"

PlasticOx_MortyGym_Text_GreeterBannedSpecies:
	.string "This GYM follows NU rules.\p"
	.string "{STR_VAR_1} is a {STR_VAR_2}.\p"
	.string "That POKéMON is over the tier.\n"
	.string "Please leave it in the PC.$"
