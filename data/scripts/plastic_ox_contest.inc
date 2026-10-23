PlasticOxContest_EventScript_Attendant::
	lock
	faceplayer
	special PlasticOxContest_Status
	compare VAR_RESULT, 1
	goto_if_eq PlasticOxContest_EventScript_Retire
	compare VAR_RESULT, 2
	goto_if_eq PlasticOxContest_EventScript_Finish
	special PlasticOxContest_CheckEntry
	compare VAR_RESULT, POX_CONTEST_ENTRY_PRIZE_PENDING
	goto_if_eq PlasticOxContest_EventScript_AttendantPrize
	compare VAR_RESULT, POX_CONTEST_ENTRY_OPEN
	goto_if_eq PlasticOxContest_EventScript_AttendantOffer
	call PlasticOxContest_EventScript_EntryUnavailable
	goto PlasticOxContest_EventScript_Release
PlasticOxContest_EventScript_AttendantOffer::
	msgbox PlasticOxContest_Text_Enter, MSGBOX_YESNO
	compare VAR_RESULT, YES
	call_if_eq PlasticOxContest_EventScript_Register
	special PlasticOxContest_Status
	compare VAR_RESULT, 1
	goto_if_eq PlasticOxContest_EventScript_EnterPark
	goto PlasticOxContest_EventScript_Release
PlasticOxContest_EventScript_AttendantPrize::
	call PlasticOxContest_EventScript_Prize
	goto PlasticOxContest_EventScript_Release

PlasticOxContest_EventScript_EnterPark::
	compare VAR_0x8007, 0
	goto_if_eq PlasticOxContest_EventScript_EnterSouth
	warp MAP_NATIONAL_PARK_NORMAL_HNS, 39, 19
	waitstate
	releaseall
	end
PlasticOxContest_EventScript_EnterSouth::
	warp MAP_NATIONAL_PARK_NORMAL_HNS, 12, 48
	waitstate
	releaseall
	end

PlasticOxContest_EventScript_EntryUnavailable::
	compare VAR_RESULT, POX_CONTEST_ENTRY_CLOSED
	goto_if_eq PlasticOxContest_EventScript_Closed
	compare VAR_RESULT, POX_CONTEST_ENTRY_USED
	goto_if_eq PlasticOxContest_EventScript_Used
	compare VAR_RESULT, POX_CONTEST_ENTRY_NO_ROOM
	goto_if_eq PlasticOxContest_EventScript_NoRoom
	return
PlasticOxContest_EventScript_Closed::
	msgbox PlasticOxContest_Text_Closed, MSGBOX_DEFAULT
	return
PlasticOxContest_EventScript_Used::
	msgbox PlasticOxContest_Text_Used, MSGBOX_DEFAULT
	return
PlasticOxContest_EventScript_NoRoom::
	msgbox PlasticOxContest_Text_NoRoom, MSGBOX_DEFAULT
	return

PlasticOxContest_EventScript_Register::
	msgbox PlasticOxContest_Text_SelectMon, MSGBOX_DEFAULT
PlasticOxContest_EventScript_SelectMon::
	special ChoosePartyMon
	goto_if_ge VAR_0x8004, PARTY_SIZE, PlasticOxContest_EventScript_CancelRegister
	special PlasticOxContest_Start
	compare VAR_RESULT, POX_CONTEST_ENTRY_INVALID_MON
	goto_if_eq PlasticOxContest_EventScript_InvalidMon
	compare VAR_RESULT, POX_CONTEST_ENTRY_OPEN
	goto_if_ne PlasticOxContest_EventScript_RegisterFailed
	msgbox PlasticOxContest_Text_Started, MSGBOX_DEFAULT
	return
PlasticOxContest_EventScript_InvalidMon::
	msgbox PlasticOxContest_Text_InvalidMon, MSGBOX_DEFAULT
	goto PlasticOxContest_EventScript_SelectMon
PlasticOxContest_EventScript_RegisterFailed::
	msgbox PlasticOxContest_Text_RegisterFailed, MSGBOX_DEFAULT
PlasticOxContest_EventScript_CancelRegister::
	return

PlasticOxContest_EventScript_Retire::
	msgbox PlasticOxContest_Text_Retire, MSGBOX_YESNO
	compare VAR_RESULT, YES
	goto_if_ne PlasticOxContest_EventScript_Release
	goto PlasticOxContest_EventScript_Finish

PlasticOxContest_EventScript_AfterBattle::
	lockall
	compare VAR_0x8005, 0
	goto_if_eq PlasticOxContest_EventScript_FirstCatch
	msgbox PlasticOxContest_Text_Replace, MSGBOX_YESNO
	copyvar VAR_0x8004, VAR_RESULT
	goto PlasticOxContest_EventScript_Accept
PlasticOxContest_EventScript_FirstCatch::
	msgbox PlasticOxContest_Text_FirstCatch, MSGBOX_DEFAULT
	setvar VAR_0x8004, 1
PlasticOxContest_EventScript_Accept::
	special PlasticOxContest_AcceptCatch
	special PlasticOxContest_Status
	compare VAR_0x8006, 0
	goto_if_eq PlasticOxContest_EventScript_Finish
	releaseall
	end

PlasticOxContest_EventScript_Finish::
	lockall
	special PlasticOxContest_GetEntrySide
	compare VAR_RESULT, 0
	goto_if_eq PlasticOxContest_EventScript_ReturnSouth
	warp MAP_GATE_NATIONAL_PARK_HNS, 35, 7
	waitstate
	releaseall
	end
PlasticOxContest_EventScript_ReturnSouth::
	warp MAP_GATE_NATIONAL_PARK_HNS, 7, 2
	waitstate
	releaseall
	end

PlasticOxContest_EventScript_ReportResult::
	compare VAR_RESULT, 4
	goto_if_eq PlasticOxContest_EventScript_DeliveryBlocked
	compare VAR_RESULT, 0
	goto_if_eq PlasticOxContest_EventScript_NoCatch
	compare VAR_RESULT, 1
	goto_if_eq PlasticOxContest_EventScript_Winner
	compare VAR_RESULT, 2
	goto_if_eq PlasticOxContest_EventScript_Second
	msgbox PlasticOxContest_Text_Third, MSGBOX_DEFAULT
	call PlasticOxContest_EventScript_Prize
	return
PlasticOxContest_EventScript_Second::
	msgbox PlasticOxContest_Text_Second, MSGBOX_DEFAULT
	call PlasticOxContest_EventScript_Prize
	return
PlasticOxContest_EventScript_Winner::
	msgbox PlasticOxContest_Text_Winner, MSGBOX_DEFAULT
	call PlasticOxContest_EventScript_Prize
	return
PlasticOxContest_EventScript_Prize::
	special PlasticOxContest_ClaimPrize
	compare VAR_RESULT, TRUE
	goto_if_ne PlasticOxContest_EventScript_BagFull
	playfanfare MUS_OBTAIN_ITEM
	msgbox PlasticOxContest_Text_Prize, MSGBOX_DEFAULT
	waitfanfare
	return
PlasticOxContest_EventScript_BagFull::
	msgbox PlasticOxContest_Text_BagFull, MSGBOX_DEFAULT
	return
PlasticOxContest_EventScript_DeliveryBlocked::
	msgbox PlasticOxContest_Text_DeliveryBlocked, MSGBOX_DEFAULT
	return
PlasticOxContest_EventScript_NoCatch::
	msgbox PlasticOxContest_Text_NoCatch, MSGBOX_DEFAULT
	call PlasticOxContest_EventScript_Prize
	return
PlasticOxContest_EventScript_Release::
	releaseall
	end

PlasticOxContest_Text_Enter:
	.string "The Bug-Catching Contest is held\n"
	.string "Tuesday, Thursday, and Saturday!\p"
	.string "Choose one healthy Pokémon to take\n"
	.string "inside. Your others will wait safely.\p"
	.string "You get 20 Sport Balls and 500\n"
	.string "steps. Keep just one caught Pokémon.\p"
	.string "You can replace it with a later catch.\n"
	.string "Species, level, condition, and natural\l"
	.string "strength determine the score.\p"
	.string "First place wins a Sun Stone!\n"
	.string "Other places win prizes too.\p"
	.string "Your original party returns afterward.\p"
	.string "Saving is unavailable during a round.\n"
	.string "Enter the contest?$"
PlasticOxContest_Text_Started:
	.string "Your contest starts now! Your chosen\n"
	.string "Pokémon will battle the wild bugs.\p"
	.string "Choose RETIRE or speak to me to judge\n"
	.string "early. Leaving the park also ends\l"
	.string "the round and keeps your catch.\p"
	.string "Your other Pokémon will return\n"
	.string "after judging.\n"
	.string "Good luck!$"
PlasticOxContest_Text_SelectMon:
	.string "Which healthy Pokémon will join\n"
	.string "the contest with you?$"
PlasticOxContest_Text_InvalidMon:
	.string "That Pokémon cannot enter. Please\n"
	.string "choose one that is healthy and\l"
	.string "has already hatched.$"
PlasticOxContest_Text_RegisterFailed:
	.string "We cannot start a contest right\n"
	.string "now. Please ask me again.$"
PlasticOxContest_Text_Closed:
	.string "The Bug-Catching Contest runs on\n"
	.string "Tuesday, Thursday, and Saturday.\p"
	.string "The park is open for a normal visit\n"
	.string "today.$"
PlasticOxContest_Text_Used:
	.string "You have already entered today's\n"
	.string "contest. Please come back on the\l"
	.string "next contest day.$"
PlasticOxContest_Text_Retire:
	.string "Shall we end your round and judge\n"
	.string "your caught Pokémon now?$"
PlasticOxContest_Text_Replace:
	.string "You caught {STR_VAR_1}!\n"
	.string "Replace your retained {STR_VAR_2}?\p"
	.string "The Pokémon you do not choose will\n"
	.string "be released back into the park.$"
PlasticOxContest_Text_FirstCatch:
	.string "{STR_VAR_1} is your first entry!\n"
	.string "We will keep it safe for judging.$"
PlasticOxContest_Text_Winner:
	.string "Your entry scored {STR_VAR_1} points!\n"
	.string "Congratulations! You took first place!\p"
	.string "Your caught Pokémon has joined your\n"
	.string "party or been sent to your PC.$"
PlasticOxContest_Text_Second:
	.string "Your entry scored {STR_VAR_1} points!\n"
	.string "You took second place!\n"
	.string "An Everstone is your prize.\p"
	.string "Your caught Pokémon is in your party\n"
	.string "or PC. Try again for a Sun Stone!$"
PlasticOxContest_Text_Third:
	.string "Your entry scored {STR_VAR_1} points!\n"
	.string "You finished third this round!\n"
	.string "A Sitrus Berry is your prize.\p"
	.string "Your caught Pokémon is in your party\n"
	.string "or PC. Try again on another\n"
	.string "contest day!$"
PlasticOxContest_Text_Prize:
	.string "{PLAYER} received a {STR_VAR_2}!\p"
	.string "Come back on another contest day!$"
PlasticOxContest_Text_BagFull:
	.string "Your Bag is full. Your {STR_VAR_2} is\n"
	.string "safe with me. Make room and return!$"
PlasticOxContest_Text_NoRoom:
	.string "Please make room for a catch in\n"
	.string "your party or PC, and for 20 Sport\l"
	.string "Balls in your Bag.$"
PlasticOxContest_Text_DeliveryBlocked:
	.string "Your party and PC are both full!\n"
	.string "Your caught Pokémon is safe with us.\p"
	.string "Make space, then ask for judging\n"
	.string "again to receive it.$"
PlasticOxContest_Text_NoCatch:
	.string "You did not retain a Pokémon, so\n"
	.string "there is no entry to judge.\p"
	.string "You get an Oran Berry for joining.\n"
	.string "Try again on the next\n"
	.string "contest day!$"
PlasticOxContest_EventScript_TrainerRest::
	msgbox PlasticOxContest_Text_TrainerRest, MSGBOX_NPC
	end

PlasticOxContest_Text_TrainerRest:
	.string "Our battles can wait. Good luck\n"
	.string "finding a prize bug!$"
