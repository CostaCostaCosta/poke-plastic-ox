MtSilver_SummitDay_hns_MapScripts::
	.byte 0

@ Cerulean Cave summit: RED and MEWTWO, the post-game final battle.
@ Winning shows the player's trainer card, then the Hall of Fame (team and
@ player record) and the credits via GameClear. RED then rests
@ (FLAG_POX_RED_RESTING) until the player wins the League again; PoxLeague_Hall
@ clears the flag, so every new Hall of Fame entry brings him back for a rematch.
@ While RED rests, MEWTWO stays as a reward encounter: any ball catches it.
PoxCeruleanCave_Mewtwo::
	lock
	goto_if_set FLAG_POX_CAUGHT_MEWTWO, PoxCeruleanCave_MewtwoEnd
	goto_if_set FLAG_POX_RED_RESTING, PoxCeruleanCave_MewtwoReward
	playmoncry SPECIES_MEWTWO, CRY_MODE_ENCOUNTER
	msgbox PoxCeruleanCave_Text_Mewtwo, MSGBOX_DEFAULT
	waitmoncry
	goto PoxCeruleanCave_RedBattle

PoxCeruleanCave_MewtwoReward::
	playmoncry SPECIES_MEWTWO, CRY_MODE_ENCOUNTER
	waitmoncry
	msgbox PoxCeruleanCave_Text_MewtwoReward, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, PoxCeruleanCave_MewtwoEnd
	closemessage
	setwildbattle SPECIES_MEWTWO, 70, ITEM_NONE
	special BattleSetup_StartLegendaryRewardBattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_ne VAR_RESULT, B_OUTCOME_CAUGHT, PoxCeruleanCave_MewtwoEnd
	setflag FLAG_POX_CAUGHT_MEWTWO
	removeobject LOCALID_CERULEAN_CAVE_MEWTWO
PoxCeruleanCave_MewtwoEnd::
	release
	end

PoxCeruleanCave_Red::
	lock
	faceplayer
PoxCeruleanCave_RedBattle::
	msgbox PoxCeruleanCave_Text_RedIntro, MSGBOX_DEFAULT
	@ Early-rival mode with no flags: an ordinary battle and whiteout, but the
	@ only mode that prints a trainer line ("…") when the player loses.
	trainerbattle_earlyrival TRAINER_PLASTIC_OX_RED, 0, PoxCeruleanCave_Text_RedDefeat, PoxCeruleanCave_Text_RedWon
	setflag FLAG_POX_RED_RESTING
	msgbox PoxCeruleanCave_Text_RedAfter, MSGBOX_DEFAULT
	closemessage
	fadescreen FADE_TO_BLACK
	special PoxShowPlayerTrainerCard
	setrespawn HEAL_LOCATION_POX_INDIGO
	fadescreenspeed FADE_TO_BLACK, 24
	special GameClear
	releaseall
	end

PoxCeruleanCave_Text_Mewtwo::
	.string "MEWTWO's eyes fix on you.\n"
	.string "It doesn't leave the TRAINER's side.$"

PoxCeruleanCave_Text_MewtwoReward::
	.string "RED is gone. MEWTWO stayed behind,\n"
	.string "watching you. It seems to be waiting.\p"
	.string "Throw any BALL and it will join you.\n"
	.string "Approach MEWTWO?$"

PoxCeruleanCave_Text_RedIntro::
	.string "……………… ………………$"

PoxCeruleanCave_Text_RedDefeat::
	.string "…!$"

PoxCeruleanCave_Text_RedWon::
	.string "…$"

PoxCeruleanCave_Text_RedAfter::
	.string "……………… ………………$"
