PoxCinnabar_MansionLocked::
	lockall
	msgbox PoxCinnabar_Text_Locked, MSGBOX_DEFAULT
	releaseall
	end

PoxCinnabar_Text_Locked::
	.string "The MANSION door is locked.\p"
	.string "BLAINE holds the MANSION KEY.\n"
	.string "Challenge him at the GYM first.$"

PoxCinnabar_MansionGuide::
	lockall
	checkitem ITEM_SECRET_KEY
	goto_if_eq VAR_RESULT, FALSE, PoxCinnabar_MansionLocked
	msgbox PoxCinnabar_Text_Explore, MSGBOX_DEFAULT
	releaseall
	end

PoxCinnabar_Text_Explore::
	.string "Your MANSION KEY opens the door.\n"
	.string "The statues conceal secret switches.\p"
	.string "A SAGE guards a fiery POKéMON\n"
	.string "deep in the basement.$"

PoxCinnabar_GymGuide::
	msgbox PoxCinnabar_Text_Gym, MSGBOX_NPC
	end

PoxCinnabar_Text_Gym::
	.string "BLAINE welcomes challengers.\n"
	.string "The GYM door is open!$"

pox_legendary_sage PoxCinnabar_EnteiSage, TRAINER_PLASTIC_OX_ENTEI_SAGE, SPECIES_ENTEI, 45, FLAG_POX_ENTEI, LOCALID_POX_ENTEI_SAGE, LOCALID_POX_ENTEI, PoxCinnabar_Text_Sage, PoxCinnabar_Text_SageDefeat

PoxCinnabar_Text_Sage::
	.string "SAGE: MORTY sent me to help the\n"
	.string "displaced legendary POKéMON.\p"
	.string "I found ENTEI here and stayed\n"
	.string "to help it feel safe again.\p"
	.string "SAGE: ENTEI's fire tests the bonds\n"
	.string "between people and POKéMON.\p"
	.string "Face my team, with ENTEI at my side.\n"
	.string "Show us the strength of your bond!$"

PoxCinnabar_Text_SageDefeat::
	.string "Your bond burns bright.\n"
	.string "ENTEI has chosen you.$"
