PokemonMansion_1F_Frlg_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, PokemonMansion_1F_OnLoad
	map_script MAP_SCRIPT_ON_TRANSITION, PokemonMansion_1F_OnTransition
	.byte 0

PokemonMansion_1F_OnLoad::
	call_if_set FLAG_POKEMON_MANSION_SWITCH_STATE, PokemonMansion_EventScript_PressSwitch_1F
	end

PokemonMansion_1F_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_POKEMON_MANSION_1F
	end

PokemonMansion_1F_EventScript_Statue::
	lockall
	setvar VAR_0x8004, 0
	call PokemonMansion_EventScript_SecretSwitch
	playse SE_UNLOCK
	special DrawWholeMapView
	waitse
	releaseall
	end

PoxMansion_EventScript_StrengthKey::
	checkitem ITEM_STRENGTH_KEY
	goto_if_eq VAR_RESULT, TRUE, PoxMansion_EventScript_StrengthKeyOwned
	msgbox PoxMansion_Text_StrengthKeyIntro, MSGBOX_DEFAULT
	giveitem ITEM_STRENGTH_KEY
	goto_if_eq VAR_RESULT, FALSE, PoxMansion_EventScript_StrengthKeyBagFull
PoxMansion_EventScript_StrengthKeyOwned::
	msgbox PoxMansion_Text_StrengthKeyOwned, MSGBOX_DEFAULT
	end
PoxMansion_EventScript_StrengthKeyBagFull::
	msgbox PoxMansion_Text_StrengthKeyBagFull, MSGBOX_DEFAULT
	end

PoxMansion_Text_StrengthKeyIntro::
	.string "Careful with that shelf. If it's\nbrittle, it's important.\pBLAINE sent word you'd be\nthrough. He asked me to give you\lthis. It's the STRENGTH KEY,\lfrom when we still moved the big\lcabinets ourselves.$"

PoxMansion_Text_StrengthKeyOwned::
	.string "With the STRENGTH KEY a POKéMON\ncan shove boulders aside outside\lof battle.\pYou'll want that wherever the\nsea has been rearranging a cave.$"

PoxMansion_Text_StrengthKeyBagFull::
	.string "Your KEY ITEMS POCKET is full.\nMake room and come back.\pI'm not going anywhere. Clearly.$"

PoxMansion_EventScript_Explorer::
	msgbox PoxMansion_Text_Explorer, MSGBOX_NPC
	end
PoxMansion_Text_Explorer::
	.string "I came in on a dare. It isn't\neven scary. It's just paper.\lRooms and rooms of paper.\pThere's a man from the LAB\nfurther in who has been here all\lday. He talks to the shelves.$"

PokemonMansion_Text_PressSecretSwitch::
	.string "A secret switch!\p"
	.string "Press it?$"

PokemonMansion_Text_WhoWouldnt::
	.string "Who wouldn't?$"

PokemonMansion_Text_NotQuiteYet::
	.string "Not quite yet!$"

PokemonMansion_1F_EventScript_ItemCarbos::
	finditem ITEM_CARBOS
	end

PokemonMansion_1F_EventScript_ItemEscapeRope::
	finditem ITEM_ESCAPE_ROPE
	end

PokemonMansion_1F_EventScript_ItemProtein::
	finditem ITEM_PROTEIN
	end

PokemonMansion_1F_EventScript_Ted::
	trainerbattle_single TRAINER_SCIENTIST_TED, PokemonMansion_1F_Text_TedIntro, PokemonMansion_1F_Text_TedDefeat
	msgbox PokemonMansion_1F_Text_TedPostBattle, MSGBOX_AUTOCLOSE
	end

PokemonMansion_1F_EventScript_Johnson::
	trainerbattle_single TRAINER_YOUNGSTER_JOHNSON, PokemonMansion_1F_Text_JohnsonIntro, PokemonMansion_1F_Text_JohnsonDefeat
	msgbox PokemonMansion_1F_Text_JohnsonPostBattle, MSGBOX_AUTOCLOSE
	end

PokemonMansion_1F_Text_TedIntro::
	.string "Who are you?\n"
	.string "There shouldn't be anyone here.$"

PokemonMansion_1F_Text_TedDefeat::
	.string "Ouch!$"

PokemonMansion_1F_Text_TedPostBattle::
	.string "A key? I don't know what you're\n"
	.string "talking about.$"

PokemonMansion_1F_Text_JohnsonIntro::
	.string "W-w-waah! You startled me!\n"
	.string "I thought you were a ghost.$"

PokemonMansion_1F_Text_JohnsonDefeat::
	.string "Tch!\n"
	.string "I can't get any wins.$"

PokemonMansion_1F_Text_JohnsonPostBattle::
	.string "I was exploring here by myself,\n"
	.string "but I feel spooked.\p"
	.string "I ought to go soon.$"
