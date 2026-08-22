PalletTown_PlayersHouse_1F_Frlg_MapScripts::
	.byte 0

PalletTown_PlayersHouse_1F_EventScript_Mom::
	lock
	faceplayer
	msgbox PalletTown_PlayersHouse_1F_Text_YouShouldTakeQuickRest
	closemessage
	call Common_EventScript_OutOfCenterPartyHeal
	msgbox PalletTown_PlayersHouse_1F_Text_LookingGreatTakeCare
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
