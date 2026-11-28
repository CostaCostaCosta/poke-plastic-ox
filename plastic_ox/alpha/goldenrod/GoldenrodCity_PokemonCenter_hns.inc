GoldenrodCity_PokemonCenter_hns_MapScripts::
	.byte 0

@ Standard Pokémon Center nurse: greeting, Yes/No, heal-machine animation, bow.
GoldenrodCity_PokemonCenter_hns_EventScript_Nurse::
	lock
	faceplayer
	call EventScript_PkmnCenterNurse_Frlg
	release
	end


PoxGoldenrod_GoldenrodCity_PokemonCenter_hns_2::
	msgbox PoxGoldenrod_GoldenrodCity_PokemonCenter_hns_2_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_PokemonCenter_hns_2_Text:
	.string "The GYM emptied my medicine bag.\nI'm glad the CENTER stays open.$"

PoxGoldenrod_GoldenrodCity_PokemonCenter_hns_3::
	msgbox PoxGoldenrod_GoldenrodCity_PokemonCenter_hns_3_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_PokemonCenter_hns_3_Text:
	.string "My friend battles at the park.\nI come here to trade stories.$"

PoxGoldenrod_GoldenrodCity_PokemonCenter_hns_4::
	msgbox PoxGoldenrod_GoldenrodCity_PokemonCenter_hns_4_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_PokemonCenter_hns_4_Text:
	.string "The nurse knows my POKéMON by name.\nI wish she'd forget my mishaps.$"

PoxGoldenrod_GoldenrodCity_PokemonCenter_hns_5::
	msgbox PoxGoldenrod_GoldenrodCity_PokemonCenter_hns_5_Text, MSGBOX_NPC
	end
PoxGoldenrod_GoldenrodCity_PokemonCenter_hns_5_Text:
	.string "We practiced link battles all week.\nI still can't beat my brother.$"

