RustboroCity_Flat2_3F_MapScripts::
	.byte 0

RustboroCity_Flat2_3F_EventScript_DevonEmployee::
	lock
	faceplayer
	goto_if_set FLAG_POX_RUSTBORO_CHOICE_BAND, RustboroCity_Flat2_3F_EventScript_GaveChoiceBand
	msgbox RustboroCity_Flat2_3F_Text_ChoiceBandGift, MSGBOX_DEFAULT
	giveitem ITEM_CHOICE_BAND
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_POX_RUSTBORO_CHOICE_BAND
	release
	end

RustboroCity_Flat2_3F_EventScript_GaveChoiceBand::
	msgbox RustboroCity_Flat2_3F_Text_ChoiceBandAdvice, MSGBOX_DEFAULT
	release
	end

RustboroCity_Flat2_3F_EventScript_Woman::
	msgbox RustboroCity_Flat2_3F_Text_PresidentsSonAlsoCollectsRareStones, MSGBOX_NPC
	end

RustboroCity_Flat2_3F_Text_ChoiceBandGift:
	.string "I work for DEVON, and we made this\n"
	.string "CHOICE BAND for serious trainers.\p"
	.string "It boosts a POKéMON's power, but\n"
	.string "locks it into one move. Take it!$"

RustboroCity_Flat2_3F_Text_ChoiceBandAdvice:
	.string "That CHOICE BAND is powerful, but\n"
	.string "choose your first move carefully!$"

RustboroCity_Flat2_3F_Text_PresidentsSonAlsoCollectsRareStones:
	.string "I think the PRESIDENT's son also\n"
	.string "collects rare stones.$"
