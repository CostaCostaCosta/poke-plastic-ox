PalletTown_PlayersHouse_1F_Frlg_MapScripts::
	.byte 0

PalletTown_PlayersHouse_1F_EventScript_Mom::
	lock
	faceplayer
	goto_if_eq VAR_POX_MOM_STATE, 0, PalletTown_Mom_FirstConversation
	goto_if_unset FLAG_POX_TRIGGERS_ENABLED, PalletTown_Mom_Rest
	goto_if_unset FLAG_POX_STORY_STARTER, PalletTown_Mom_BeforeStarter
PalletTown_Mom_Rest::
	msgbox PalletTown_PlayersHouse_1F_Text_YouShouldTakeQuickRest
	closemessage
	call Common_EventScript_OutOfCenterPartyHeal
	msgbox PalletTown_PlayersHouse_1F_Text_LookingGreatTakeCare
	release
	end

PalletTown_Mom_FirstConversation::
	setvar VAR_POX_MOM_STATE, 1
	msgbox PalletTown_Mom_Text_FirstConversation, MSGBOX_DEFAULT
	release
	end

PalletTown_PlayersHouse_1F_EventScript_TV::
	msgbox PalletTown_PlayersHouse_1F_Text_TV, MSGBOX_SIGN
	end

PalletTown_PlayersHouse_1F_Text_YouShouldTakeQuickRest::
	.string "MOM: You should take a quick rest.$"

PalletTown_PlayersHouse_1F_Text_LookingGreatTakeCare::
	.string "MOM: Looking great!\n"
	.string "Take care on your journey.$"

PalletTown_PlayersHouse_1F_Text_TV::
	.string "A travel program is showing roads\n"
	.string "that connect distant regions.$"

PalletTown_Mom_BeforeStarter::
	msgbox PalletTown_Mom_Text_Lab, MSGBOX_DEFAULT
	release
	end

PalletTown_Mom_Text_Lab::
	.string "MOM: Today's the day, {PLAYER}!\n"
	.string "PROFESSOR OAK is waiting at his lab.\p"
	.string "His friends ELM and BIRCH brought\n"
	.string "POKéMON for you to meet.\p"
	.string "The lab is southeast of our house.\n"
	.string "Come home whenever you need a rest!$"

PalletTown_Mom_Text_FirstConversation::
	.string "MOM: Look at you, ready for a big\n"
	.string "adventure!\p"
	.string "PROFESSOR OAK's lab is southeast\n"
	.string "of our house. ELM and BIRCH came\n"
	.string "all this way to see you, too.\p"
	.string "Come home whenever you need me.$"
