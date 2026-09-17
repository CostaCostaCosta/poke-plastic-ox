OldaleTown_House1_MapScripts::
	.byte 0

OldaleTown_House1_EventScript_Woman::
	lock
	faceplayer
	checkitem ITEM_POCKET_WATCH, 1
	goto_if_eq VAR_RESULT, TRUE, OldaleTown_House1_EventScript_WomanAlreadyGaveWatch
	msgbox OldaleTown_House1_Text_PocketWatchGift, MSGBOX_DEFAULT
	giveitem ITEM_POCKET_WATCH
	goto_if_eq VAR_RESULT, FALSE, OldaleTown_House1_EventScript_PocketWatchBagFull
	msgbox OldaleTown_House1_Text_PocketWatchInstructions, MSGBOX_DEFAULT
	release
	end

OldaleTown_House1_EventScript_PocketWatchBagFull::
	msgbox OldaleTown_House1_Text_PocketWatchBagFull, MSGBOX_DEFAULT
	release
	end

OldaleTown_House1_EventScript_WomanAlreadyGaveWatch::
	msgbox OldaleTown_House1_Text_PocketWatchReminder, MSGBOX_DEFAULT
	release
	end

OldaleTown_House1_Text_PocketWatchGift:
	.string "Oh! A traveling TRAINER!\p"
	.string "Take this old POCKET WATCH. It can\n"
	.string "help you keep to your own schedule.$"

OldaleTown_House1_Text_PocketWatchInstructions:
	.string "Use it inside any building to adjust\n"
	.string "the time and day of the week.\p"
	.string "Its delicate gears won't work well\n"
	.string "outdoors.$"

OldaleTown_House1_Text_PocketWatchBagFull:
	.string "Your BAG is full. Make some room and\n"
	.string "come back for the POCKET WATCH.$"

OldaleTown_House1_Text_PocketWatchReminder:
	.string "The POCKET WATCH only works inside\n"
	.string "buildings, away from wind and rain.$"

OldaleTown_House1_Text_LeftPokemonGoesOutFirst:
	.string "When a POKéMON battle starts, the one\n"
	.string "at the left of the list goes out first.\p"
	.string "So, when you get more POKéMON in your\n"
	.string "party, try switching around the order\l"
	.string "of your POKéMON.\p"
	.string "It could give you an advantage.$"
