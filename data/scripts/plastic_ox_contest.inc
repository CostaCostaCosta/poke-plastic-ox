PlasticOxContest_EventScript_Attendant::
	lock
	faceplayer
	checkflag FLAG_POX_CONTEST_PRIZE_PENDING
	goto_if TRUE, PlasticOxContest_EventScript_Prize
	special PlasticOxContest_Status
	compare VAR_RESULT, 0
	goto_if_ne PlasticOxContest_EventScript_Retire
	msgbox PlasticOxContest_Text_Enter, MSGBOX_YESNO
	compare VAR_RESULT, YES
	goto_if_ne PlasticOxContest_EventScript_Release
	special PlasticOxContest_Start
	compare VAR_RESULT, TRUE
	goto_if_ne PlasticOxContest_EventScript_NoRoom
	msgbox PlasticOxContest_Text_Started, MSGBOX_DEFAULT
	goto PlasticOxContest_EventScript_Release

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
	special PlasticOxContest_Judge
	compare VAR_RESULT, 4
	goto_if_eq PlasticOxContest_EventScript_DeliveryBlocked
	compare VAR_RESULT, 0
	goto_if_eq PlasticOxContest_EventScript_NoCatch
	compare VAR_RESULT, 1
	goto_if_eq PlasticOxContest_EventScript_Winner
	compare VAR_RESULT, 2
	goto_if_eq PlasticOxContest_EventScript_Second
	msgbox PlasticOxContest_Text_Third, MSGBOX_DEFAULT
	goto PlasticOxContest_EventScript_Release
PlasticOxContest_EventScript_Second::
	msgbox PlasticOxContest_Text_Second, MSGBOX_DEFAULT
	goto PlasticOxContest_EventScript_Release
PlasticOxContest_EventScript_Winner::
	msgbox PlasticOxContest_Text_Winner, MSGBOX_DEFAULT
PlasticOxContest_EventScript_Prize::
	special PlasticOxContest_ClaimPrize
	compare VAR_RESULT, TRUE
	goto_if_ne PlasticOxContest_EventScript_BagFull
	playfanfare MUS_OBTAIN_ITEM
	msgbox PlasticOxContest_Text_Prize, MSGBOX_DEFAULT
	waitfanfare
	goto PlasticOxContest_EventScript_Release
PlasticOxContest_EventScript_BagFull::
	msgbox PlasticOxContest_Text_BagFull, MSGBOX_DEFAULT
	goto PlasticOxContest_EventScript_Release
PlasticOxContest_EventScript_NoRoom::
	msgbox PlasticOxContest_Text_NoRoom, MSGBOX_DEFAULT
	goto PlasticOxContest_EventScript_Release
PlasticOxContest_EventScript_DeliveryBlocked::
	msgbox PlasticOxContest_Text_DeliveryBlocked, MSGBOX_DEFAULT
	goto PlasticOxContest_EventScript_Release
PlasticOxContest_EventScript_NoCatch::
	msgbox PlasticOxContest_Text_NoCatch, MSGBOX_DEFAULT
PlasticOxContest_EventScript_Release::
	releaseall
	end

PlasticOxContest_Text_Enter:
	.string "The Bug-Catching Contest is open\n"
	.string "every day! Would you like to enter?\p"
	.string "You get 20 contest balls and 500\n"
	.string "steps. Keep just one caught Pokémon.\p"
	.string "You can replace it with a later catch.\n"
	.string "Species, level, condition, and natural\l"
	.string "strength determine the score.\p"
	.string "First place wins a Sun Stone!\n"
	.string "You keep your chosen Pokémon.\p"
	.string "Saving is unavailable during a round.\n"
	.string "Enter the contest?$"
PlasticOxContest_Text_Started:
	.string "Your contest starts now! Search the\n"
	.string "grass for Bug Pokémon.\p"
	.string "Choose RETIRE or speak to me to judge\n"
	.string "early. Leaving the park also ends\l"
	.string "the round and keeps your catch.\p"
	.string "Your own party stays safely with you.\n"
	.string "Good luck!$"
PlasticOxContest_Text_Retire:
	.string "Shall we end your round and judge\n"
	.string "your chosen Bug Pokémon now?$"
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
	.string "Your chosen Pokémon has joined your\n"
	.string "party or been sent to your PC.$"
PlasticOxContest_Text_Second:
	.string "Your entry scored {STR_VAR_1} points!\n"
	.string "You took second place. Well done!\p"
	.string "Your chosen Pokémon is in your party\n"
	.string "or PC. Try again for a Sun Stone!$"
PlasticOxContest_Text_Third:
	.string "Your entry scored {STR_VAR_1} points!\n"
	.string "You finished third this round.\p"
	.string "Your chosen Pokémon is in your party\n"
	.string "or PC. You can enter again anytime!$"
PlasticOxContest_Text_Prize:
	.string "{PLAYER} received a Sun Stone!\p"
	.string "Come back for another round anytime!$"
PlasticOxContest_Text_BagFull:
	.string "Your Bag is full. Your Sun Stone is\n"
	.string "safe with me. Make room and return!$"
PlasticOxContest_Text_NoRoom:
	.string "Please make room for your contest\n"
	.string "catch in your party or PC first.$"
PlasticOxContest_Text_DeliveryBlocked:
	.string "Your party and PC are both full!\n"
	.string "Your chosen Pokémon is safe with us.\p"
	.string "Make space, then ask for judging\n"
	.string "again to receive it.$"
PlasticOxContest_Text_NoCatch:
	.string "You did not retain a Pokémon, so\n"
	.string "there is no entry to judge.\p"
	.string "The next contest is open already.\n"
	.string "You can try again anytime!$"
