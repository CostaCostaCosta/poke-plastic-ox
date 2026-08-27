PokemonCenter_Kanto_hns_MapScripts::
	.byte 0

PokemonCenter_Kanto_hns_EventScript_Nurse::
	lock
	faceplayer
	msgbox PokemonCenter_Kanto_hns_Text_NurseGreeting, MSGBOX_DEFAULT
	special HealPlayerParty
	playfanfare MUS_HEAL
	waitfanfare
	msgbox PokemonCenter_Kanto_hns_Text_NurseHealed, MSGBOX_DEFAULT
	waitbuttonpress
	release
	end

PokemonCenter_Kanto_hns_EventScript_BugCatcher::
	lock
	faceplayer
	msgbox PokemonCenter_Kanto_hns_Text_BugCatcher, MSGBOX_DEFAULT
	release
	end

PokemonCenter_Kanto_hns_Text_NurseGreeting:
	.string "Welcome to our POKéMON CENTER.\p"
	.string "The whole region merged and somehow\n"
	.string "our beds still work.\l"
	.string "Shall I heal your POKéMON?$"

PokemonCenter_Kanto_hns_Text_NurseHealed:
	.string "Your POKéMON are fully healed.\p"
	.string "We hope to see you again!$"

PokemonCenter_Kanto_hns_Text_BugCatcher:
	.string "The maps got scrambled when the\n"
	.string "regions merged, but this PC's\l"
	.string "rooftop still faces VERMILION.\p"
	.string "Some things don't move.$"
