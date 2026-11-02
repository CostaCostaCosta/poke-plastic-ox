PalletTown_Frlg_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_PalletTown_Frlg
	.byte 0

PalletTown_SurfToRoute21::
	warp MAP_ROUTE21_NORTH, 7, 1
	waitstate
	end

PalletTown_EventScript_FatMan::
	msgbox PalletTown_Text_FatMan, MSGBOX_NPC
	end

PalletTown_EventScript_SignLady::
	msgbox PalletTown_Text_SignLady, MSGBOX_NPC
	end

PalletTown_EventScript_ProfOakTeam::
	lock
	faceplayer
	msgbox PalletTown_Text_ProfOakTeam, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, PalletTown_EventScript_ProfOakTeamDeclined
	special GivePlasticOxPlayerParty
	msgbox PalletTown_Text_ProfOakTeamGiven, MSGBOX_DEFAULT
	release
	end

PalletTown_EventScript_ProfOakTeamDeclined::
	msgbox PalletTown_Text_ProfOakTeamDeclined, MSGBOX_DEFAULT
	release
	end

PalletTown_EventScript_OaksLabSign::
	msgbox PalletTown_Text_OaksLabSign, MSGBOX_SIGN
	end

PalletTown_EventScript_PlayersHouseSign::
	msgbox PalletTown_Text_PlayersHouseSign, MSGBOX_SIGN
	end

PalletTown_EventScript_RivalsHouseSign::
	msgbox PalletTown_Text_RivalsHouseSign, MSGBOX_SIGN
	end

PalletTown_EventScript_TownSign::
	msgbox PalletTown_Text_TownSign, MSGBOX_SIGN
	end

PalletTown_EventScript_TrainerTips::
	msgbox PalletTown_Text_TrainerTips, MSGBOX_SIGN
	end

PalletTown_Text_FatMan::
	.string "Technology is incredible!\p"
	.string "A POKéDEX can record every POKéMON\n"
	.string "you meet on your travels.$"

PalletTown_Text_SignLady::
	.string "PROFESSORS ELM and BIRCH are visiting\n"
	.string "OAK at his lab.\p"
	.string "Three professors in our little town!\n"
	.string "They seem excited about something.$"

PalletTown_Text_ProfOakTeam::
	.string "OAK: Before you head to LANCE, I've\n"
	.string "prepared an ADV OU team for you.\p"
	.string "Would you like to receive it?$"

PalletTown_Text_ProfOakTeamGiven::
	.string "OAK: Your team is ready: SKARMORY,\n"
	.string "BLISSEY, CLAYDOL, DUGTRIO, GENGAR,\n"
	.string "and SUICUNE. Good luck!$"

PalletTown_Text_ProfOakTeamDeclined::
	.string "OAK: I'll wait here outside your house.$"

PalletTown_Text_OaksLabSign::
	.string "OAK POKéMON RESEARCH LAB$"

PalletTown_Text_PlayersHouseSign::
	.string "{PLAYER}'s house$"

PalletTown_Text_RivalsHouseSign::
	.string "DAISY and BLUE's house$"

PalletTown_Text_TownSign::
	.string "PALLET TOWN\n"
	.string "Shades of your journey await!$"

PalletTown_Text_TrainerTips::
	.string "TRAINER TIPS\p"
	.string "Head north to reach ROUTE 101.$"
