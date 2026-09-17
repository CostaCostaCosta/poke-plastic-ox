Route2_House_Frlg_MapScripts::
	.byte 0

Route2_House_EventScript_MrMimeTrade::
	lock
	faceplayer
	setvar VAR_0x8008, INGAME_TRADE_MR_MIME
	call EventScript_GetInGameTradeSpeciesInfo
	goto_if_set FLAG_DID_MIMIEN_TRADE, Route2_House_EventScript_AlreadyTraded
	msgbox Route2_House_Text_OfferTrade, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route2_House_EventScript_Declined
	call EventScript_ChooseMonForInGameTrade
	goto_if_ge VAR_0x8004, PARTY_SIZE, Route2_House_EventScript_Declined
	call EventScript_GetInGameTradeSpecies
	goto_if_ne VAR_RESULT, VAR_0x8009, Route2_House_EventScript_WrongPokemon
	call EventScript_DoInGameTrade
	msgbox Route2_House_Text_Thanks
	setflag FLAG_DID_MIMIEN_TRADE
	release
	end

Route2_House_EventScript_Declined::
	msgbox Route2_House_Text_Declined
	release
	end

Route2_House_EventScript_WrongPokemon::
	bufferspeciesname STR_VAR_1, VAR_0x8009
	msgbox Route2_House_Text_WrongPokemon
	release
	end

Route2_House_EventScript_AlreadyTraded::
	msgbox Route2_House_Text_AlreadyTraded
	release
	end

Route2_House_Text_OfferTrade::
	.string "I'm looking for a {STR_VAR_1}!\p"
	.string "Would you trade one for my\n"
	.string "{STR_VAR_2}?$"

Route2_House_Text_Thanks::
	.string "Thanks! Take good care of MIMIEN.$"

Route2_House_Text_Declined::
	.string "Come back if you find a STANTLER.$"

Route2_House_Text_WrongPokemon::
	.string "That's not a {STR_VAR_1}. Think of me\n"
	.string "if you catch one.$"

Route2_House_Text_AlreadyTraded::
	.string "How is my {STR_VAR_2} doing?$"
