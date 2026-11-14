EcruteakCity_Gym_hns_MapScripts::
	.byte 0

PoxEcruteak_EcruteakCity_Gym_hns_0::
	lock
	faceplayer
	msgbox PoxEcruteak_EcruteakCity_Gym_hns_0_Text, MSGBOX_NPC
	release
	end

PoxEcruteak_EcruteakCity_Gym_hns_0_Text:
	.string "The gym is a maze of shadow. Step\nwhere the floor looks solid and\pyou will walk in circles.\pKADO and GENZO keep the lamps.\nYUI keeps the chalk. RIN keeps the\nplast door.\pBeat the ones in your way and\nMORTY will see you at the top.$"

Pox_GymKado::
	trainerbattle_single TRAINER_PLASTIC_OX_ECRUTEAK_KADO, Pox_Text_GymKadoIntro, Pox_Text_GymKadoDefeat
	msgbox Pox_Text_GymKadoAfter, MSGBOX_AUTOCLOSE
	end

Pox_Text_GymKadoIntro:
	.string "Mind the wick. I trim forty before\nthe first challenger and forty\pafter the last.\pYou learn a maze by carrying a\nlight through it.\pShow me you can.$"

Pox_Text_GymKadoDefeat:
	.string "You found the turn. Most people\nfind the wall first.\pGo on. GENZO has the brazier, and\nhe does not give directions.$"

Pox_Text_GymKadoAfter:
	.string "The lamps are half lit on purpose.\nA bright gym is a gym where\pnobody listens.$"

Pox_GymYui::
	trainerbattle_single TRAINER_PLASTIC_OX_ECRUTEAK_YUI, Pox_Text_GymYuiIntro, Pox_Text_GymYuiDefeat
	msgbox Pox_Text_GymYuiAfter, MSGBOX_AUTOCLOSE
	end

Pox_Text_GymYuiIntro:
	.string "Rope on the floor, chalk on the\nrope, follow the chalk.\pThat is the whole maze. I repaint\nit every morning.\pEvery morning someone walks\nstraight through it.\pToday it is you.$"

Pox_Text_GymYuiDefeat:
	.string "You stepped off the chalk and\nstill found me.\pFine. I will repaint it tonight.$"

Pox_Text_GymYuiAfter:
	.string "Lost? Stand still and count the\nlamps. Nine means the floor holds\pfor three more steps.$"

Pox_GymGenzo::
	trainerbattle_single TRAINER_PLASTIC_OX_ECRUTEAK_GENZO, Pox_Text_GymGenzoIntro, Pox_Text_GymGenzoDefeat
	msgbox Pox_Text_GymGenzoAfter, MSGBOX_AUTOCLOSE
	end

Pox_Text_GymGenzoIntro:
	.string "The brazier has burned since the\ntower did. One light in here is\pnot a trick.\pMORTY says the dark is a room,\nnot an enemy. A room still needs\pa fire.\pWarm up.$"

Pox_Text_GymGenzoDefeat:
	.string "Warm enough. The last door is\nRIN's. She is colder than I am.$"

Pox_Text_GymGenzoAfter:
	.string "Take a coal if you go down under\nthe tower. Those stairs hold a\pchill that is not the season.$"

Pox_GymRin::
	trainerbattle_single TRAINER_PLASTIC_OX_ECRUTEAK_RIN, Pox_Text_GymRinIntro, Pox_Text_GymRinDefeat
	msgbox Pox_Text_GymRinAfter, MSGBOX_AUTOCLOSE
	end

Pox_Text_GymRinIntro:
	.string "This is the last turn. Past me the\nfloor stops pretending and MORTY\npis simply there.\pI have watched every challenger\ncome up this stair. Most are\ptalking to themselves by now.\pLet us hear what you sound like.$"

Pox_Text_GymRinDefeat:
	.string "You sound like a challenger.\nGo up.$"

Pox_Text_GymRinAfter:
	.string "He will not explain the tower.\nDo not ask him to.\pAsk what he saw, then listen.$"

PoxEcruteak_EcruteakCity_Gym_hns_Sign0::
	msgbox PoxEcruteak_EcruteakCity_Gym_hns_Sign0_Text, MSGBOX_SIGN
	end

PoxEcruteak_EcruteakCity_Gym_hns_Sign0_Text:
	.string "ECRUTEAK CITY GYM\nKeep to the chalk. Keep your lamp\plit.\pThe floor is not always floor.$"

PoxEcruteak_EcruteakCity_Gym_hns_Sign1::
	msgbox PoxEcruteak_EcruteakCity_Gym_hns_Sign1_Text, MSGBOX_SIGN
	end

PoxEcruteak_EcruteakCity_Gym_hns_Sign1_Text:
	.string "A brass plate lists the GYM\nLEADERs of ECRUTEAK.\pThe newest name is MORTY. The\noldest has worn smooth.$"
