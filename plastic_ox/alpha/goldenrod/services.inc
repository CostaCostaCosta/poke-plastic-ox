@ Gen 2 haircut brothers (GSC schedule). The older brother works Tuesdays,
@ Thursdays and Saturdays: a good ¥500 cut that pushes friendship to maximum.
@ The younger brother works Sundays, Mondays and Wednesdays: ¥300, but he
@ ruins the cut and the chosen POKéMON loses all of its trust.
@ Neither works on Friday. The off-duty brother is hidden by the map
@ ON_TRANSITION script in GoldenrodCity_UndergroundTunnel_hns/scripts.inc.
PoxGoldenrod_OlderHaircut::
	lock
	faceplayer
	setvar VAR_0x8008, 500
	msgbox PoxGoldenrod_Text_Older, MSGBOX_YESNO
	goto PoxGoldenrod_HaircutOffer

PoxGoldenrod_YoungerHaircut::
	lock
	faceplayer
	setvar VAR_0x8008, 300
	goto_if_set FLAG_POX_BAD_HAIRCUT_KNOWN, PoxGoldenrod_YoungerHaircut_Warn
	msgbox PoxGoldenrod_Text_Younger, MSGBOX_YESNO
	goto PoxGoldenrod_HaircutOffer

PoxGoldenrod_YoungerHaircut_Warn::
	msgbox PoxGoldenrod_Text_YoungerWarn, MSGBOX_YESNO
PoxGoldenrod_HaircutOffer::
	goto_if_ne VAR_RESULT, YES, PoxGoldenrod_Release
	msgbox PoxGoldenrod_Text_Choose
	special ChoosePartyMon
	lock
	faceplayer
	goto_if_ge VAR_0x8004, PARTY_SIZE, PoxGoldenrod_Release
	special IsSelectedMonEgg
	goto_if_eq VAR_RESULT, TRUE, PoxGoldenrod_Egg
	goto_if_eq VAR_0x8008, 300, PoxGoldenrod_PayYounger
	checkmoney 500
	goto_if_eq VAR_RESULT, FALSE, PoxGoldenrod_NoMoney
	removemoney 500
	goto PoxGoldenrod_Cut
PoxGoldenrod_PayYounger::
	checkmoney 300
	goto_if_eq VAR_RESULT, FALSE, PoxGoldenrod_NoMoney
	removemoney 300
	goto PoxGoldenrod_BadCut
PoxGoldenrod_Cut::
	closemessage
	fadescreen FADE_TO_BLACK
	special PoxMaximizeSelectedMonFriendship
	playfanfare MUS_HEAL
	waitfanfare
	fadescreen FADE_FROM_BLACK
	msgbox PoxGoldenrod_Text_Done
	goto PoxGoldenrod_Release
PoxGoldenrod_BadCut::
	closemessage
	fadescreen FADE_TO_BLACK
	special PoxMinimizeSelectedMonFriendship
	playse SE_FAILURE
	waitse
	fadescreen FADE_FROM_BLACK
	setflag FLAG_POX_BAD_HAIRCUT_KNOWN
	msgbox PoxGoldenrod_Text_BadDone
	goto PoxGoldenrod_Release
PoxGoldenrod_Release::
	release
	end
PoxGoldenrod_Egg::
	msgbox PoxGoldenrod_Text_Egg
	goto PoxGoldenrod_Release
PoxGoldenrod_NoMoney::
	msgbox PoxGoldenrod_Text_NoMoney
	goto PoxGoldenrod_Release
PoxGoldenrod_Text_Older:
	.string "I'm the older HAIRCUT BROTHER.\pTuesdays, Thursdays, Saturdays.\nThose are my days.\p¥500 buys a proper cut, and your\nPOKéMON's friendship climbs all\pthe way to the top. Ready?$"
PoxGoldenrod_Text_Younger:
	.string "I'm the younger HAIRCUT BROTHER.\pSundays, Mondays, Wednesdays.\nI mind the chair on those days.\p¥300 and I'll tidy your POKéMON\nright up. Want one?$"
PoxGoldenrod_Text_YoungerWarn:
	.string "Back for another?\pI'll be straight with you. My\nhands slipped last time, and your\pPOKéMON stopped trusting me.\pIt's still ¥300. Shall I try?$"
PoxGoldenrod_Text_Choose:
	.string "Which POKéMON gets the scissors?$"
PoxGoldenrod_Text_Done:
	.string "There! A clean cut. Your POKéMON\nlooks sharp and trusts you fully.$"
PoxGoldenrod_Text_BadDone:
	.string "Hm. That went sideways.\pYour POKéMON won't even look at\nyou now. I'm sorry. Truly.$"
PoxGoldenrod_Text_Egg:
	.string "An EGG? There's nothing to trim\nyet. Bring it back once it hatches.$"
PoxGoldenrod_Text_NoMoney:
	.string "You're short on money.\nCome back when you can pay.$"

PoxGoldenrod_Directory::
	msgbox PoxGoldenrod_Text_Directory, MSGBOX_SIGN
	end
PoxGoldenrod_Text_Directory:
	.string "GOLDENROD CITY\nShops, broadcasts, and friendly faces.$"

PoxGoldenrod_DeptStore7F_Sign::
	msgbox PoxGoldenrod_Text_DeptStore7F, MSGBOX_SIGN
	end
PoxGoldenrod_Text_DeptStore7F:
	.string "ROOFTOP TERRACE\nFresh air and a view of the whole\lcity. Drinks are sold on 6F.$"

PoxGoldenrod_GameCorner_Sign::
	msgbox PoxGoldenrod_Text_GameCornerSign, MSGBOX_SIGN
	end
PoxGoldenrod_Text_GameCornerSign:
	.string "GAME CORNER\nCoins in, luck out. Prizes at the\lcounter. Play for fun!$"

PoxGoldenrod_Bike::
	lock
	faceplayer
	checkitem ITEM_MACH_BIKE
	goto_if_eq VAR_RESULT, TRUE, PoxGoldenrod_BikeHave
	checkitem ITEM_ACRO_BIKE
	goto_if_eq VAR_RESULT, TRUE, PoxGoldenrod_BikeHave
	msgbox PoxGoldenrod_Text_Bike
	giveitem ITEM_MACH_BIKE
	goto PoxGoldenrod_Release
PoxGoldenrod_BikeHave::
	msgbox PoxGoldenrod_Text_BikeHave
	goto PoxGoldenrod_Release
PoxGoldenrod_Text_Bike:
	.string "Explore the city on two wheels!\nTake this bicycle with you.$"
PoxGoldenrod_Text_BikeHave:
	.string "Your bicycle is ready for the road!$"

@ The street woman points at the FLOWER SHOP counter: the shop is the only
@ place that hands over the SQUIRTBOTTLE (Pox_SquirtBottle at (2,4)).
PoxGoldenrod_SquirtBottleNote::
	goto_if_set FLAG_POX_SUDOWOODO_CLEARED, PoxGoldenrod_SquirtBottleNote_Cleared
	msgbox PoxGoldenrod_Text_SquirtBottleNote, MSGBOX_NPC
	end
PoxGoldenrod_SquirtBottleNote_Cleared::
	msgbox PoxGoldenrod_Text_SquirtBottleNoteCleared, MSGBOX_NPC
	end
PoxGoldenrod_Text_SquirtBottleNoteCleared:
	.string "Somebody cleared that odd tree off\nROUTE 36. The FLOWER SHOP girl has\pher bottle back for the flowers.$"
PoxGoldenrod_Text_SquirtBottleNote:
	.string "The FLOWER SHOP lends a\nSQUIRTBOTTLE for the odd tree on\pROUTE 36. Ask the girl inside.$"

PoxGoldenrod_Slots::
	lockall
	checkitem ITEM_COIN_CASE
	goto_if_eq VAR_RESULT, FALSE, PoxGoldenrod_NeedCase
	random 12
	copyvar VAR_0x8004, VAR_RESULT
	specialvar VAR_RESULT, GetSlotMachineId
	playslotmachine VAR_RESULT
	releaseall
	end
PoxGoldenrod_NeedCase::
	msgbox PoxGoldenrod_Text_NeedCase
	releaseall
	end
PoxGoldenrod_Text_NeedCase:
	.string "You'll need a COIN CASE.\nLook in the UNDERGROUND.$"

PoxGoldenrod_Elevator::
	lockall
	msgbox PoxGoldenrod_Text_Elevator
	multichoice 0, 0, MULTI_POX_GOLDENROD_FLOORS, FALSE
	switch VAR_RESULT
	case 0, PoxGoldenrod_LiftB1
	case 1, PoxGoldenrod_Lift1
	case 2, PoxGoldenrod_Lift2
	case 3, PoxGoldenrod_Lift3
	case 4, PoxGoldenrod_Lift4
	case 5, PoxGoldenrod_Lift5
	case 6, PoxGoldenrod_Lift6
	case 7, PoxGoldenrod_Lift7
	releaseall
	end
PoxGoldenrod_Text_Elevator:
	.string "Which floor would you like?$"

PoxGoldenrod_LiftB1::
	closemessage
	warp MAP_GOLDENROD_CITY_DEPARTMENT_STORE_BASEMENT_HNS, 10, 7
	waitstate
	releaseall
	end

PoxGoldenrod_Lift1::
	closemessage
	warp MAP_GOLDENROD_CITY_DEPARTMENT_STORE_1F_HNS, 9, 5
	waitstate
	releaseall
	end

PoxGoldenrod_Lift2::
	closemessage
	warp MAP_GOLDENROD_CITY_DEPARTMENT_STORE_2F_HNS, 9, 5
	waitstate
	releaseall
	end

PoxGoldenrod_Lift3::
	closemessage
	warp MAP_GOLDENROD_CITY_DEPARTMENT_STORE_3F_HNS, 9, 5
	waitstate
	releaseall
	end

PoxGoldenrod_Lift4::
	closemessage
	warp MAP_GOLDENROD_CITY_DEPARTMENT_STORE_4F_HNS, 9, 5
	waitstate
	releaseall
	end

PoxGoldenrod_Lift5::
	closemessage
	warp MAP_GOLDENROD_CITY_DEPARTMENT_STORE_5F_HNS, 9, 5
	waitstate
	releaseall
	end

PoxGoldenrod_Lift6::
	closemessage
	warp MAP_GOLDENROD_CITY_DEPARTMENT_STORE_6F_HNS, 9, 5
	waitstate
	releaseall
	end

PoxGoldenrod_Lift7::
	closemessage
	warp MAP_GOLDENROD_CITY_DEPARTMENT_STORE_7F_HNS, 10, 6
	waitstate
	releaseall
	end

PoxGoldenrod_Shop2F::
	lock
	faceplayer
	msgbox PoxGoldenrod_Shop2F_Text, MSGBOX_DEFAULT
	pokemart PoxGoldenrod_Shop2F_Items
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end
PoxGoldenrod_Shop2F_Text:
	.string "Welcome to the TRAINER'S MARKET!\nBALLS and medicine for the road.$"
	.align 2
PoxGoldenrod_Shop2F_Items:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_POTION
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_BURN_HEAL
	.2byte ITEM_ICE_HEAL
	.2byte ITEM_ESCAPE_ROPE
	.2byte ITEM_REPEL
	.2byte ITEM_NONE

PoxGoldenrod_Shop3F::
	lock
	faceplayer
	msgbox PoxGoldenrod_Shop3F_Text, MSGBOX_DEFAULT
	pokemart PoxGoldenrod_Shop3F_Items
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end
PoxGoldenrod_Shop3F_Text:
	.string "BATTLE COLLECTION. Held items\nthat turn a close match around.$"
	.align 2
PoxGoldenrod_Shop3F_Items:
	.2byte ITEM_SCOPE_LENS
	.2byte ITEM_BRIGHT_POWDER
	.2byte ITEM_FOCUS_BAND
	.2byte ITEM_WHITE_HERB
	.2byte ITEM_MENTAL_HERB
	.2byte ITEM_NONE

PoxGoldenrod_Shop4F::
	lock
	faceplayer
	msgbox PoxGoldenrod_Shop4F_Text, MSGBOX_DEFAULT
	pokemart PoxGoldenrod_Shop4F_Items
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end
PoxGoldenrod_Shop4F_Text:
	.string "EVOLUTION CORNER. Stones for the\nbig day, or one to wait a while.$"
	.align 2
PoxGoldenrod_Shop4F_Items:
	.2byte ITEM_FIRE_STONE
	.2byte ITEM_MOON_STONE
	.2byte ITEM_SUN_STONE
	.2byte ITEM_EVERSTONE
	.2byte ITEM_NONE

PoxGoldenrod_Shop5F::
	lock
	faceplayer
	msgbox PoxGoldenrod_Shop5F_Text, MSGBOX_DEFAULT
	pokemart PoxGoldenrod_Shop5F_Items
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end
PoxGoldenrod_Shop5F_Text:
	.string "PREMIUM HELD ITEMS. Our\nCHOICE BAND sells out by noon!$"
	.align 2
PoxGoldenrod_Shop5F_Items:
	.2byte ITEM_CHOICE_BAND
	.2byte ITEM_LEFTOVERS
	.2byte ITEM_SHELL_BELL
	.2byte ITEM_NONE

PoxGoldenrod_Vending6F::
	lockall
	msgbox PoxGoldenrod_Vending6F_Text, MSGBOX_DEFAULT
	pokemart PoxGoldenrod_Vending6F_Items
	releaseall
	end
PoxGoldenrod_Vending6F_Text:
	.string "A vending machine. The buttons\nare worn smooth.$"
	.align 2
PoxGoldenrod_Vending6F_Items:
	.2byte ITEM_FRESH_WATER
	.2byte ITEM_SODA_POP
	.2byte ITEM_LEMONADE
	.2byte ITEM_NONE

PoxGoldenrod_DeptFloor1F::
	msgbox PoxGoldenrod_DeptFloor1F_Text, MSGBOX_SIGN
	end
PoxGoldenrod_DeptFloor1F_Text:
	.string "GOLDENROD DEPT. STORE\n1F SERVICE  2F TRAINER'S MARKET\p3F BATTLE COLLECTION\n4F EVOLUTION CORNER\p5F PREMIUM HELD ITEMS\n6F REFRESHMENTS  ROOF TERRACE$"

PoxGoldenrod_DeptFloor2F::
	msgbox PoxGoldenrod_DeptFloor2F_Text, MSGBOX_SIGN
	end
PoxGoldenrod_DeptFloor2F_Text:
	.string "2F TRAINER'S MARKET\nBALLS, medicine and travel goods.$"

PoxGoldenrod_DeptFloor3F::
	msgbox PoxGoldenrod_DeptFloor3F_Text, MSGBOX_SIGN
	end
PoxGoldenrod_DeptFloor3F_Text:
	.string "3F BATTLE COLLECTION\nHeld items for close battles.$"

PoxGoldenrod_DeptFloor4F::
	msgbox PoxGoldenrod_DeptFloor4F_Text, MSGBOX_SIGN
	end
PoxGoldenrod_DeptFloor4F_Text:
	.string "4F EVOLUTION CORNER\nEvolution stones and EVERSTONES.$"

PoxGoldenrod_DeptFloor5F::
	msgbox PoxGoldenrod_DeptFloor5F_Text, MSGBOX_SIGN
	end
PoxGoldenrod_DeptFloor5F_Text:
	.string "5F PREMIUM HELD ITEMS\nCHOICE BAND, LEFTOVERS and more.$"

PoxGoldenrod_DeptFloor6F::
	msgbox PoxGoldenrod_DeptFloor6F_Text, MSGBOX_SIGN
	end
PoxGoldenrod_DeptFloor6F_Text:
	.string "6F REFRESHMENTS\nDrinks here. The roof is upstairs.$"

PoxGoldenrod_DeptShelf2F::
	msgbox PoxGoldenrod_DeptShelf2F_Text, MSGBOX_SIGN
	end
PoxGoldenrod_DeptShelf2F_Text:
	.string "POTIONS in neat rows, every label\nfacing forward. Someone is tidy.$"

PoxGoldenrod_DeptShelf4F::
	msgbox PoxGoldenrod_DeptShelf4F_Text, MSGBOX_SIGN
	end
PoxGoldenrod_DeptShelf4F_Text:
	.string "A glass case of polished stones.\nAsk the clerk to open it.$"
