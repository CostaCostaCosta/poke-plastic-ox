Route30_hns_MapScripts::
	.byte 0

Route30_EventScript_Boy::
	lock
	faceplayer
	msgbox Route30_Text_Boy, MSGBOX_NPC
	release
	end

Route30_EventScript_Joey::
	lock
	faceplayer
	msgbox Route30_Text_Joey, MSGBOX_NPC
	release
	end

Route30_EventScript_Girl::
	lock
	faceplayer
	msgbox Route30_Text_Girl, MSGBOX_NPC
	release
	end

Route30_EventScript_Don::
	lock
	faceplayer
	msgbox Route30_Text_Don, MSGBOX_NPC
	release
	end

Route30_EventScript_JoeyDayOff::
	lock
	faceplayer
	msgbox Route30_Text_JoeyDayOff, MSGBOX_NPC
	release
	end

Route30_EventScript_Sign::
	msgbox Route30_Text_Sign, MSGBOX_SIGN
	end

Route30_EventScript_TrainerTips::
	msgbox Route30_Text_TrainerTips, MSGBOX_SIGN
	end

Route30_Text_Boy:
	.string "The lake used to be the whole\n"
	.string "north end of the route.\p"
	.string "Now there's a road PAST it going\n"
	.string "somewhere called VIOLET. Never\n"
	.string "heard of it. Have you?$"

Route30_Text_Joey:
	.string "I'm training my RATTATA to beat\n"
	.string "any region's top percentage.\p"
	.string "A traveler showed me a POKEMON\n"
	.string "called a TREECKO. It just stood\n"
	.string "there, judging us.$"

Route30_Text_Girl:
	.string "South is CHERRYGROVE. The sea\n"
	.string "smells different there than it\n"
	.string "did last year.\p"
	.string "Salties and tropics mixed\n"
	.string "together. Even the water is\n"
	.string "confused.$"

Route30_Text_Don:
	.string "Bug catching tip: foreign bugs\n"
	.string "count double in my book!\p"
	.string "I caught something with a leaf for\n"
	.string "a neck. My guidebook has no page\n"
	.string "for it.$"

Route30_Text_JoeyDayOff:
	.string "Even trainers need days off.\p"
	.string "I was going to walk to CHERRYGROVE,\n"
	.string "but if I keep walking past it, who\n"
	.string "knows where I'd end up?$"

Route30_Text_Sign:
	.string "ROUTE 30 - CHERRYGROVE CITY\n"
	.string "straight ahead$"

Route30_Text_TrainerTips:
	.string "TRAINER TIPS\n"
	.string "Routes no longer end where the\n"
	.string "map says they do.\p"
	.string "Pack supplies for impossible\n"
	.string "geography!$"
