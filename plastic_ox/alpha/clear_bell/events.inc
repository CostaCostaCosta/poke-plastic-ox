@ The Clear Bell chain. Installed by plastic_ox/alpha/clear_bell.py.
@ New Mauville's generator goes quiet -> ZAPDOS moves to the Radio Tower ->
@ the engineer gives the CLEAR BELL -> MORTY rings it under the Burned Tower
@ and SUICUNE comes back to the place it last saw the player.

@ ---- Goldenrod Radio Tower 5F ----

PoxRadioTower_OnTransition::
	call_if_set FLAG_POX_CAUGHT_ZAPDOS, PoxRadioTower_HideZapdos
	call_if_unset FLAG_POX_STORY_SPACE_CENTER, PoxRadioTower_HideZapdos
	call_if_ne VAR_NEW_MAUVILLE_STATE, 2, PoxRadioTower_HideZapdos
	end
PoxRadioTower_HideZapdos::
	setflag FLAG_TEMP_1
	return

pox_legendary_sage PoxRadioTower_ZapdosSage, TRAINER_PLASTIC_OX_ZAPDOS_SAGE, SPECIES_ZAPDOS, 55, FLAG_POX_CAUGHT_ZAPDOS, LOCALID_POX_ZAPDOS_SAGE, LOCALID_POX_ZAPDOS, PoxRadioTower_Text_ZapdosSage, PoxRadioTower_Text_ZapdosSageDefeat

PoxRadioTower_Engineer::
	lock
	faceplayer
	goto_if_set FLAG_POX_CAUGHT_ZAPDOS, PoxRadioTower_EngineerBell
	goto_if_ne VAR_NEW_MAUVILLE_STATE, 2, PoxRadioTower_EngineerQuiet
	goto_if_unset FLAG_POX_STORY_SPACE_CENTER, PoxRadioTower_EngineerStatic
	msgbox PoxRadioTower_Text_EngineerGuest, MSGBOX_DEFAULT
	goto PoxRadioTower_EngineerEnd
PoxRadioTower_EngineerQuiet::
	msgbox PoxRadioTower_Text_EngineerQuiet, MSGBOX_DEFAULT
	goto PoxRadioTower_EngineerEnd
PoxRadioTower_EngineerStatic::
	msgbox PoxRadioTower_Text_EngineerStatic, MSGBOX_DEFAULT
	goto PoxRadioTower_EngineerEnd
PoxRadioTower_EngineerBell::
	checkitem ITEM_CLEAR_BELL
	goto_if_eq VAR_RESULT, TRUE, PoxRadioTower_EngineerAfter
	msgbox PoxRadioTower_Text_EngineerFound, MSGBOX_DEFAULT
	giveitem ITEM_CLEAR_BELL
	msgbox PoxRadioTower_Text_EngineerGive, MSGBOX_DEFAULT
	goto PoxRadioTower_EngineerEnd
PoxRadioTower_EngineerAfter::
	msgbox PoxRadioTower_Text_EngineerAfter, MSGBOX_DEFAULT
PoxRadioTower_EngineerEnd::
	release
	end

PoxRadioTower_Text_ZapdosSage::
	.string "SAGE: When the storm under HOENN\n"
	.string "went out, this one went looking\l"
	.string "for the next loudest sky.\p"
	.string "It found the aerial. It sits up\n"
	.string "here and hums along with it.\p"
	.string "MORTY said to stay until it feels\n"
	.string "safe. Show me it can rest with you.$"

PoxRadioTower_Text_ZapdosSageDefeat::
	.string "SAGE: Not one of yours flinched\n"
	.string "when the lights flickered.\p"
	.string "ZAPDOS saw that too.$"

PoxRadioTower_Text_EngineerQuiet::
	.string "I keep the transmitter honest.\n"
	.string "Clean signal, every band, every\l"
	.string "night. Boring is the goal.$"

PoxRadioTower_Text_EngineerStatic::
	.string "Static on every band since that\n"
	.string "old generator down south went\l"
	.string "dark. Same hour, every night.\p"
	.string "The director shut the east studio\n"
	.string "until the inspectors sign off.$"

PoxRadioTower_Text_EngineerGuest::
	.string "Something came in off the aerial\n"
	.string "and settled in the east studio.\p"
	.string "There's a fellow in robes with it.\n"
	.string "He says to let it be. I'm letting.$"

PoxRadioTower_Text_EngineerFound::
	.string "The static's gone. Thank you.\p"
	.string "When we bolted the transmitter\n"
	.string "down, we dug this out of the\l"
	.string "footing. It rang on its own last\l"
	.string "night. First time in years.\p"
	.string "It isn't ours. Take it to someone\n"
	.string "who knows what it's for.$"

PoxRadioTower_Text_EngineerGive::
	.string "Old ECRUTEAK work, the director\n"
	.string "says. They had a bell tower there\l"
	.string "once, before the fire.$"

PoxRadioTower_Text_EngineerAfter::
	.string "The aerial's clean as a whistle.\n"
	.string "Shame. I'd got used to the hum.$"

@ ---- Burned Tower B1F: MORTY and SUICUNE ----

PoxClearBell_TowerOnTransition::
	call_if_unset FLAG_BADGE03_GET, PoxClearBell_HideMorty
	call_if_set FLAG_POX_CAUGHT_SUICUNE, PoxClearBell_HideMorty
	call_if_unset FLAG_POX_RANG_CLEAR_BELL, PoxClearBell_HideSuicune
	call_if_set FLAG_POX_CAUGHT_SUICUNE, PoxClearBell_HideSuicune
	goto PoxTower_InitGraphics
PoxClearBell_HideMorty::
	setflag FLAG_TEMP_1
	return
PoxClearBell_HideSuicune::
	setflag FLAG_TEMP_2
	return

@ The gym MORTY is away from badge 3 until SUICUNE is caught.
PoxClearBell_GymOnTransition::
	call_if_set FLAG_POX_HIDE_STORY_NPCS, PoxClearBell_HideMorty
	goto_if_unset FLAG_BADGE03_GET, PoxClearBell_GymEnd
	call_if_unset FLAG_POX_CAUGHT_SUICUNE, PoxClearBell_HideMorty
PoxClearBell_GymEnd::
	end

PoxClearBell_Morty::
	lockall
	faceplayer
	goto_if_set FLAG_POX_RANG_CLEAR_BELL, PoxClearBell_SuicuneSage
	checkitem ITEM_CLEAR_BELL
	goto_if_eq VAR_RESULT, TRUE, PoxClearBell_Ring
	msgbox PoxClearBell_Text_MortyWaiting, MSGBOX_DEFAULT
	releaseall
	end
PoxClearBell_Ring::
	msgbox PoxClearBell_Text_MortyBell, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, PoxClearBell_NotYet
	closemessage
	playse SE_M_HEAL_BELL
	waitse
	delay 40
	playse SE_M_HEAL_BELL
	waitse
	setvar VAR_0x8004, 1
	setvar VAR_0x8005, 1
	setvar VAR_0x8006, 12
	setvar VAR_0x8007, 3
	special ShakeCamera
	waitstate
	setflag FLAG_POX_RANG_CLEAR_BELL
	clearflag FLAG_TEMP_2
	addobject LOCALID_POX_SUICUNE
	playmoncry SPECIES_SUICUNE, CRY_MODE_NORMAL
	applymovement LOCALID_POX_SUICUNE, PoxClearBell_SuicuneArrive
	waitmovement 0
	waitmoncry
	msgbox PoxClearBell_Text_MortyArrived, MSGBOX_DEFAULT
	goto PoxClearBell_SuicuneSage
PoxClearBell_NotYet::
	msgbox PoxClearBell_Text_MortyNotYet, MSGBOX_DEFAULT
	releaseall
	end

PoxClearBell_SuicuneArrive:
	jump_in_place_down
	jump_in_place_down
	step_end

pox_legendary_sage PoxClearBell_SuicuneSage, TRAINER_PLASTIC_OX_SUICUNE_SAGE, SPECIES_SUICUNE, 55, FLAG_POX_CAUGHT_SUICUNE, LOCALID_POX_SUICUNE_MORTY, LOCALID_POX_SUICUNE, PoxClearBell_Text_MortySage, PoxClearBell_Text_MortySageDefeat

PoxClearBell_Text_MortyWaiting::
	.string "MORTY: This is where it looked\n"
	.string "back at you. I keep coming here.\p"
	.string "The tower used to call them with\n"
	.string "a bell. The bell is long gone.\p"
	.string "If the tower could call again,\n"
	.string "I think it would come. I'll wait.$"

PoxClearBell_Text_MortyBell::
	.string "MORTY: That sound in your bag...\n"
	.string "That is the tower's own bell.\p"
	.string "Shall I ring it?$"

PoxClearBell_Text_MortyNotYet::
	.string "MORTY: Then not yet. It has\n"
	.string "waited this long. So can I.$"

PoxClearBell_Text_MortyArrived::
	.string "MORTY: SUICUNE...\n"
	.string "It came back for you.$"

PoxClearBell_Text_MortySage::
	.string "MORTY: I sent the sages out and\n"
	.string "kept the hardest watch for myself.\p"
	.string "SUICUNE will choose its partner.\n"
	.string "Let it watch you choose yours.$"

PoxClearBell_Text_MortySageDefeat::
	.string "MORTY: There. It saw.\n"
	.string "My watch is over.$"
