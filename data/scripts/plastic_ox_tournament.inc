@ Authored tournament scripts. Installed by plastic_ox/alpha/tournament.py.
PoxTournament_Host::
	lockall
	faceplayer

	goto_if_unset FLAG_POX_TOURNAMENT_REWARD_1, PoxTournament_Host1

	goto_if_unset FLAG_POX_TOURNAMENT_REWARD_2, PoxTournament_Host2

	goto_if_unset FLAG_POX_TOURNAMENT_REWARD_3, PoxTournament_Host3

	goto_if_unset FLAG_POX_TOURNAMENT_REWARD_4, PoxTournament_Host4

	msgbox PoxTournament_Text_Done, MSGBOX_DEFAULT
	goto PoxTournament_End

PoxTournament_Host1::
	goto_if_defeated TRAINER_PLASTIC_OX_TOURNAMENT_1, PoxTournament_Reward1

	msgbox PoxTournament_Text_Next1, MSGBOX_DEFAULT
	goto PoxTournament_End

PoxTournament_Host2::
	goto_if_defeated TRAINER_PLASTIC_OX_TOURNAMENT_2, PoxTournament_Reward2

	goto_if_set FLAG_BADGE05_GET, PoxTournament_Ready2
	msgbox PoxTournament_Text_Next2, MSGBOX_DEFAULT
	goto PoxTournament_End
PoxTournament_Ready2::
	msgbox PoxTournament_Text_Ready2, MSGBOX_DEFAULT
	goto PoxTournament_End

PoxTournament_Host3::
	goto_if_defeated TRAINER_PLASTIC_OX_TOURNAMENT_3, PoxTournament_Reward3

	goto_if_set FLAG_BADGE06_GET, PoxTournament_Ready3
	msgbox PoxTournament_Text_Next3, MSGBOX_DEFAULT
	goto PoxTournament_End
PoxTournament_Ready3::
	msgbox PoxTournament_Text_Ready3, MSGBOX_DEFAULT
	goto PoxTournament_End

PoxTournament_Host4::
	goto_if_defeated TRAINER_PLASTIC_OX_TOURNAMENT_4, PoxTournament_Reward4

	goto PoxTournament_Check4

PoxTournament_Round1::
	lockall
	faceplayer
PoxTournament_Check1::

	goto_if_set FLAG_POX_TOURNAMENT_REWARD_1, PoxTournament_Won
	goto_if_unset FLAG_BADGE04_GET, PoxTournament_Wait1
	goto_if_defeated TRAINER_PLASTIC_OX_TOURNAMENT_1, PoxTournament_Reward1
	msgbox PoxTournament_Text_Ask1, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, PoxTournament_End
	trainerbattle_single TRAINER_PLASTIC_OX_TOURNAMENT_1, PoxTournament_Text_Intro1, PoxTournament_Text_Defeat1, PoxTournament_Reward1
	goto PoxTournament_Reward1
PoxTournament_Reward1::
	giveitem ITEM_CONTEST_PASS
	goto_if_eq VAR_RESULT, FALSE, PoxTournament_End
	setflag FLAG_POX_TOURNAMENT_REWARD_1
	msgbox PoxTournament_Text_Reward1, MSGBOX_DEFAULT
	goto PoxTournament_End
PoxTournament_Wait1::
	msgbox PoxTournament_Text_Wait1, MSGBOX_DEFAULT
	goto PoxTournament_End

PoxTournament_Round2::
	lockall
	faceplayer
PoxTournament_Check2::

	goto_if_unset FLAG_POX_TOURNAMENT_REWARD_1, PoxTournament_Order

	goto_if_set FLAG_POX_TOURNAMENT_REWARD_2, PoxTournament_Won
	goto_if_unset FLAG_BADGE05_GET, PoxTournament_Wait2
	goto_if_defeated TRAINER_PLASTIC_OX_TOURNAMENT_2, PoxTournament_Reward2
	msgbox PoxTournament_Text_Ask2, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, PoxTournament_End
	trainerbattle_single TRAINER_PLASTIC_OX_TOURNAMENT_2, PoxTournament_Text_Intro2, PoxTournament_Text_Defeat2, PoxTournament_Reward2
	goto PoxTournament_Reward2
PoxTournament_Reward2::
	giveitem ITEM_ANCIENT_BRAILLE_TABLET
	goto_if_eq VAR_RESULT, FALSE, PoxTournament_End
	setflag FLAG_POX_TOURNAMENT_REWARD_2
	msgbox PoxTournament_Text_Reward2, MSGBOX_DEFAULT
	goto PoxTournament_End
PoxTournament_Wait2::
	msgbox PoxTournament_Text_Wait2, MSGBOX_DEFAULT
	goto PoxTournament_End

PoxTournament_Round3::
	lockall
	faceplayer
PoxTournament_Check3::

	goto_if_unset FLAG_POX_TOURNAMENT_REWARD_2, PoxTournament_Order

	goto_if_set FLAG_POX_TOURNAMENT_REWARD_3, PoxTournament_Won
	goto_if_unset FLAG_BADGE06_GET, PoxTournament_Wait3
	goto_if_defeated TRAINER_PLASTIC_OX_TOURNAMENT_3, PoxTournament_Reward3
	msgbox PoxTournament_Text_Ask3, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, PoxTournament_End
	trainerbattle_single TRAINER_PLASTIC_OX_TOURNAMENT_3, PoxTournament_Text_Intro3, PoxTournament_Text_Defeat3, PoxTournament_Reward3
	goto PoxTournament_Reward3
PoxTournament_Reward3::
	giveitem ITEM_NEW_MAUVILLE_KEY
	goto_if_eq VAR_RESULT, FALSE, PoxTournament_End
	setflag FLAG_POX_TOURNAMENT_REWARD_3
	msgbox PoxTournament_Text_Reward3, MSGBOX_DEFAULT
	goto PoxTournament_End
PoxTournament_Wait3::
	msgbox PoxTournament_Text_Wait3, MSGBOX_DEFAULT
	goto PoxTournament_End

PoxTournament_Round4::
	lockall
	faceplayer
PoxTournament_Check4::

	goto_if_unset FLAG_POX_TOURNAMENT_REWARD_3, PoxTournament_Order

	goto_if_set FLAG_POX_TOURNAMENT_REWARD_4, PoxTournament_Won
	goto_if_unset FLAG_POX_LEAGUE_BILL, PoxTournament_Wait4
	goto_if_defeated TRAINER_PLASTIC_OX_TOURNAMENT_4, PoxTournament_Reward4
	msgbox PoxTournament_Text_Ask4, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, PoxTournament_End
	trainerbattle_single TRAINER_PLASTIC_OX_TOURNAMENT_4, PoxTournament_Text_Intro4, PoxTournament_Text_Defeat4, PoxTournament_Reward4
	goto PoxTournament_Reward4
PoxTournament_Reward4::
	giveitem ITEM_RED_ORB
	goto_if_eq VAR_RESULT, FALSE, PoxTournament_End
	setflag FLAG_POX_TOURNAMENT_REWARD_4
	msgbox PoxTournament_Text_Reward4, MSGBOX_DEFAULT
	goto PoxTournament_End
PoxTournament_Wait4::
	msgbox PoxTournament_Text_Wait4, MSGBOX_DEFAULT
	goto PoxTournament_End

PoxTournament_Order::
	msgbox PoxTournament_Text_Order, MSGBOX_DEFAULT
	goto PoxTournament_End
PoxTournament_Won::
	msgbox PoxTournament_Text_Won, MSGBOX_DEFAULT
PoxTournament_End::
	releaseall
	end

PoxTournament_Text_Next1::
	.string "MR. POKéMON: I collect curiosities,\n"
	.string "and promising battle records!\p"
	.string "Our first challenger is IRIS.\n"
	.string "She is standing just to my right.\p"
	.string "Beat her UU team for a pass to\n"
	.string "Thursday's Bug-Catching Contest!$"

PoxTournament_Text_Next2::
	.string "MR. POKéMON: One fine victory!\p"
	.string "CEDRIC is our UUBL challenger.\n"
	.string "He will face you after BLAINE.\p"
	.string "His prize is an ancient tablet\n"
	.string "covered in BRAILLE.$"

PoxTournament_Text_Next3::
	.string "MR. POKéMON: Two wins already!\p"
	.string "Beat TATE and LIZA at MOSSDEEP,\n"
	.string "then try REX and his OU team.\p"
	.string "Win the key to NEW MAUVILLE.\n"
	.string "A sage awaits beyond its generator.$"

PoxTournament_Text_Ask1::
	.string "IRIS: Ready for round one?\n"
	.string "Six partners, one shared purpose!$"

PoxTournament_Text_Ask2::
	.string "CEDRIC: Round two calls for poise.\n"
	.string "Shall we test your UUBL team?$"

PoxTournament_Text_Ask3::
	.string "REX: OU leaves no room for slack!\n"
	.string "Ready for round three?$"

PoxTournament_Text_Ask4::
	.string "MR. POKéMON: A CHAMPION at last!\p"
	.string "My rare partners are more than\n"
	.string "exhibits. Care for the final match?$"

PoxTournament_Text_Intro1::
	.string "IRIS: Every partner has a role!$"

PoxTournament_Text_Intro2::
	.string "CEDRIC: Let us begin!$"

PoxTournament_Text_Intro3::
	.string "REX: Show me your best!$"

PoxTournament_Text_Intro4::
	.string "MR. POKéMON: What a discovery!$"

PoxTournament_Text_Defeat1::
	.string "A beautifully balanced performance!$"

PoxTournament_Text_Defeat2::
	.string "An excellent answer to my tactics!$"

PoxTournament_Text_Defeat3::
	.string "You earned that key!$"

PoxTournament_Text_Defeat4::
	.string "The finest entry in my records!$"

PoxTournament_Text_Wait1::
	.string "IRIS: Earn your fourth BADGE first.\n"
	.string "Then bring your UU partners here.$"

PoxTournament_Text_Wait2::
	.string "CEDRIC: Defeat BLAINE first.\n"
	.string "Then our UUBL round can begin.$"

PoxTournament_Text_Wait3::
	.string "REX: Defeat TATE and LIZA first.\n"
	.string "Then come back for our OU match.$"

PoxTournament_Text_Wait4::
	.string "MR. POKéMON: Three wins! Splendid!\p"
	.string "Defeat the ELITE FOUR and CHAMPION\n"
	.string "BILL, then you and I shall battle.$"

PoxTournament_Text_Reward1::
	.string "Keep that CONTEST PASS! It admits\n"
	.string "you every Thursday at NATIONAL PARK.\p"
	.string "SCYTHER and PINSIR appear in the\n"
	.string "special Bug-Catching Contest.\p"
	.string "Return after BLAINE for round two.$"

PoxTournament_Text_Reward2::
	.string "Take this ancient BRAILLE tablet\n"
	.string "to the SEALED CHAMBER.\p"
	.string "Its inscription speaks of WAILORD\n"
	.string "first and RELICANTH last.\p"
	.string "REGIROCK belongs to the UUBL stage.\n"
	.string "The other seals await your OU BADGE.\p"
	.string "Return after TATE and LIZA\n"
	.string "for the third round.$"

PoxTournament_Text_Reward3::
	.string "Use the NEW MAUVILLE KEY at the\n"
	.string "locked door off ROUTE 110.\p"
	.string "Quiet the generator, then meet\n"
	.string "the sage caring for RAIKOU.\p"
	.string "Become CHAMPION, then return\n"
	.string "for my own challenge!$"

PoxTournament_Text_Reward4::
	.string "This RED ORB is quite a curiosity!\p"
	.string "Show it to MR. STONE at DEVON.\n"
	.string "He studies the legends of GROUDON.$"

PoxTournament_Text_Order::
	.string "Finish the preceding round first.\n"
	.string "MR. POKéMON will explain.$"

PoxTournament_Text_Won::
	.string "Your victory is in our records!\n"
	.string "Speak with MR. POKéMON.$"

PoxTournament_Text_Done::
	.string "MR. POKéMON: All four rounds!\n"
	.string "Your record is a treasure.\p"
	.string "Keep exploring! A collection\n"
	.string "is never truly complete.$"

PoxTournament_Raikou::
	lockall
	goto_if_unset FLAG_BADGE06_GET, PoxTournament_LegendLocked
	checkitem ITEM_NEW_MAUVILLE_KEY
	goto_if_eq VAR_RESULT, FALSE, PoxTournament_LegendLocked
	goto_if_ne VAR_NEW_MAUVILLE_STATE, 2, PoxTournament_PowerOn
	goto PoxTournament_RaikouBattle
PoxTournament_PowerOn::
	msgbox PoxTournament_Text_Power, MSGBOX_DEFAULT
	goto PoxTournament_End
pox_legendary_sage PoxTournament_RaikouBattle, TRAINER_PLASTIC_OX_RAIKOU_SAGE, SPECIES_RAIKOU, 55, FLAG_POX_CAUGHT_RAIKOU, LOCALID_POX_RAIKOU_SAGE, LOCALID_POX_RAIKOU, PoxTournament_Text_Raikou, PoxTournament_Text_SageDefeat
PoxTournament_LegendLocked::
	msgbox PoxTournament_Text_Seal, MSGBOX_DEFAULT
	goto PoxTournament_End

PoxTournament_Regirock::
	lockall
	checkitem ITEM_ANCIENT_BRAILLE_TABLET
	goto_if_eq VAR_RESULT, FALSE, PoxTournament_LegendLocked
	goto_if_unset FLAG_REGI_DOORS_OPENED, PoxTournament_LegendLocked
	goto_if_unset FLAG_BADGE05_GET, PoxTournament_LegendLocked
	goto PoxTournament_RegirockBattle
pox_legendary_sage PoxTournament_RegirockBattle, TRAINER_PLASTIC_OX_REGIROCK_SAGE, SPECIES_REGIROCK, 50, FLAG_POX_CAUGHT_REGIROCK, LOCALID_POX_REGIROCK_SAGE, LOCALID_POX_REGIROCK, PoxTournament_Text_Regi, PoxTournament_Text_SageDefeat

PoxTournament_Regice::
	lockall
	checkitem ITEM_ANCIENT_BRAILLE_TABLET
	goto_if_eq VAR_RESULT, FALSE, PoxTournament_LegendLocked
	goto_if_unset FLAG_REGI_DOORS_OPENED, PoxTournament_LegendLocked
	goto_if_unset FLAG_BADGE06_GET, PoxTournament_LegendLocked
	goto PoxTournament_RegiceBattle
pox_legendary_sage PoxTournament_RegiceBattle, TRAINER_PLASTIC_OX_REGICE_SAGE, SPECIES_REGICE, 55, FLAG_POX_CAUGHT_REGICE, LOCALID_POX_REGICE_SAGE, LOCALID_POX_REGICE, PoxTournament_Text_Regi, PoxTournament_Text_SageDefeat

PoxTournament_Registeel::
	lockall
	checkitem ITEM_ANCIENT_BRAILLE_TABLET
	goto_if_eq VAR_RESULT, FALSE, PoxTournament_LegendLocked
	goto_if_unset FLAG_REGI_DOORS_OPENED, PoxTournament_LegendLocked
	goto_if_unset FLAG_BADGE06_GET, PoxTournament_LegendLocked
	goto PoxTournament_RegisteelBattle
pox_legendary_sage PoxTournament_RegisteelBattle, TRAINER_PLASTIC_OX_REGISTEEL_SAGE, SPECIES_REGISTEEL, 55, FLAG_POX_CAUGHT_REGISTEEL, LOCALID_POX_REGISTEEL_SAGE, LOCALID_POX_REGISTEEL, PoxTournament_Text_Regi, PoxTournament_Text_SageDefeat

PoxTournament_Stone::
	lockall
	faceplayer
	goto_if_unset FLAG_POX_LEAGUE_BILL, PoxTournament_StoneWait
	checkitem ITEM_RED_ORB
	goto_if_eq VAR_RESULT, FALSE, PoxTournament_StoneWait
	setflag FLAG_POX_GROUDON_RESEARCH
	msgbox PoxTournament_Text_StoneOrb, MSGBOX_DEFAULT
	goto PoxTournament_End
PoxTournament_StoneWait::
	msgbox PoxTournament_Text_Stone, MSGBOX_DEFAULT
	goto PoxTournament_End

PoxTournament_Text_Power::
	.string "The generator is upsetting RAIKOU.\n"
	.string "Please find its red stop switch.$"

PoxTournament_Text_Raikou::
	.string "MORTY sent me to help RAIKOU.\p"
	.string "Show us the care and skill\n"
	.string "you give your partners!$"

PoxTournament_Text_Regi::
	.string "These inscriptions led me here.\p"
	.string "Show this ancient POKéMON\n"
	.string "that it can trust you!$"

PoxTournament_Text_SageDefeat::
	.string "You have earned its trust.$"

PoxTournament_Text_Seal::
	.string "The ancient power remains sealed.\n"
	.string "Return when you are ready.$"

PoxTournament_Text_Stone::
	.string "MR. STONE: Ancient stones tell\n"
	.string "stories that books have forgotten.\p"
	.string "I am studying GROUDON. An orb\n"
	.string "from its legend would help greatly.$"

PoxTournament_Text_StoneOrb::
	.string "MR. STONE: The RED ORB! Remarkable!\p"
	.string "Keep it safe. I will compare its\n"
	.string "markings with our GROUDON records.\p"
	.string "Our research has only just begun.$"

PoxTournament_Text_Ready2::
	.string "MR. POKéMON: BLAINE's BADGE!\n"
	.string "CEDRIC is ready for round two.\p"
	.string "He is the gentleman to my right.\n"
	.string "His UUBL team awaits you!$"

PoxTournament_Text_Ready3::
	.string "MR. POKéMON: MOSSDEEP's BADGE!\n"
	.string "REX is ready for round three.\p"
	.string "Find him at the far end of our\n"
	.string "line of challengers. Good luck!$"
