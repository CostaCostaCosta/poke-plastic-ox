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

Gate_NationalPark_EventScript_OfficerEast::
	special PoxGetDayOfWeek
	compare VAR_RESULT, WEEKDAY_THU
	goto_if_eq Gate_NationalPark_EventScript_ThursdayEast
	msgbox Gate_NationalPark_Text_ScheduleEast, MSGBOX_NPC
	end

Gate_NationalPark_EventScript_ThursdayEast::
	msgbox Gate_NationalPark_Text_ThursdayEast, MSGBOX_NPC
	end

@ Everyone else in the gate keeps their own line on every day of the week.
Gate_NationalPark_EventScript_BirdWatcher::
	msgbox Gate_NationalPark_Text_BirdWatcher, MSGBOX_NPC
	end

Gate_NationalPark_EventScript_Contestant::
	msgbox Gate_NationalPark_Text_Contestant, MSGBOX_NPC
	end

Gate_NationalPark_EventScript_Contestant2::
	msgbox Gate_NationalPark_Text_Contestant2, MSGBOX_NPC
	end

Gate_NationalPark_EventScript_Contestant3::
	msgbox Gate_NationalPark_Text_Contestant3, MSGBOX_NPC
	end

Gate_NationalPark_EventScript_Contestant4::
	msgbox Gate_NationalPark_Text_Contestant4, MSGBOX_NPC
	end

Gate_NationalPark_EventScript_Contestant5::
	msgbox Gate_NationalPark_Text_Contestant5, MSGBOX_NPC
	end

Gate_NationalPark_EventScript_Contestant6::
	msgbox Gate_NationalPark_Text_Contestant6, MSGBOX_NPC
	end


Gate_NationalPark_EventScript_Visitor::
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
	goto Gate_NationalPark_EventScript_WardenSignIn
Gate_NationalPark_EventScript_WardenHost::
	msgbox Gate_NationalPark_Text_WardenHost, MSGBOX_DEFAULT
@ When today's round is open, the Warden walks his guest over to the south
@ desk himself and stands by while the attendant signs them in. Otherwise
@ (round used, prize waiting...) the desk's own reply is all there is to say.
Gate_NationalPark_EventScript_WardenSignIn::
	special PlasticOxContest_CheckEntry
	goto_if_ne VAR_RESULT, POX_CONTEST_ENTRY_OPEN, Gate_NationalPark_EventScript_WardenDesk
	msgbox Gate_NationalPark_Text_WardenFollowMe, MSGBOX_DEFAULT
	closemessage
	getplayerxy VAR_TEMP_1, VAR_TEMP_2
	goto_if_eq VAR_TEMP_2, 3, Gate_NationalPark_EventScript_WardenFromBelow
	goto_if_lt VAR_TEMP_1, 11, Gate_NationalPark_EventScript_WardenFromLeft
	applymovement LOCALID_PLAYER, Gate_NationalPark_Movement_GuestFromRight
	goto Gate_NationalPark_EventScript_WardenEscort
Gate_NationalPark_EventScript_WardenFromBelow::
	applymovement LOCALID_PLAYER, Gate_NationalPark_Movement_GuestFromBelow
	goto Gate_NationalPark_EventScript_WardenEscort
Gate_NationalPark_EventScript_WardenFromLeft::
	applymovement LOCALID_PLAYER, Gate_NationalPark_Movement_GuestFromLeft
Gate_NationalPark_EventScript_WardenEscort::
	waitmovement 0
	applymovement LOCALID_PARK_WARDEN, Gate_NationalPark_Movement_WardenToDesk
	applymovement LOCALID_PLAYER, Gate_NationalPark_Movement_GuestToDesk
	waitmovement 0
	msgbox Gate_NationalPark_Text_WardenAtDesk, MSGBOX_DEFAULT
	closemessage
Gate_NationalPark_EventScript_WardenDesk::
	setvar VAR_0x8007, 0
	goto PlasticOxContest_EventScript_Attendant

@ The guest steps to (12,3), east of the Warden's first step down.
Gate_NationalPark_Movement_GuestFromRight:
	walk_down
	step_end
Gate_NationalPark_Movement_GuestFromBelow:
	walk_right
	step_end
Gate_NationalPark_Movement_GuestFromLeft:
	walk_down
	walk_right
	walk_right
	step_end
@ Warden (11,2) leads along row 3 and steps aside at (4,4); the guest
@ follows a step behind and stops at the desk, (3,3), facing the attendant.
Gate_NationalPark_Movement_WardenToDesk:
	walk_down
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_down
	face_left
	step_end
Gate_NationalPark_Movement_GuestToDesk:
	delay_16
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	delay_16
	walk_left
	walk_left
	face_up
	step_end

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
	.string "in the grass today.$"
Gate_NationalPark_Text_WardenFollowMe:
	.string "WARDEN: Come along, come along!\n"
	.string "I'll walk you to the desk myself.$"
Gate_NationalPark_Text_WardenAtDesk:
	.string "WARDEN: This one's on my list.\n"
	.string "Sign my guest in, would you?$"

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

Gate_NationalPark_Text_ScheduleEast::
	.string "East gate, ROUTE 36 side.\nContest entrants, please sign in\pwith the attendant here.\pThe park itself is open every\nday.$"

Gate_NationalPark_Text_ThursdayEast::
	.string "Thursday's round belongs to the\nWARDEN. Guests only today, I'm\pafraid.\pHe's the fellow in the hat. Good\nluck understanding a word he\psays.$"

Gate_NationalPark_Text_Contestant2::
	.string "My new net is made for SCYTHER.\nI've practiced swinging it all\pweek!$"

Gate_NationalPark_Text_Contestant3::
	.string "Last time I caught a CATERPIE.\nThis time I want something with\phorns!$"

Gate_NationalPark_Text_Contestant4::
	.string "I'm mostly here for the prize\nBERRIES. Don't tell the judges.$"

Gate_NationalPark_Text_Contestant5::
	.string "The east side of the park has\nthe big bugs. Everybody knows\pthat!$"

Gate_NationalPark_Text_Contestant6::
	.string "I borrowed my brother's VENONAT\nfor luck. He doesn't know yet.$"
