PlasticOx_BrunoGym_MapScripts::
	.byte 0

PlasticOx_BrunoGym_EventScript_Greeter::
	lock
	faceplayer
	msgbox PlasticOx_BrunoGym_Text_Greeter, MSGBOX_DEFAULT
	specialvar VAR_RESULT, CheckSaffronGymOURules
	goto_if_eq VAR_RESULT, 1, PlasticOx_BrunoGym_EventScript_GreeterBannedMove
	goto_if_eq VAR_RESULT, 2, PlasticOx_BrunoGym_EventScript_GreeterBannedItem
	goto_if_eq VAR_RESULT, 3, PlasticOx_BrunoGym_EventScript_GreeterBannedSpecies
	goto_if_eq VAR_RESULT, 4, PlasticOx_BrunoGym_EventScript_GreeterDuplicate
	goto_if_eq VAR_RESULT, 5, PlasticOx_BrunoGym_EventScript_GreeterBannedAbility
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

PlasticOx_BrunoGym_EventScript_GreeterBannedSpecies::
	msgbox PlasticOx_BrunoGym_Text_GreeterBannedSpecies, MSGBOX_DEFAULT
	release
	end

PlasticOx_BrunoGym_EventScript_GreeterDuplicate::
	msgbox PlasticOx_BrunoGym_Text_GreeterDuplicate, MSGBOX_DEFAULT
	release
	end

PlasticOx_BrunoGym_EventScript_GreeterBannedAbility::
	msgbox PlasticOx_BrunoGym_Text_GreeterBannedAbility, MSGBOX_DEFAULT
	release
	end

PlasticOx_BrunoGym_Text_Greeter:
	.string "Yo! Champ in the making!\n"
	.string "Welcome to SAFFRON DOJO GYM.\p"
	.string "This GYM follows OU tier rules.\p"
	.string "Bring your best OU-tier POKéMON!$"

PlasticOx_BrunoGym_Text_GreeterBannedMove:
	.string "SAFFRON DOJO GYM uses OU rules.\p"
	.string "That move is banned here.\n"
	.string "Please change it before entering.$"

PlasticOx_BrunoGym_Text_GreeterBannedItem:
	.string "SAFFRON DOJO GYM uses OU rules.\p"
	.string "That item is banned here.\n"
	.string "Please remove it before entering.$"

PlasticOx_BrunoGym_Text_GreeterBannedSpecies:
	.string "SAFFRON DOJO GYM uses OU rules.\p"
	.string "{STR_VAR_1} is a {STR_VAR_2}.\p"
	.string "That POKéMON is over the tier.\n"
	.string "Please leave it in the PC.$"

PlasticOx_BrunoGym_Text_GreeterDuplicate:
	.string "SAFFRON DOJO GYM uses OU rules.\p"
	.string "{STR_VAR_1} is a second {STR_VAR_2}.\p"
	.string "Only one of each POKéMON.\n"
	.string "Please leave one in the PC.$"

PlasticOx_BrunoGym_Text_GreeterBannedAbility:
	.string "SAFFRON DOJO GYM uses OU rules.\p"
	.string "{STR_VAR_1} has {STR_VAR_2}.\p"
	.string "That ability is banned here.\n"
	.string "Please leave it in the PC.$"
