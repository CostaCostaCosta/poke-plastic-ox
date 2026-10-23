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
	return

Gate_NationalPark_ContestDay::
	clearflag FLAG_POX_HIDE_PARK_CONTEST_CROWD
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
	msgbox Gate_NationalPark_Text_Schedule, MSGBOX_NPC
	end

Gate_NationalPark_EventScript_BirdWatcher::
	msgbox Gate_NationalPark_Text_BirdWatcher, MSGBOX_NPC
	end

Gate_NationalPark_EventScript_Contestant::
	msgbox Gate_NationalPark_Text_Contestant, MSGBOX_NPC
	end

Gate_NationalPark_EventScript_Visitor::
	msgbox Gate_NationalPark_Text_Visitor, MSGBOX_NPC
	end

Gate_NationalPark_Text_Schedule:
	.string "The Bug-Catching Contest is held\n"
	.string "Tuesday, Thursday, and Saturday.\p"
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
