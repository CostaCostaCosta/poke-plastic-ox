@ Celebi at the Ilex Forest shrine (bible: Celebi — Ilex Forest).
@ Installed by plastic_ox/alpha/celebi.py.

@ Called from the Ilex arrival script. Temp flag 1 hides the sage and Celebi
@ until the Burned Tower scatters the legendaries, and again once Celebi is caught.
PoxCelebi_IlexArrival::
	call_if_unset FLAG_POX_STORY_BURNED_TOWER, PoxCelebi_IlexHide
	call_if_set FLAG_POX_CAUGHT_CELEBI, PoxCelebi_IlexHide
	return
PoxCelebi_IlexHide::
	setflag FLAG_TEMP_1
	return

@ The sage only battles once the player carries the GS BALL.
PoxCelebi_Sage::
	lockall
	checkitem ITEM_GS_BALL
	goto_if_eq VAR_RESULT, FALSE, PoxCelebi_SageWaiting
	goto PoxCelebi_SageBattle
PoxCelebi_SageWaiting::
	msgbox PoxCelebi_Text_Waiting, MSGBOX_DEFAULT
	releaseall
	end

pox_legendary_sage PoxCelebi_SageBattle, TRAINER_PLASTIC_OX_CELEBI_SAGE, SPECIES_CELEBI, 55, FLAG_POX_CAUGHT_CELEBI, LOCALID_POX_CELEBI_SAGE, LOCALID_POX_CELEBI, PoxCelebi_Text_Sage, PoxCelebi_Text_SageDefeat

PoxCelebi_Text_Waiting::
	.string "SAGE: Shh. It is here, behind the\n"
	.string "shrine. It will not come closer.\p"
	.string "The forest is waiting for something\n"
	.string "to be brought back to it.\p"
	.string "I do not know what. I only know\n"
	.string "that it is not me.$"

PoxCelebi_Text_Sage::
	.string "SAGE: That ball in your bag. The\n"
	.string "leaves went still when you came in.\p"
	.string "MORTY told me to wait until it\n"
	.string "felt safe. I think it finally does.\p"
	.string "One battle, so I can be sure.$"

PoxCelebi_Text_SageDefeat::
	.string "SAGE: Quietly done.\n"
	.string "CELEBI is yours to ask.$"
