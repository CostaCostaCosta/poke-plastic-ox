PalletTown_ProfessorOaksLab_Frlg_MapScripts::
	.byte 0

PalletTown_ProfessorOaksLab_EventScript_ProfOak::
	lock
	faceplayer
	msgbox PalletTown_ProfessorOaksLab_Text_ProfOak, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, PalletTown_ProfessorOaksLab_EventScript_ProfOakDeclined
	special GivePlasticOxPlayerParty
	msgbox PalletTown_ProfessorOaksLab_Text_ProfOakTeamGiven, MSGBOX_DEFAULT
	release
	end

PalletTown_ProfessorOaksLab_EventScript_ProfOakDeclined::
	msgbox PalletTown_ProfessorOaksLab_Text_ProfOakDeclined, MSGBOX_DEFAULT
	release
	end

PalletTown_ProfessorOaksLab_EventScript_Rival::
	msgbox PalletTown_ProfessorOaksLab_Text_Visitor, MSGBOX_NPC
	end

PalletTown_ProfessorOaksLab_EventScript_Aide1::
	msgbox PalletTown_ProfessorOaksLab_Text_Aide, MSGBOX_NPC
	end

PalletTown_ProfessorOaksLab_EventScript_Aide2::
	msgbox PalletTown_ProfessorOaksLab_Text_Aide, MSGBOX_NPC
	end

PalletTown_ProfessorOaksLab_EventScript_Aide3::
	msgbox PalletTown_ProfessorOaksLab_Text_Aide, MSGBOX_NPC
	end

PalletTown_ProfessorOaksLab_EventScript_BulbasaurBall::
	msgbox PalletTown_ProfessorOaksLab_Text_PokeBall, MSGBOX_SIGN
	end

PalletTown_ProfessorOaksLab_EventScript_CharmanderBall::
	msgbox PalletTown_ProfessorOaksLab_Text_PokeBall, MSGBOX_SIGN
	end

PalletTown_ProfessorOaksLab_EventScript_SquirtleBall::
	msgbox PalletTown_ProfessorOaksLab_Text_PokeBall, MSGBOX_SIGN
	end

PalletTown_ProfessorOaksLab_EventScript_Pokedex::
	msgbox PalletTown_ProfessorOaksLab_Text_Pokedex, MSGBOX_SIGN
	end

PalletTown_ProfessorOaksLab_EventScript_Computer::
	msgbox PalletTown_ProfessorOaksLab_Text_Computer, MSGBOX_SIGN
	end

PalletTown_ProfessorOaksLab_EventScript_LeftSign::
	msgbox PalletTown_ProfessorOaksLab_Text_Sign, MSGBOX_SIGN
	end

PalletTown_ProfessorOaksLab_EventScript_RightSign::
	msgbox PalletTown_ProfessorOaksLab_Text_Sign, MSGBOX_SIGN
	end

PalletTown_ProfessorOaksLab_Text_ProfOak::
	.string "OAK: I've prepared a complete ADV OU\n"
	.string "team for your battle with LANCE.\p"
	.string "Would you like me to issue it now?$"

PalletTown_ProfessorOaksLab_Text_ProfOakTeamGiven::
	.string "OAK: Your team is ready: SKARMORY,\n"
	.string "BLISSEY, CLAYDOL, DUGTRIO, GENGAR,\n"
	.string "and SUICUNE. Good luck!$"

PalletTown_ProfessorOaksLab_Text_ProfOakDeclined::
	.string "OAK: Return whenever you're ready.$"

PalletTown_ProfessorOaksLab_Text_Visitor::
	.string "I'm studying how regions connect.$"

PalletTown_ProfessorOaksLab_Text_Aide::
	.string "We're cataloging reused map assets.$"

PalletTown_ProfessorOaksLab_Text_PokeBall::
	.string "The POKé BALL is for display.$"

PalletTown_ProfessorOaksLab_Text_Pokedex::
	.string "A POKéDEX rests on the table.$"

PalletTown_ProfessorOaksLab_Text_Computer::
	.string "Research notes fill the screen.$"

PalletTown_ProfessorOaksLab_Text_Sign::
	.string "POKéMON RESEARCH NOTES$"
PalletTown_ProfessorOaksLab_EventScript_StarterGate::
	checkflag FLAG_POX_STORY_STARTER
	goto_if_eq TRUE, PalletTown_ProfessorOaksLab_EventScript_StarterDone
	givemon SPECIES_TREECKO, 5
	setflag FLAG_POX_STORY_STARTER
	msgbox PalletTown_ProfessorOaksLab_Text_Starter, MSGBOX_DEFAULT
	release
	end

PalletTown_ProfessorOaksLab_EventScript_StarterDone::
	end

PalletTown_ProfessorOaksLab_Text_Starter:
	.string "PROF. OAK (voice): Take TREECKO and go see how far the roads go now.$"
