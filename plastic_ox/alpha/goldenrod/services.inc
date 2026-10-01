@ Local Goldenrod services. Both brothers use the selected party slot.
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
	msgbox PoxGoldenrod_Text_Younger, MSGBOX_YESNO
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
PoxGoldenrod_Cut::
	closemessage
	fadescreen FADE_TO_BLACK
	special PoxMaximizeSelectedMonFriendship
	playfanfare MUS_HEAL
	waitfanfare
	fadescreen FADE_FROM_BLACK
	msgbox PoxGoldenrod_Text_Done
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
	.string "I'm the older HAIRCUT BROTHER.\pA haircut costs ¥500 and brings\nyour POKéMON's friendship to maximum.\pWould you like one?$"
PoxGoldenrod_Text_Younger:
	.string "I'm the younger HAIRCUT BROTHER.\pFor ¥300, I'll give your POKéMON\na haircut and maximum friendship!\pWould you like one?$"
PoxGoldenrod_Text_Choose:
	.string "Which POKéMON needs a haircut?$"
PoxGoldenrod_Text_Done:
	.string "All done! Your POKéMON's friendship\nis now at its maximum!$"
PoxGoldenrod_Text_Egg:
	.string "An EGG doesn't need a haircut.\nCome back after it hatches!$"
PoxGoldenrod_Text_NoMoney:
	.string "You don't have enough money.$"

PoxGoldenrod_Directory::
	msgbox PoxGoldenrod_Text_Directory, MSGBOX_SIGN
	end
PoxGoldenrod_Text_Directory:
	.string "GOLDENROD CITY\nShops, broadcasts, and friendly faces.$"

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
	pokemart PoxGoldenrod_Shop2F_Items
	release
	end
	.align 2
PoxGoldenrod_Shop2F_Items:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_REPEL
	.2byte ITEM_NONE

PoxGoldenrod_Shop3F::
	lock
	faceplayer
	pokemart PoxGoldenrod_Shop3F_Items
	release
	end
	.align 2
PoxGoldenrod_Shop3F_Items:
	.2byte ITEM_TM_PROTECT
	.2byte ITEM_TM_RETURN
	.2byte ITEM_TM_FRUSTRATION
	.2byte ITEM_NONE

PoxGoldenrod_Shop4F::
	lock
	faceplayer
	pokemart PoxGoldenrod_Shop4F_Items
	release
	end
	.align 2
PoxGoldenrod_Shop4F_Items:
	.2byte ITEM_FIRE_STONE
	.2byte ITEM_WATER_STONE
	.2byte ITEM_THUNDER_STONE
	.2byte ITEM_LEAF_STONE
	.2byte ITEM_NONE

PoxGoldenrod_Shop5F::
	lock
	faceplayer
	pokemart PoxGoldenrod_Shop5F_Items
	release
	end
	.align 2
PoxGoldenrod_Shop5F_Items:
	.2byte ITEM_HP_UP
	.2byte ITEM_PROTEIN
	.2byte ITEM_IRON
	.2byte ITEM_CALCIUM
	.2byte ITEM_ZINC
	.2byte ITEM_CARBOS
	.2byte ITEM_NONE
