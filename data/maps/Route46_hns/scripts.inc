Route46_hns_MapScripts::
	.byte 0

Route46_EventScript_DarkCaveWarp::
	warp MAP_DARK_CAVE_SOUTH_SIDE_HNS, 56, 45
	waitstate
	end

Route46_EventScript_Ted::
	lock
	faceplayer
	msgbox Route46_Text_Ted, MSGBOX_NPC
	release
	end

Route46_EventScript_Erin::
	lock
	faceplayer
	msgbox Route46_Text_Erin, MSGBOX_NPC
	release
	end

Route46_EventScript_Bailey::
	lock
	faceplayer
	msgbox Route46_Text_Bailey, MSGBOX_NPC
	release
	end

Route46_EventScript_ItemRevive::
	finditem ITEM_REVIVE
	end

Route46_EventScript_Sign::
	msgbox Route46_Text_Sign, MSGBOX_SIGN
	end

Route46_Text_Ted:
	.string "The path south spits you out on a\n"
	.string "route with palm trees.\p"
	.string "PALM TREES! On a mountain road!\n"
	.string "I climbed down for a look and my\n"
	.string "boots got sand in them.$"

Route46_Text_Erin:
	.string "Downhill all the way to ROUTE 29,\n"
	.string "but which downhill?\p"
	.string "There's a cave shortcut to the\n"
	.string "north side of the mountains, if\n"
	.string "you trust the dark.$"

Route46_Text_Bailey:
	.string "I heard the mountains grew a new\n"
	.string "pass overnight.\p"
	.string "Mountains don't DO that. But the\n"
	.string "cave mouth is right there, so\n"
	.string "argue with the cave.$"

Route46_Text_Sign:
	.string "ROUTE 46 - Mountain descent\n"
	.string "DARK CAVE ~ entrance ahead$"
