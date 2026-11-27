PoxCinnabar_MansionLocked::
	lockall
	msgbox PoxCinnabar_Text_Locked, MSGBOX_DEFAULT
	releaseall
	end

PoxCinnabar_Text_Locked::
	.string "The door is chained shut. The\n"
	.string "padlock is newer than the house.\p"
	.string "A brass tag on the chain reads:\n"
	.string "“KEY HELD AT THE GYM. BLAINE”$"

@ The islanders who used to carry these labels speak from
@ plastic_ox/alpha/south_isles.py; story scripts still jump here.
PoxCinnabar_MansionGuide::
	goto PoxIsles_MansionGuide

PoxCinnabar_GymGuide::
	goto PoxIsles_GymRegular

pox_legendary_sage PoxCinnabar_EnteiSage, TRAINER_PLASTIC_OX_ENTEI_SAGE, SPECIES_ENTEI, 45, FLAG_POX_ENTEI, LOCALID_POX_ENTEI_SAGE, LOCALID_POX_ENTEI, PoxCinnabar_Text_Sage, PoxCinnabar_Text_SageDefeat

PoxCinnabar_Text_Sage::
	.string "SAGE: Good day. Forgive me for\n"
	.string "not rising. My guest prefers it.\p"
	.string "MORTY asked us to follow those\n"
	.string "who were scattered, and to offer\l"
	.string "them shelter.\p"
	.string "ENTEI came up out of the ash on\n"
	.string "this floor and would not leave.\l"
	.string "I have sat with it since.\p"
	.string "MORTY asked for patience.\n"
	.string "He did not ask for a leash.\p"
	.string "If it is to walk on with anyone,\n"
	.string "I must know with whom. Face my\l"
	.string "team, and ENTEI beside them.$"

PoxCinnabar_Text_SageDefeat::
	.string "It stood when you did.\n"
	.string "I think that is its answer.$"
