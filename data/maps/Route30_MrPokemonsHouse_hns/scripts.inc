Route30_MrPokemonsHouse_hns_MapScripts::
	.byte 0

Route30_MrPokemonsHouse_EventScript_Resident::
	lock
	faceplayer
	msgbox Route30_MrPokemonsHouse_Text_Resident, MSGBOX_NPC
	release
	end

Route30_MrPokemonsHouse_Text_Resident:
	.string "I study the POKEMON that gather\n"
	.string "where the regions overlap.$"
