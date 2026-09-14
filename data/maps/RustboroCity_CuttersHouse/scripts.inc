RustboroCity_CuttersHouse_MapScripts::
	.byte 0

RustboroCity_CuttersHouse_EventScript_Cutter::
	lock
	faceplayer
	checkitem ITEM_CUT_KEY
	goto_if_eq VAR_RESULT, TRUE, RustboroCity_CuttersHouse_EventScript_ExplainCut
	msgbox RustboroCity_CuttersHouse_Text_YouCanPutThisHMToGoodUse, MSGBOX_DEFAULT
	giveitem ITEM_CUT_KEY
	goto_if_eq VAR_RESULT, FALSE, RustboroCity_CuttersHouse_EventScript_End
	setflag FLAG_RECEIVED_HM_CUT
	msgbox RustboroCity_CuttersHouse_Text_ExplainCut, MSGBOX_DEFAULT
RustboroCity_CuttersHouse_EventScript_End:
	release
	end

RustboroCity_CuttersHouse_EventScript_ExplainCut::
	msgbox RustboroCity_CuttersHouse_Text_ExplainCut, MSGBOX_DEFAULT
	release
	end

RustboroCity_CuttersHouse_EventScript_Lass::
	msgbox RustboroCity_CuttersHouse_Text_DadHelpedClearLandOfTrees, MSGBOX_NPC
	end

RustboroCity_CuttersHouse_Text_YouCanPutThisHMToGoodUse:
	.string "I'm the CUTTER! I help keep the\n"
	.string "paths around RUSTBORO clear.\p"
	.string "Take this CUT KEY. You can use\n"
	.string "it to clear thin trees yourself!$"

RustboroCity_CuttersHouse_Text_ExplainCut:
	.string "Face a thin tree and press A,\n"
	.string "or use the CUT KEY from your bag.\p"
	.string "You can use it right away! No\n"
	.string "BADGE or POKéMON move is needed.\p"
	.string "The tool can be used again and\n"
	.string "again, so keep it handy!$"

RustboroCity_CuttersHouse_Text_DadHelpedClearLandOfTrees:
	.string "When they were expanding the city of\n"
	.string "RUSTBORO, my dad helped out.\p"
	.string "He made his POKéMON use CUT to clear\n"
	.string "the land of trees.$"
