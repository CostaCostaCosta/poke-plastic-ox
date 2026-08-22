PalletTown_RivalsHouse_Frlg_MapScripts::
	.byte 0

PalletTown_RivalsHouse_EventScript_Daisy::
	msgbox PalletTown_RivalsHouse_Text_Daisy, MSGBOX_NPC
	end

PalletTown_RivalsHouse_EventScript_TownMap::
	msgbox PalletTown_RivalsHouse_Text_TownMap, MSGBOX_SIGN
	end

PalletTown_RivalsHouse_EventScript_Bookshelf::
	msgbox PalletTown_RivalsHouse_Text_Bookshelf, MSGBOX_SIGN
	end

PalletTown_RivalsHouse_EventScript_Picture::
	msgbox PalletTown_RivalsHouse_Text_Picture, MSGBOX_SIGN
	end

PalletTown_RivalsHouse_Text_Daisy::
	.string "DAISY: The road north leads to\n"
	.string "ROUTE 101 and OLDALE TOWN.$"

PalletTown_RivalsHouse_Text_TownMap::
	.string "It's a map of PALLET TOWN and the\n"
	.string "nearby roads.$"

PalletTown_RivalsHouse_Text_Bookshelf::
	.string "Books about POKéMON fill the shelf.$"

PalletTown_RivalsHouse_Text_Picture::
	.string "A cheerful family photo.$"
