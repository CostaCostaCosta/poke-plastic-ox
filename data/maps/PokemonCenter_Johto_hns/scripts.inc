PokemonCenter_Johto_hns_MapScripts::
	.byte 0

PokemonCenter_Johto_hns_EventScript_Nurse::
	lock
	faceplayer
	msgbox PokemonCenter_Johto_hns_Text_NurseGreeting, MSGBOX_DEFAULT
	special HealPlayerParty
	playfanfare MUS_HEAL
	waitfanfare
	msgbox PokemonCenter_Johto_hns_Text_NurseHealed, MSGBOX_DEFAULT
	waitbuttonpress
	release
	end

PokemonCenter_Johto_hns_EventScript_Lass::
	lock
	faceplayer
	msgbox PokemonCenter_Johto_hns_Text_Lass, MSGBOX_DEFAULT
	release
	end

PokemonCenter_Johto_hns_EventScript_Boy::
	lock
	faceplayer
	msgbox PokemonCenter_Johto_hns_Text_Boy, MSGBOX_NPC
	release
	end

PokemonCenter_Johto_hns_EventScript_Gentleman::
	lock
	faceplayer
	msgbox PokemonCenter_Johto_hns_Text_Gentleman, MSGBOX_NPC
	release
	end

PokemonCenter_Johto_hns_Text_NurseGreeting:
	.string "Welcome to our POKéMON CENTER.\p"
	.string "The whole region merged and somehow\n"
	.string "our beds still work.\l"
	.string "Shall I heal your POKéMON?$"

PokemonCenter_Johto_hns_Text_NurseHealed:
	.string "Your POKéMON are fully healed.\p"
	.string "We hope to see you again!$"

PokemonCenter_Johto_hns_Text_Lass:
	.string "A trainer came through saying he\n"
	.string "walked here from PALLET Town.\p"
	.string "Is that some new region everyone\n"
	.string "keeps mentioning?$"

PokemonCenter_Johto_hns_Text_Boy:
	.string "The sea breeze feels great after a\n"
	.string "long walk along ROUTE 2.$"

PokemonCenter_Johto_hns_Text_Gentleman:
	.string "The nurse can restore your whole\n"
	.string "team before you head north.$"
