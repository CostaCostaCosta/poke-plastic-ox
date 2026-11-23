Gate_NationalPark_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Gate_NationalPark_OnTransition
	map_script MAP_SCRIPT_ON_FRAME_TABLE, Gate_NationalPark_OnFrame
	.byte 0

@ Contest staff and entrants gather on the scheduled days, even if the player
@ has already competed. Set visibility before the gate objects are spawned.
Gate_NationalPark_OnTransition::
	special PoxGetDayOfWeek
	switch VAR_RESULT
	case WEEKDAY_TUE, Gate_NationalPark_ContestDay
	case WEEKDAY_THU, Gate_NationalPark_ContestDay
	case WEEKDAY_SAT, Gate_NationalPark_ContestDay
	setflag FLAG_POX_HIDE_PARK_CONTEST_CROWD
	setflag FLAG_POX_HIDE_PARK_WARDEN
	return

@ The Safari Zone Warden comes up to host Thursday's round.
Gate_NationalPark_ContestDay::
	clearflag FLAG_POX_HIDE_PARK_CONTEST_CROWD
	setflag FLAG_POX_HIDE_PARK_WARDEN
	compare VAR_RESULT, WEEKDAY_THU
	goto_if_ne Gate_NationalPark_ContestDayEnd
	clearflag FLAG_POX_HIDE_PARK_WARDEN
Gate_NationalPark_ContestDayEnd::
	return

Gate_NationalPark_OnFrame:
	map_script_2 VAR_TEMP_0, 0, Gate_NationalPark_EventScript_Arrival
	.2byte 0

Gate_NationalPark_EventScript_Arrival::
	setvar VAR_TEMP_0, 1
	special PlasticOxContest_Status
	compare VAR_RESULT, 0
	goto_if_eq Gate_NationalPark_EventScript_ArrivalEnd
	lockall
	special PlasticOxContest_Judge
	call PlasticOxContest_EventScript_ReportResult
	releaseall
Gate_NationalPark_EventScript_ArrivalEnd::
	end

Gate_NationalPark_EventScript_SouthAttendant::
	setvar VAR_0x8007, 0
	goto PlasticOxContest_EventScript_Attendant

Gate_NationalPark_EventScript_EastAttendant::
	setvar VAR_0x8007, 1
	goto PlasticOxContest_EventScript_Attendant

Gate_NationalPark_EventScript_Officer::
	special PoxGetDayOfWeek
	compare VAR_RESULT, WEEKDAY_THU
	goto_if_eq Gate_NationalPark_EventScript_Thursday
	msgbox Gate_NationalPark_Text_Schedule, MSGBOX_NPC
	end

Gate_NationalPark_EventScript_BirdWatcher::
	special PoxGetDayOfWeek
	compare VAR_RESULT, WEEKDAY_THU
	goto_if_eq Gate_NationalPark_EventScript_Thursday
	msgbox Gate_NationalPark_Text_BirdWatcher, MSGBOX_NPC
	end

Gate_NationalPark_EventScript_Contestant::
	special PoxGetDayOfWeek
	compare VAR_RESULT, WEEKDAY_THU
	goto_if_eq Gate_NationalPark_EventScript_Thursday
	msgbox Gate_NationalPark_Text_Contestant, MSGBOX_NPC
	end

Gate_NationalPark_EventScript_Visitor::
	special PoxGetDayOfWeek
	compare VAR_RESULT, WEEKDAY_THU
	goto_if_eq Gate_NationalPark_EventScript_Thursday
	msgbox Gate_NationalPark_Text_Visitor, MSGBOX_NPC
	end

Gate_NationalPark_EventScript_Thursday::
	msgbox Gate_NationalPark_Text_Thursday, MSGBOX_NPC
	end

@ Returning the Gold Teeth (tournament round one) puts the player on the
@ Warden's guest list for good; after that he signs entrants in himself.
Gate_NationalPark_EventScript_Warden::
	lock
	faceplayer
	goto_if_set FLAG_POX_WARDEN_GUEST, Gate_NationalPark_EventScript_WardenHost
	checkitem ITEM_GOLD_TEETH
	goto_if_eq VAR_RESULT, TRUE, Gate_NationalPark_EventScript_WardenTeeth
	msgbox Gate_NationalPark_Text_WardenToothless, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, YES, Gate_NationalPark_EventScript_WardenToothlessYes
	msgbox Gate_NationalPark_Text_WardenToothlessNo, MSGBOX_DEFAULT
	release
	end
Gate_NationalPark_EventScript_WardenToothlessYes::
	msgbox Gate_NationalPark_Text_WardenToothlessYes, MSGBOX_DEFAULT
	release
	end
Gate_NationalPark_EventScript_WardenTeeth::
	msgbox Gate_NationalPark_Text_WardenSees, MSGBOX_DEFAULT
	textcolor NPC_TEXT_COLOR_NEUTRAL
	playfanfare MUS_OBTAIN_TMHM
	message Gate_NationalPark_Text_GaveTeeth
	waitmessage
	waitfanfare
	msgbox Gate_NationalPark_Text_PoppedIn, MSGBOX_DEFAULT
	call EventScript_RestorePrevTextColor
	removeitem ITEM_GOLD_TEETH
	setflag FLAG_POX_WARDEN_GUEST
	msgbox Gate_NationalPark_Text_WardenThanks, MSGBOX_DEFAULT
	release
	end
Gate_NationalPark_EventScript_WardenHost::
	msgbox Gate_NationalPark_Text_WardenHost, MSGBOX_DEFAULT
	setvar VAR_0x8007, 0
	goto PlasticOxContest_EventScript_Attendant

Gate_NationalPark_Text_WardenToothless:
	.string "WARDEN: Hif fuff hefifoo! Ha lof ha\n"
	.string "feef ee hafahi ho. Heff hee fwee!$"
Gate_NationalPark_Text_WardenToothlessNo:
	.string "WARDEN: Ha? He ohay heh ha hoo\n"
	.string "ee haheh!$"
Gate_NationalPark_Text_WardenToothlessYes:
	.string "WARDEN: Ah howhee ho hoo!\n"
	.string "Eef ee hafahi ho!$"
Gate_NationalPark_Text_WardenSees:
	.string "WARDEN: Hwah?! Hoze are... HY\n"
	.string "HEETH! Hive! Hive hem here!$"
Gate_NationalPark_Text_GaveTeeth:
	.string "{PLAYER} returned the GOLD TEETH\n"
	.string "to the WARDEN.$"
Gate_NationalPark_Text_PoppedIn:
	.string "The WARDEN popped in his teeth!$"
Gate_NationalPark_Text_WardenThanks:
	.string "WARDEN: Thanks, kid! No one could\n"
	.string "understand a word that I said.\p"
	.string "I couldn't work that way.\n"
	.string "Let me give you something for\l"
	.string "your trouble.\p"
	.string "Every Thursday I bring SCYTHER and\n"
	.string "PINSIR up from my SAFARI ZONE.\p"
	.string "Only my guests may enter, and from\n"
	.string "today, you're on my list for life!\p"
	.string "Talk to me any Thursday and I'll\n"
	.string "sign you in myself.$"
Gate_NationalPark_Text_WardenHost:
	.string "WARDEN: Fwahaha! My honored guest!\n"
	.string "My SCYTHER and PINSIR are restless\l"
	.string "in the grass today.\p"
	.string "Let's get you signed in!$"

Gate_NationalPark_Text_Thursday:
	.string "The old man in the hat is the\n"
	.string "SAFARI ZONE WARDEN.\p"
	.string "He sponsors today's contest and\n"
	.string "brings SCYTHER and PINSIR himself.\p"
	.string "Entry is by his invitation only.\n"
	.string "Mind, since he lost his gold teeth,\l"
	.string "nobody can understand him.\p"
	.string "Tuesday and Saturday contests\n"
	.string "are open to everyone.$"

Gate_NationalPark_Text_Schedule:
	.string "The Bug-Catching Contest is held\n"
	.string "Tuesday, Thursday, and Saturday.\p"
	.string "Thursday is the SAFARI ZONE\n"
	.string "WARDEN's round, for his guests.\p"
	.string "Ask the attendant to enter.\n"
	.string "The park is open every day!$"
Gate_NationalPark_Text_BirdWatcher:
	.string "I come here to watch the Pokémon\n"
	.string "in the park. It's a peaceful place.$"
Gate_NationalPark_Text_Contestant:
	.string "The Bug-Catching Contest is today!\n"
	.string "We're gathering by the park door.\p"
	.string "You can keep one bug Pokémon\n"
	.string "you catch during the contest.\p"
	.string "A strong, healthy catch scores well!$"
Gate_NationalPark_Text_Visitor:
	.string "This gate leads to ROUTE 36.\n"
	.string "The south gate leads to ROUTE 35.$"
