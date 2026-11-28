GoldenrodCity_GameCorner_hns_MapScripts::
	.byte 0

PoxGoldenrod_GoldenrodCity_GameCorner_hns_3::
	msgbox PoxGoldenrod_GoldenrodCity_GameCorner_hns_3_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_GameCorner_hns_3_Text:
	.string "I come for the music.\nThe machines are much too loud.$"

PoxGoldenrod_GoldenrodCity_GameCorner_hns_4::
	msgbox PoxGoldenrod_GoldenrodCity_GameCorner_hns_4_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_GameCorner_hns_4_Text:
	.string "My lucky seat is by the wall.\nPlease don't tell anyone.$"

PoxGoldenrod_GoldenrodCity_GameCorner_hns_5::
	msgbox PoxGoldenrod_GoldenrodCity_GameCorner_hns_5_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_GameCorner_hns_5_Text:
	.string "I set myself a coin limit.\nYesterday I remembered it.$"

PoxGoldenrod_GoldenrodCity_GameCorner_hns_6::
	msgbox PoxGoldenrod_GoldenrodCity_GameCorner_hns_6_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_GameCorner_hns_6_Text:
	.string "The reels stop faster than my eyes.\nMy granddaughter sees everything.$"

PoxGoldenrod_GoldenrodCity_GameCorner_hns_7::
	msgbox PoxGoldenrod_GoldenrodCity_GameCorner_hns_7_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_GameCorner_hns_7_Text:
	.string "A sailor taught me to count odds.\nI still prefer guessing.$"

PoxGoldenrod_GoldenrodCity_GameCorner_hns_8::
	msgbox PoxGoldenrod_GoldenrodCity_GameCorner_hns_8_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_GameCorner_hns_8_Text:
	.string "No COIN CASE? Look for one below\nthe streets, in the UNDERGROUND.$"

PoxGoldenrod_GoldenrodCity_GameCorner_hns_9::
	msgbox PoxGoldenrod_GoldenrodCity_GameCorner_hns_9_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_GameCorner_hns_9_Text:
	.string "I saved my coins for a prize.\nNow I can't choose which one.$"

PoxGoldenrod_GoldenrodCity_GameCorner_hns_10::
	msgbox PoxGoldenrod_GoldenrodCity_GameCorner_hns_10_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_GameCorner_hns_10_Text:
	.string "The night crowd cheers every win.\nEven the small ones count.$"

@ Goldenrod coin counter. The Mauville donor clerk is not placed here; the
@ menu prices (50 for ¥1,000, 500 for ¥10,000) are kept unchanged.
	.set POX_GOLDENROD_COIN_PRICE_50, 1000
	.set POX_GOLDENROD_COIN_PRICE_500, 10000

PoxGoldenrod_CoinClerk::
	lock
	faceplayer
	msgbox PoxGoldenrod_Text_CoinClerkWelcome, MSGBOX_DEFAULT
	checkitem ITEM_COIN_CASE
	goto_if_eq VAR_RESULT, FALSE, PoxGoldenrod_CoinClerk_NeedCase
	message PoxGoldenrod_Text_CoinClerkOffer
	waitmessage
	showmoneybox 0, 0
	showcoinsbox 1, 6
	multichoicedefault 15, 0, MULTI_GAME_CORNER_COINS, 0, FALSE
	switch VAR_RESULT
	case 0, PoxGoldenrod_CoinClerk_Buy50
	case 1, PoxGoldenrod_CoinClerk_Buy500
	goto PoxGoldenrod_CoinClerk_Cancel
	end

PoxGoldenrod_CoinClerk_Buy50::
	checkcoins VAR_TEMP_1
	goto_if_ge VAR_TEMP_1, (MAX_COINS + 1 - 50), PoxGoldenrod_CoinClerk_NoRoom
	checkmoney POX_GOLDENROD_COIN_PRICE_50
	goto_if_eq VAR_RESULT, FALSE, PoxGoldenrod_CoinClerk_NoMoney
	addcoins 50
	removemoney POX_GOLDENROD_COIN_PRICE_50
	updatemoneybox
	updatecoinsbox 1, 6
	playse SE_SHOP
	msgbox PoxGoldenrod_Text_CoinClerkThanks, MSGBOX_DEFAULT
	goto PoxGoldenrod_CoinClerk_Close

PoxGoldenrod_CoinClerk_Buy500::
	checkcoins VAR_TEMP_1
	goto_if_ge VAR_TEMP_1, (MAX_COINS + 1 - 500), PoxGoldenrod_CoinClerk_NoRoom
	checkmoney POX_GOLDENROD_COIN_PRICE_500
	goto_if_eq VAR_RESULT, FALSE, PoxGoldenrod_CoinClerk_NoMoney
	addcoins 500
	removemoney POX_GOLDENROD_COIN_PRICE_500
	updatemoneybox
	updatecoinsbox 1, 6
	playse SE_SHOP
	msgbox PoxGoldenrod_Text_CoinClerkThanks, MSGBOX_DEFAULT
	goto PoxGoldenrod_CoinClerk_Close

PoxGoldenrod_CoinClerk_NeedCase::
	msgbox PoxGoldenrod_Text_CoinClerkNeedCase, MSGBOX_DEFAULT
	release
	end

PoxGoldenrod_CoinClerk_NoMoney::
	msgbox PoxGoldenrod_Text_CoinClerkNoMoney, MSGBOX_DEFAULT
	goto PoxGoldenrod_CoinClerk_Close

PoxGoldenrod_CoinClerk_Cancel::
	msgbox PoxGoldenrod_Text_CoinClerkCancel, MSGBOX_DEFAULT
	goto PoxGoldenrod_CoinClerk_Close

PoxGoldenrod_CoinClerk_NoRoom::
	msgbox PoxGoldenrod_Text_CoinClerkNoRoom, MSGBOX_DEFAULT
	goto PoxGoldenrod_CoinClerk_Close

PoxGoldenrod_CoinClerk_Close::
	hidemoneybox
	hidecoinsbox 0, 5
	release
	end

PoxGoldenrod_Text_CoinClerkWelcome:
	.string "Coins? ¥1,000 buys fifty.\n¥10,000 buys five hundred.\pYou'll need a COIN CASE first.$"

PoxGoldenrod_Text_CoinClerkOffer:
	.string "How many COINS, then?$"

PoxGoldenrod_Text_CoinClerkThanks:
	.string "There you are. Mind the odds.$"

PoxGoldenrod_Text_CoinClerkNeedCase:
	.string "No COIN CASE, no coins.\nThe UNDERGROUND has one.$"

PoxGoldenrod_Text_CoinClerkNoMoney:
	.string "That's not enough money.$"

PoxGoldenrod_Text_CoinClerkCancel:
	.string "Suit yourself. The reels will wait.$"

PoxGoldenrod_Text_CoinClerkNoRoom:
	.string "Your COIN CASE is full.\nSpend some before you buy more.$"

@ Second prize-desk object used to run the same POX_PU_CoinPrizes counter.
@ It is now the floor host for the single desk beside him.
PoxGoldenrod_PrizeHost::
	msgbox PoxGoldenrod_Text_PrizeHost, MSGBOX_NPC
	end
PoxGoldenrod_Text_PrizeHost:
	.string "The prize desk is to my left.\nI mind the floor out here.\pFour thousand coins for a PORYGON.\nIn eleven years I have never heard\panybody count that high out loud.$"
