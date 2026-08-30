Route31_hns_MapScripts::
	.byte 0

Route31_EventScript_Wade::
	lock
	faceplayer
	msgbox Route31_Text_Wade, MSGBOX_NPC
	release
	end

Route31_EventScript_Youngster::
	lock
	faceplayer
	msgbox Route31_Text_Youngster, MSGBOX_NPC
	release
	end

Route31_EventScript_SleepyMan::
	lock
	faceplayer
	msgbox Route31_Text_SleepyMan, MSGBOX_NPC
	release
	end

Route31_EventScript_Boy::
	lock
	faceplayer
	msgbox Route31_Text_Boy, MSGBOX_NPC
	release
	end

Route31_EventScript_ItemPokeBall::
	finditem ITEM_POKE_BALL
	end

Route31_EventScript_ItemAntidote::
	finditem ITEM_ANTIDOTE
	end

Route31_EventScript_Sign::
	msgbox Route31_Text_Sign, MSGBOX_SIGN
	end

Route31_EventScript_DarkCaveSign::
	msgbox Route31_Text_DarkCaveSign, MSGBOX_SIGN
	end

Route31_Text_Wade:
	.string "A bug came through here wearing\n"
	.string "Hoenn pollen. My nets aren't rated\n"
	.string "for foreign bugs!\p"
	.string "The whole forest's like that now.\n"
	.string "Bugs don't carry maps.$"

Route31_Text_Youngster:
	.string "The cave up north lets out on a\n"
	.string "mountain road, and that road ends\n"
	.string "at a beach with a HOENN name.\p"
	.string "I checked twice. The signs agree\n"
	.string "with each other. Nobody else does.$"

Route31_Text_SleepyMan:
	.string "Zzz... huh? Is it morning?\p"
	.string "The sun comes up on the wrong side\n"
	.string "of the mountain lately. Zzz...\p"
	.string "Don't tell the sun I complained.$"

Route31_Text_Boy:
	.string "My friend went into DARK CAVE and\n"
	.string "came out somewhere he'd never\n"
	.string "hiked to.\p"
	.string "He thinks the cave moved. Caves\n"
	.string "can't move. Right?$"

Route31_Text_Sign:
	.string "ROUTE 30 - south, toward\n"
	.string "CHERRYGROVE CITY$"

Route31_Text_DarkCaveSign:
	.string "DARK CAVE - southern entrance\n"
	.string "Watch your step in the dark.$"
