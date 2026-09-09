PalletTown_RivalsHouse_Frlg_MapScripts::
	.byte 0

PalletTown_RivalsHouse_EventScript_Daisy::
	goto_if_unset FLAG_POX_STORY_STARTER, PalletTown_Daisy_BeforeStarter
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
	.string "ROUTE 101 and OLDALE TOWN.\p"
	.string "There is a POKéMON CENTER there.\n"
	.string "CHERRYGROVE is farther west.\p"
	.string "BLUE is already out exploring.\n"
	.string "Travel at your own pace, okay?$"

PalletTown_RivalsHouse_Text_TownMap::
	.string "It's a map of PALLET TOWN and the\n"
	.string "nearby roads.$"

PalletTown_RivalsHouse_Text_Bookshelf::
	.string "Books about POKéMON fill the shelf.$"

PalletTown_RivalsHouse_Text_Picture::
	.string "A cheerful family photo.$"

PalletTown_Daisy_BeforeStarter::
	msgbox PalletTown_Daisy_Text_Lab, MSGBOX_NPC
	end

PalletTown_Daisy_Text_Lab::
	.string "DAISY: Choosing your first POKéMON?\n"
	.string "Grandpa is waiting at the lab.\p"
	.string "He's been comparing maps with ELM\n"
	.string "and BIRCH all morning!$"
