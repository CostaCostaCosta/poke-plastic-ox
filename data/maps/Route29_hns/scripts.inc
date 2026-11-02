Route29_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_Route29_hns
	.byte 0

Route29_EventScript_OldMan::
	lock
	faceplayer
	msgbox Route29_Text_OldMan, MSGBOX_NPC
	release
	end

Route29_EventScript_Youngster::
	lock
	faceplayer
	msgbox Route29_Text_Youngster, MSGBOX_NPC
	release
	end

Route29_EventScript_Boy::
	lock
	faceplayer
	msgbox Route29_Text_Boy, MSGBOX_NPC
	release
	end

Route29_EventScript_Tuscany::
	lock
	faceplayer
	msgbox Route29_Text_Tuscany, MSGBOX_NPC
	release
	end

Route29_EventScript_Girl::
	lock
	faceplayer
	msgbox Route29_Text_Girl, MSGBOX_NPC
	release
	end

Route29_EventScript_ItemPotion::
	finditem ITEM_POTION
	end

Route29_EventScript_SignEast::
	msgbox Route29_Text_SignEast, MSGBOX_SIGN
	end

Route29_EventScript_SignWest::
	msgbox Route29_Text_SignWest, MSGBOX_SIGN
	end

Route29_Text_OldMan:
	.string "CHERRYGROVE lies to the west.\n"
	.string "OLDALE TOWN is east from here.\p"
	.string "I used to give different\n"
	.string "directions. Habit is stubborn.$"

Route29_Text_Youngster:
	.string "My SENTRET stands up so tall\n"
	.string "when someone passes by!\p"
	.string "I think it wants a battle.\n"
	.string "Well, I know I do!$"

Route29_Text_Boy:
	.string "That gate leads to ROUTE 46.\n"
	.string "I'm saving the climb for later.\p"
	.string "My lunch is heavy enough\n"
	.string "without carrying it uphill.$"

Route29_Text_Tuscany:
	.string "I'm TUSCANY. I like Tuesdays.\n"
	.string "They're my days for a walk.\p"
	.string "Everyone rushes past on Mondays.\n"
	.string "Today, I can hear the birds.$"

Route29_Text_Girl:
	.string "I walk out from CHERRYGROVE\n"
	.string "when the sea wind gets too sharp.\p"
	.string "It's quieter here. Even a short\n"
	.string "walk can feel like a holiday.$"

Route29_Text_SignEast:
	.string "ROUTE 29\n"
	.string "East to OLDALE TOWN$"

Route29_Text_SignWest:
	.string "ROUTE 29\n"
	.string "West to CHERRYGROVE CITY$"
