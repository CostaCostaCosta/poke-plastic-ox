@ Tin Tower: the sages come home, the stair opens at five, Moltres waits on the roof.
@ Installed by plastic_ox/alpha/tin_tower.py.

@ A sage is home once their legendary is caught (the shared reward script sets
@ the caught flag only after the sage is beaten and the capture succeeds).
PoxTinTower_CountSages::
	setvar VAR_TEMP_1, 0
	call_if_set FLAG_POX_ENTEI, PoxTinTower_AddSage
	call_if_set FLAG_POX_HIDE_ARTICUNO, PoxTinTower_AddSage
	call_if_set FLAG_POX_CAUGHT_RAIKOU, PoxTinTower_AddSage
	call_if_set FLAG_POX_CAUGHT_REGIROCK, PoxTinTower_AddSage
	call_if_set FLAG_POX_CAUGHT_REGICE, PoxTinTower_AddSage
	call_if_set FLAG_POX_CAUGHT_REGISTEEL, PoxTinTower_AddSage
	call_if_set FLAG_POX_CAUGHT_JIRACHI, PoxTinTower_AddSage
	return
PoxTinTower_AddSage::
	addvar VAR_TEMP_1, 1
	return

@ Temp flags hide the sages who are still away; they reset on every map load.
PoxTinTower_Office_OnTransition::
	call_if_unset FLAG_POX_ENTEI, PoxTinTower_AwayEntei
	call_if_unset FLAG_POX_HIDE_ARTICUNO, PoxTinTower_AwayArticuno
	call_if_unset FLAG_POX_CAUGHT_RAIKOU, PoxTinTower_AwayRaikou
	call_if_unset FLAG_POX_CAUGHT_REGIROCK, PoxTinTower_AwayRegirock
	call_if_unset FLAG_POX_CAUGHT_REGICE, PoxTinTower_AwayRegice
	call_if_unset FLAG_POX_CAUGHT_REGISTEEL, PoxTinTower_AwayRegisteel
	call_if_unset FLAG_POX_CAUGHT_JIRACHI, PoxTinTower_AwayJirachi
	call PoxTinTower_CountSages
	goto_if_lt VAR_TEMP_1, 5, PoxTinTower_Office_End
	setobjectxyperm LOCALID_POX_TIN_TOWER_KEEPER, 8, 4
	setobjectmovementtype LOCALID_POX_TIN_TOWER_KEEPER, MOVEMENT_TYPE_FACE_DOWN
PoxTinTower_Office_End::
	end
PoxTinTower_AwayEntei::
	setflag FLAG_TEMP_1
	return
PoxTinTower_AwayArticuno::
	setflag FLAG_TEMP_2
	return
PoxTinTower_AwayRaikou::
	setflag FLAG_TEMP_3
	return
PoxTinTower_AwayRegirock::
	setflag FLAG_TEMP_4
	return
PoxTinTower_AwayRegice::
	setflag FLAG_TEMP_5
	return
PoxTinTower_AwayRegisteel::
	setflag FLAG_TEMP_6
	return
PoxTinTower_AwayJirachi::
	setflag FLAG_TEMP_7
	return

PoxTinTower_Keeper::
	lock
	faceplayer
	call PoxTinTower_CountSages
	goto_if_ge VAR_TEMP_1, 5, PoxTinTower_Keeper_Open
	buffernumberstring STR_VAR_1, VAR_TEMP_1
	msgbox PoxTinTower_Text_KeeperShut, MSGBOX_DEFAULT
	release
	end
PoxTinTower_Keeper_Open::
	msgbox PoxTinTower_Text_KeeperOpen, MSGBOX_DEFAULT
	release
	end

PoxTinTower_SageEntei::
	msgbox PoxTinTower_Text_SageEntei, MSGBOX_NPC
	end
PoxTinTower_SageArticuno::
	msgbox PoxTinTower_Text_SageArticuno, MSGBOX_NPC
	end
PoxTinTower_SageRaikou::
	msgbox PoxTinTower_Text_SageRaikou, MSGBOX_NPC
	end
PoxTinTower_SageRegirock::
	msgbox PoxTinTower_Text_SageRegirock, MSGBOX_NPC
	end
PoxTinTower_SageRegice::
	msgbox PoxTinTower_Text_SageRegice, MSGBOX_NPC
	end
PoxTinTower_SageRegisteel::
	msgbox PoxTinTower_Text_SageRegisteel, MSGBOX_NPC
	end
PoxTinTower_SageJirachi::
	msgbox PoxTinTower_Text_SageJirachi, MSGBOX_NPC
	end

pox_legendary_sage PoxTinTower_MoltresSage, TRAINER_PLASTIC_OX_MOLTRES_SAGE, SPECIES_MOLTRES, 55, FLAG_POX_CAUGHT_MOLTRES, LOCALID_POX_MOLTRES_SAGE, LOCALID_POX_MOLTRES, PoxTinTower_Text_MoltresSage, PoxTinTower_Text_MoltresSageDefeat

PoxTinTower_Text_KeeperShut::
	.string "The stair to the TIN TOWER stays\n"
	.string "shut until the sages come home.\p"
	.string "MORTY's rule, not mine. I count\n"
	.string "five before I open this door.\p"
	.string "So far I have counted {STR_VAR_1}.$"

PoxTinTower_Text_KeeperOpen::
	.string "Five came home. The door is open.\p"
	.string "One more went up the stair and has\n"
	.string "not come down. Mind the ladders.\l"
	.string "They are older than I am.$"

PoxTinTower_Text_SageEntei::
	.string "That mansion had a cold kitchen\n"
	.string "and a hot cellar. ENTEI chose the\l"
	.string "cellar.\p"
	.string "I came home with shorter eyebrows\n"
	.string "and a very long report.$"

PoxTinTower_Text_SageArticuno::
	.string "My ink froze in the pot at\n"
	.string "SEAFOAM. I wrote the last month\l"
	.string "in pencil.\p"
	.string "ARTICUNO is with you now, so I am\n"
	.string "allowed to thaw.$"

PoxTinTower_Text_SageRaikou::
	.string "NEW MAUVILLE hums all night. I\n"
	.string "slept with cotton in my ears for\l"
	.string "a whole season.\p"
	.string "The quiet in this office is the\n"
	.string "loudest thing I have heard.$"

PoxTinTower_Text_SageRegirock::
	.string "I swept the sand out of those\n"
	.string "ruins every morning, and the wind\l"
	.string "swept it back every afternoon.\p"
	.string "REGIROCK never minded either way.\n"
	.string "I think it liked the broom.$"

PoxTinTower_Text_SageRegice::
	.string "The island cave never drips. I\n"
	.string "listened for a month to be sure.\p"
	.string "Not once. I still do not know\n"
	.string "what to write about that.$"

PoxTinTower_Text_SageRegisteel::
	.string "The tomb rang when I knocked on\n"
	.string "the wall, so I stopped knocking.\p"
	.string "REGISTEEL did not stop. You can\n"
	.string "still hear it if you sleep light.$"

PoxTinTower_Text_SageJirachi::
	.string "The falls roared the whole time\n"
	.string "I was down there. I learned to\l"
	.string "read lips.\p"
	.string "The BAGON learned to read mine.\n"
	.string "I miss them more than the quiet.$"

PoxTinTower_Text_MoltresSage::
	.string "SAGE: It came down on this roof\n"
	.string "the night the old bell fell.\p"
	.string "MORTY said to stay until it feels\n"
	.string "safe. Show me it will be safe with\l"
	.string "you.$"

PoxTinTower_Text_MoltresSageDefeat::
	.string "SAGE: Your POKéMON stood in the\n"
	.string "heat and did not step back.\p"
	.string "Then MOLTRES is yours to ask.$"
