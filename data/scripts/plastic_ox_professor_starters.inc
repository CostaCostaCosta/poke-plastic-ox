@ Professor starter rewards. Each professor sets VAR_0x8004 and jumps to
@ PoxProf_Talk; the counting and flags live in src/plastic_ox_professor_starters.c.
@ VAR_0x8004: 0 = OAK (KANTO), 1 = ELM (JOHTO), 2 = BIRCH (HOENN).

PoxProf_Oak::
	lock
	faceplayer
	setvar VAR_0x8004, 0
	call PoxProf_Talk
	release
	end

PoxProf_Elm::
	lock
	faceplayer
	setvar VAR_0x8004, 1
	call PoxProf_Talk
	release
	end

PoxProf_Birch::
	lock
	faceplayer
	setvar VAR_0x8004, 2
	call PoxProf_Talk
	release
	end

@ Callable: returns to the caller, which owns lock/release.
PoxProf_Talk::
	special PoxProfStarters_Status
	copyvar VAR_0x8008, VAR_RESULT
	goto_if_eq VAR_0x8008, 2, PoxProf_Complete
	call_if_eq VAR_0x8005, 0, PoxProf_Intro
	goto_if_eq VAR_0x8008, 0, PoxProf_Progress
	msgbox PoxProf_Text_Reward, MSGBOX_DEFAULT
	special PoxProfStarters_BufferChoices
	call_if_eq VAR_0x8005, TRUE, PoxProf_PushFirst
	call_if_eq VAR_0x8006, TRUE, PoxProf_PushSecond
	call_if_eq VAR_0x8007, TRUE, PoxProf_PushThird
	dynmultipush PoxProf_Text_Cancel, 3
	dynmultistack 0, 0, FALSE, 4, FALSE, 0, DYN_MULTICHOICE_CB_NONE
	goto_if_ge VAR_RESULT, 3, PoxProf_Declined
	copyvar VAR_0x8005, VAR_RESULT
	special PoxProfStarters_GetChoice
	goto_if_eq VAR_0x8006, SPECIES_NONE, PoxProf_Declined
	givemon VAR_0x8006, 5
	goto_if_eq VAR_RESULT, MON_CANT_GIVE, PoxProf_NoRoom
	copyvar VAR_0x8009, VAR_RESULT
	special PoxProfStarters_Claim
	playfanfare MUS_OBTAIN_ITEM
	msgbox PoxProf_Text_Received, MSGBOX_DEFAULT
	waitfanfare
	call_if_eq VAR_0x8009, MON_GIVEN_TO_PC, PoxProf_SentToPC
	msgbox PoxProf_Text_TakeCare, MSGBOX_DEFAULT
	return

PoxProf_PushFirst::
	dynmultipush PoxProf_Text_Option1, 0
	return
PoxProf_PushSecond::
	dynmultipush PoxProf_Text_Option2, 1
	return
PoxProf_PushThird::
	dynmultipush PoxProf_Text_Option3, 2
	return

PoxProf_Intro::
	call_if_eq VAR_0x8004, 0, PoxProf_IntroOak
	call_if_eq VAR_0x8004, 1, PoxProf_IntroElm
	call_if_eq VAR_0x8004, 2, PoxProf_IntroBirch
	return
PoxProf_IntroOak::
	msgbox PoxProf_Text_IntroOak, MSGBOX_DEFAULT
	return
PoxProf_IntroElm::
	msgbox PoxProf_Text_IntroElm, MSGBOX_DEFAULT
	return
PoxProf_IntroBirch::
	msgbox PoxProf_Text_IntroBirch, MSGBOX_DEFAULT
	return

PoxProf_Progress::
	msgbox PoxProf_Text_Progress, MSGBOX_DEFAULT
	return

PoxProf_Complete::
	msgbox PoxProf_Text_Complete, MSGBOX_DEFAULT
	return

PoxProf_Declined::
	msgbox PoxProf_Text_Declined, MSGBOX_DEFAULT
	return

PoxProf_NoRoom::
	msgbox PoxProf_Text_NoRoom, MSGBOX_DEFAULT
	return

PoxProf_SentToPC::
	msgbox PoxProf_Text_SentToPC, MSGBOX_DEFAULT
	return

PoxProf_Text_IntroOak::
	.string "I'm PROFESSOR OAK!\p"
	.string "I've spent many years studying\n"
	.string "the POKéMON of KANTO.\p"
	.string "For every 25 different KANTO\n"
	.string "POKéMON you register in your\l"
	.string "POKéDEX, I'll give you one of the\l"
	.string "region's starter POKéMON!$"

PoxProf_Text_IntroElm::
	.string "Hello! I'm PROFESSOR ELM.\p"
	.string "I've moved my research here to\n"
	.string "GOLDENROD CITY to continue\l"
	.string "studying JOHTO's POKéMON.\p"
	.string "Register 25 different JOHTO\n"
	.string "POKéMON in your POKéDEX, and I'll\l"
	.string "reward you with a starter POKéMON!\p"
	.string "You can earn another for every\n"
	.string "25 you register!$"

PoxProf_Text_IntroBirch::
	.string "Hey there! I'm PROFESSOR BIRCH!\p"
	.string "I've set up my research here in\n"
	.string "FORTREE CITY. The surrounding\l"
	.string "wilderness is perfect for studying\l"
	.string "POKéMON!\p"
	.string "I'm looking for TRAINERS who can\n"
	.string "help document HOENN's POKéMON.\p"
	.string "For every 25 different HOENN\n"
	.string "POKéMON you register, I'll reward\l"
	.string "you with one of our starter POKéMON!$"

PoxProf_Text_Progress::
	.string "You've registered {STR_VAR_1} {STR_VAR_2}\n"
	.string "POKéMON!\p"
	.string "Your next reward is at {STR_VAR_3}!$"

PoxProf_Text_Reward::
	.string "Excellent! You've registered\n"
	.string "{STR_VAR_1} {STR_VAR_2} POKéMON!\p"
	.string "You've earned a starter POKéMON!\p"
	.string "Which one would you like?$"

PoxProf_Text_Option1::
	.string "{STR_VAR_1}$"
PoxProf_Text_Option2::
	.string "{STR_VAR_2}$"
PoxProf_Text_Option3::
	.string "{STR_VAR_3}$"
PoxProf_Text_Cancel::
	.string "CANCEL$"

PoxProf_Text_Received::
	.string "{PLAYER} received {STR_VAR_1}!$"

PoxProf_Text_SentToPC::
	.string "Your party is full, so {STR_VAR_1}\n"
	.string "was sent to the PC.$"

PoxProf_Text_TakeCare::
	.string "Raise it well! Keep filling that\n"
	.string "POKéDEX for your next reward.$"

PoxProf_Text_Declined::
	.string "Take your time deciding. Your\n"
	.string "reward will be waiting for you.$"

PoxProf_Text_NoRoom::
	.string "Oh! Your party and PC boxes are\n"
	.string "full. Make some room, then come\l"
	.string "back for your reward.$"

PoxProf_Text_Complete::
	.string "Amazing! You've earned all three\n"
	.string "starter POKéMON!\p"
	.string "Keep exploring! There's still so\n"
	.string "much to learn about POKéMON!$"
