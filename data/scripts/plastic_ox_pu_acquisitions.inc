POX_PU_MoonStone1::
	lock
	faceplayer
	goto_if_set FLAG_POX_MTMOON_MOON_STONE_1, POX_PU_Release
	giveitem ITEM_MOON_STONE
	goto_if_eq VAR_RESULT, FALSE, POX_PU_Release
	setflag FLAG_POX_MTMOON_MOON_STONE_1
	removeobject VAR_LAST_TALKED
	goto POX_PU_Release

POX_PU_MoonStone2::
	lock
	faceplayer
	goto_if_set FLAG_POX_MTMOON_MOON_STONE_2, POX_PU_Release
	giveitem ITEM_MOON_STONE
	goto_if_eq VAR_RESULT, FALSE, POX_PU_Release
	setflag FLAG_POX_MTMOON_MOON_STONE_2
	removeobject VAR_LAST_TALKED
	goto POX_PU_Release

POX_PU_CoinPrizes::
	lock
	faceplayer
	checkitem ITEM_COIN_CASE
	goto_if_eq VAR_RESULT, FALSE, POX_PU_PrizeNeedCase
	msgbox POX_PU_Text_Prizes, MSGBOX_DEFAULT
	showcoinsbox 1, 1
	msgbox POX_PU_Text_AbraPrize, MSGBOX_YESNO
	setvar VAR_0x8004, 0
	goto_if_eq VAR_RESULT, YES, POX_PU_BuyPrize
	msgbox POX_PU_Text_LuvdiscPrize, MSGBOX_YESNO
	setvar VAR_0x8004, 1
	goto_if_eq VAR_RESULT, YES, POX_PU_BuyPrize
	msgbox POX_PU_Text_CastformPrize, MSGBOX_YESNO
	setvar VAR_0x8004, 2
	goto_if_eq VAR_RESULT, YES, POX_PU_BuyPrize
	msgbox POX_PU_Text_PorygonPrize, MSGBOX_YESNO
	setvar VAR_0x8004, 3
	goto_if_eq VAR_RESULT, YES, POX_PU_BuyPrize
	goto POX_PU_ClosePrize

POX_PU_BuyPrize::
	special PlasticOxBuyCoinPrize
	goto_if_eq VAR_RESULT, MON_CANT_GIVE, POX_PU_PrizeNoRoom
	goto_if_eq VAR_RESULT, 3, POX_PU_PrizeNoCoins
	copyvar VAR_0x8005, VAR_RESULT
	updatecoinsbox 1, 1
	playfanfare MUS_OBTAIN_ITEM
	msgbox POX_PU_Text_PrizeReceived, MSGBOX_DEFAULT
	waitfanfare
	goto_if_eq VAR_0x8005, MON_GIVEN_TO_PC, POX_PU_PrizeSentToPC
	goto POX_PU_ClosePrize

POX_PU_PrizeSentToPC::
	msgbox POX_PU_Text_SentToPC, MSGBOX_DEFAULT
	goto POX_PU_ClosePrize

POX_PU_PrizeNoRoom::
	msgbox POX_PU_Text_PrizeNoRoom, MSGBOX_DEFAULT
	goto POX_PU_ClosePrize

POX_PU_PrizeNoCoins::
	msgbox POX_PU_Text_NoCoins, MSGBOX_DEFAULT
POX_PU_ClosePrize::
	hidecoinsbox 0, 0
	goto POX_PU_Release

POX_PU_PrizeNeedCase::
	msgbox POX_PU_Text_NeedCase, MSGBOX_DEFAULT
	goto POX_PU_Release

POX_PU_HelixRevival::
	msgbox POX_PU_Text_ReviveHelix, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, RustboroCity_DevonCorp_2F_EventScript_CheckDomeFossil
	special PlasticOxReviveHelix
	goto_if_eq VAR_RESULT, MON_CANT_GIVE, POX_PU_FossilNoRoom
	goto_if_eq VAR_RESULT, 3, POX_PU_Release
	copyvar VAR_0x8005, VAR_RESULT
	setflag FLAG_RECEIVED_REVIVED_FOSSIL_MON
	playfanfare MUS_OBTAIN_ITEM
	msgbox POX_PU_Text_OmanyteReceived, MSGBOX_DEFAULT
	waitfanfare
	goto_if_ne VAR_0x8005, MON_GIVEN_TO_PC, POX_PU_Release
	msgbox POX_PU_Text_SentToPC, MSGBOX_DEFAULT
	goto POX_PU_Release

POX_PU_FossilNoRoom::
	msgbox POX_PU_Text_FossilNoRoom, MSGBOX_DEFAULT
	goto POX_PU_Release

POX_PU_MailGuard::
	lock
	faceplayer
	goto_if_set FLAG_POX_DELIBIRD_DELIVERED, POX_PU_MailGuardDone
	goto_if_set FLAG_POX_DELIBIRD_RECEIVED, POX_PU_MailGuardRetry
	msgbox POX_PU_Text_MailOffer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, POX_PU_Release
	special PlasticOxGiveMailDelibird
	goto_if_eq VAR_RESULT, MON_CANT_GIVE, POX_PU_MailNoRoom
	playfanfare MUS_OBTAIN_ITEM
	msgbox POX_PU_Text_DelibirdReceived, MSGBOX_DEFAULT
	waitfanfare
	goto POX_PU_Release

POX_PU_MailGuardRetry::
	special PlasticOxGiveMailDelibird
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PARTY, POX_PU_MailReplaced
	goto_if_eq VAR_RESULT, MON_CANT_GIVE, POX_PU_MailNoRoom
	msgbox POX_PU_Text_MailReminder, MSGBOX_DEFAULT
	goto POX_PU_Release

POX_PU_MailReplaced::
	msgbox POX_PU_Text_MailReplaced, MSGBOX_DEFAULT
	goto POX_PU_Release

POX_PU_MailNoRoom::
	msgbox POX_PU_Text_MailNoRoom, MSGBOX_DEFAULT
	goto POX_PU_Release

POX_PU_MailGuardDone::
	msgbox POX_PU_Text_MailGuardDone, MSGBOX_DEFAULT
	goto POX_PU_Release

POX_PU_MailRecipient::
	lock
	faceplayer
	goto_if_set FLAG_POX_DELIBIRD_DELIVERED, POX_PU_MailRecipientDone
	special PlasticOxDeliverMail
	goto_if_ne VAR_RESULT, MON_GIVEN_TO_PARTY, POX_PU_MailRecipientWaiting
	msgbox POX_PU_Text_Delivered, MSGBOX_DEFAULT
	goto POX_PU_Release

POX_PU_MailRecipientWaiting::
	msgbox POX_PU_Text_MailRecipientWaiting, MSGBOX_DEFAULT
	goto POX_PU_Release

POX_PU_MailRecipientDone::
	msgbox POX_PU_Text_MailRecipientDone, MSGBOX_DEFAULT
POX_PU_Release::
	release
	end

POX_PU_Text_Prizes:
	.string "Welcome to the GOLDENROD prize desk!\p"
	.string "All four prize POKéMON are Lv. 15.\n"
	.string "I'll show you each offer in turn.$"
POX_PU_Text_AbraPrize:
	.string "Would you like ABRA\nfor 200 COINS?$"
POX_PU_Text_LuvdiscPrize:
	.string "Would you like LUVDISC\nfor 500 COINS?$"
POX_PU_Text_CastformPrize:
	.string "Would you like CASTFORM\nfor 1,500 COINS?$"
POX_PU_Text_PorygonPrize:
	.string "Would you like PORYGON\nfor 4,000 COINS?$"
POX_PU_Text_PrizeReceived:
	.string "Here is your Lv. 15 prize POKéMON!\nThank you for playing!$"
POX_PU_Text_SentToPC:
	.string "Your party is full, so your new\nPOKéMON was sent to your PC.$"
POX_PU_Text_PrizeNoRoom:
	.string "Your party and PC are both full.\nYour COINS have not been spent.$"
POX_PU_Text_NoCoins:
	.string "You don't have enough COINS.\nNo COINS have been spent.$"
POX_PU_Text_NeedCase:
	.string "Please visit the coin cashier\nto the left for a free COIN CASE.$"
POX_PU_Text_ReviveHelix:
	.string "That's a HELIX FOSSIL! We can now\nrevive it as a Lv. 10 OMANYTE.\p"
	.string "Shall I revive it for you?$"
POX_PU_Text_OmanyteReceived:
	.string "Your HELIX FOSSIL came back to life!\nYou received OMANYTE at Lv. 10!$"
POX_PU_Text_FossilNoRoom:
	.string "Your party and PC are both full.\nKeep your fossil and come back!$"
POX_PU_Text_MailOffer:
	.string "I'm WEBSTER, the gate guard.\nWill you deliver a letter for me?\p"
	.string "My friend RANDY is on ROUTE 33,\nnear the mountain path.\p"
	.string "My DELIBIRD will carry the MAIL.\nWill you take it to him?$"
POX_PU_Text_DelibirdReceived:
	.string "You received DELIBIRD at Lv. 16!\nIt's holding WEBSTER's MAIL.\p"
	.string "Take it to RANDY on ROUTE 33.$"
POX_PU_Text_MailReminder:
	.string "Take my DELIBIRD, holding my MAIL,\nto RANDY on ROUTE 33.\p"
	.string "If you stored the MAIL in your PC,\ngive it back to DELIBIRD first.\p"
	.string "If you erased it, bring my DELIBIRD\nback with nothing held.$"
POX_PU_Text_MailReplaced:
	.string "I wrote the letter again and gave\nit to my DELIBIRD. Thanks!$"
POX_PU_Text_MailNoRoom:
	.string "You'll need an open party slot\nand room for DELIBIRD's MAIL.\p"
	.string "Please make room and try again.$"
POX_PU_Text_MailGuardDone:
	.string "RANDY got my letter? Thank you!\nTake good care of DELIBIRD.$"
POX_PU_Text_MailRecipientWaiting:
	.string "I'm RANDY. I moved here from\nROUTE 31 to explore MT. MOON.\p"
	.string "Expecting MAIL from WEBSTER...\nIs his DELIBIRD in your party,\lholding his original letter?$"
POX_PU_Text_Delivered:
	.string "A letter from WEBSTER!\nYou delivered his MAIL!\p"
	.string "He's doing well. That's a relief!\nThanks for bringing it.\p"
	.string "He says you should keep DELIBIRD.\nIt looks happy traveling with you!$"
POX_PU_Text_MailRecipientDone:
	.string "Thanks again for WEBSTER's letter!\nDELIBIRD is yours to keep.$"
