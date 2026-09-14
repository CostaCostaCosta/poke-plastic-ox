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
	.string "DAISY: My TOWN MAP doesn't work\n"
	.string "anymore!\p"
	.string "All the roads lead somewhere new.\n"
	.string "I suppose you'll have to make your\n"
	.string "own map as you explore!$"

PalletTown_RivalsHouse_Text_TownMap::
	.string "It's DAISY's old TOWN MAP. The\n"
	.string "nearby roads no longer match it.$"

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
