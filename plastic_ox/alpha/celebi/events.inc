@ Celebi at the Ilex Forest shrine (bible: Celebi — Ilex Forest).
@ Installed by plastic_ox/alpha/celebi.py.

@ Called from the Ilex arrival script. Temp flag 1 hides the sage until the
@ Burned Tower scatters the legendaries and again once Celebi is caught. Temp
@ flag 2 hides Celebi until the player has handed the GS BALL to the sage.
PoxCelebi_IlexArrival::
	call_if_unset FLAG_POX_STORY_BURNED_TOWER, PoxCelebi_IlexHide
	call_if_set FLAG_POX_CAUGHT_CELEBI, PoxCelebi_IlexHide
	call_if_unset FLAG_POX_CELEBI_GS_BALL_GIVEN, PoxCelebi_IlexHideCelebi
	return
PoxCelebi_IlexHide::
	setflag FLAG_TEMP_1
	setflag FLAG_TEMP_2
	return
PoxCelebi_IlexHideCelebi::
	setflag FLAG_TEMP_2
	return

@ The sage waits for the GS BALL. Once it is handed over and laid on the
@ shrine, Celebi appears and the shared sage + legendary battle runs.
PoxCelebi_Sage::
	lockall
	goto_if_set FLAG_POX_CELEBI_GS_BALL_GIVEN, PoxCelebi_SageBattle
	checkitem ITEM_GS_BALL
	goto_if_eq VAR_RESULT, FALSE, PoxCelebi_SageWaiting
	msgbox PoxCelebi_Text_Offer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, PoxCelebi_SageKeep
	removeitem ITEM_GS_BALL
	setflag FLAG_POX_CELEBI_GS_BALL_GIVEN
	msgbox PoxCelebi_Text_Placed, MSGBOX_DEFAULT
	closemessage
	playse SE_M_HEAL_BELL
	waitse
	@ Celebi drifts down from the canopy onto the shrine clearing; its
	@ permanent spot is restored so later visits find it at the shrine.
	setobjectxyperm LOCALID_POX_CELEBI, 24, 22
	clearflag FLAG_TEMP_2
	addobject LOCALID_POX_CELEBI
	playmoncry SPECIES_CELEBI, CRY_MODE_NORMAL
	applymovement LOCALID_POX_CELEBI, PoxCelebi_Descend
	waitmovement 0
	waitmoncry
	setobjectxyperm LOCALID_POX_CELEBI, 24, 26
	goto PoxCelebi_SageBattle
PoxCelebi_Descend:
	walk_slow_down
	walk_slow_down
	walk_in_place_slow_down
	walk_slow_down
	walk_slow_down
	face_down
	step_end

PoxCelebi_SageWaiting::
	msgbox PoxCelebi_Text_Waiting, MSGBOX_DEFAULT
	releaseall
	end
PoxCelebi_SageKeep::
	msgbox PoxCelebi_Text_Keep, MSGBOX_DEFAULT
	releaseall
	end

pox_legendary_sage PoxCelebi_SageBattle, TRAINER_PLASTIC_OX_CELEBI_SAGE, SPECIES_CELEBI, 55, FLAG_POX_CAUGHT_CELEBI, LOCALID_POX_CELEBI_SAGE, LOCALID_POX_CELEBI, PoxCelebi_Text_Sage, PoxCelebi_Text_SageDefeat

PoxCelebi_Text_Waiting::
	.string "SAGE: Shh. Something lives in this\n"
	.string "clearing. It will not show itself.\p"
	.string "The forest is waiting for something\n"
	.string "to be brought back to it.\p"
	.string "I do not know what. I only know\n"
	.string "that it is not me.$"

PoxCelebi_Text_Offer::
	.string "SAGE: That ball in your bag. The\n"
	.string "leaves went still when you came in.\p"
	.string "May I lay it on the shrine?$"

PoxCelebi_Text_Keep::
	.string "SAGE: Then I will keep waiting.\n"
	.string "The forest is patient. So am I.$"

PoxCelebi_Text_Placed::
	.string "The SAGE set the GS BALL on the\n"
	.string "shrine. Its seal gave way.$"

PoxCelebi_Text_Sage::
	.string "SAGE: There it is. MORTY told me\n"
	.string "to wait until it felt safe.\p"
	.string "One battle, so I can be sure it is\n"
	.string "safe with you.$"

PoxCelebi_Text_SageDefeat::
	.string "SAGE: Quietly done.\n"
	.string "CELEBI is yours to ask.$"
