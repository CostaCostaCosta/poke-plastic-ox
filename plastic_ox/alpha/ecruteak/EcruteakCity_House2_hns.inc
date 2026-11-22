EcruteakCity_House2_hns_MapScripts::
	.byte 0

PoxEcruteak_EcruteakCity_House2_hns_0::
	lock
	faceplayer
	msgbox PoxEcruteak_EcruteakCity_House2_hns_0_Text, MSGBOX_NPC
	release
	end
PoxEcruteak_EcruteakCity_House2_hns_0_Text:
	.string "Every book in this house is about\nECRUTEAK or the tower that burned\pdown.\pMy grandmother wrote one of them.\nShe got the year wrong and never\pforgave herself.$"

PoxEcruteak_EcruteakCity_House2_hns_Sign0::
	msgbox PoxEcruteak_EcruteakCity_House2_hns_Sign0_Text, MSGBOX_SIGN
	end
PoxEcruteak_EcruteakCity_House2_hns_Sign0_Text:
	.string "A book about ECRUTEAK history,\nworn soft.\pThe margin notes are in two\ndifferent hands.$"

PoxEcruteak_EcruteakCity_House2_hns_Sign1::
	msgbox PoxEcruteak_EcruteakCity_House2_hns_Sign1_Text, MSGBOX_SIGN
	end
PoxEcruteak_EcruteakCity_House2_hns_Sign1_Text:
	.string "A book about the tower,\nwater-damaged.\pSomeone has pressed a chestnut\nleaf between the pages.$"

PoxEcruteak_EcruteakCity_House2_hns_Trader::
	lock
	faceplayer
	goto_if_set FLAG_POX_ECRUTEAK_RELICANTH_TRADE, PoxEcruteak_EcruteakCity_House2_hns_TradeDone
	ingame_trade INGAME_TRADE_RELICANTH, PoxEcruteak_EcruteakCity_House2_hns_Text_WantTrade, PoxEcruteak_EcruteakCity_House2_hns_TradeDecline, PoxEcruteak_EcruteakCity_House2_hns_TradeWrongMon, PoxEcruteak_EcruteakCity_House2_hns_Text_TradeComplete
	setflag FLAG_POX_ECRUTEAK_RELICANTH_TRADE
	release
	end

PoxEcruteak_EcruteakCity_House2_hns_TradeDecline::
	msgbox PoxEcruteak_EcruteakCity_House2_hns_Text_TradeDecline, MSGBOX_DEFAULT
	release
	end

PoxEcruteak_EcruteakCity_House2_hns_TradeWrongMon::
	bufferspeciesname STR_VAR_1, VAR_0x8009
	msgbox PoxEcruteak_EcruteakCity_House2_hns_Text_TradeWrongMon, MSGBOX_DEFAULT
	release
	end

PoxEcruteak_EcruteakCity_House2_hns_TradeDone::
	msgbox PoxEcruteak_EcruteakCity_House2_hns_Text_TradeDone, MSGBOX_DEFAULT
	release
	end

PoxEcruteak_EcruteakCity_House2_hns_Text_WantTrade:
	.string "I dredge the river under the\nbridge. Last spring the net came\pup with this {STR_VAR_2} in it.\pThe old books say its kind swam\nhere before the tower was built.\pNow it sits in my rain barrel\nand sulks for deeper water.\pTrade me a {STR_VAR_1}? A shell\nwould suit the barrel better.$"

PoxEcruteak_EcruteakCity_House2_hns_Text_TradeComplete:
	.string "Take it somewhere the water is\ndeep. It has waited long enough.\pYour {STR_VAR_1} gets the barrel.\nI will change the water daily.$"

PoxEcruteak_EcruteakCity_House2_hns_Text_TradeDecline:
	.string "No hurry. The barrel is not going\nanywhere, and neither is it.$"

PoxEcruteak_EcruteakCity_House2_hns_Text_TradeWrongMon:
	.string "That is not a {STR_VAR_1}. I need\nsomething that likes a barrel.$"

PoxEcruteak_EcruteakCity_House2_hns_Text_TradeDone:
	.string "The shell in my rain barrel\nopened for the first time today.\pI think it likes the barrel.\nThe net stays dry until spring.$"
