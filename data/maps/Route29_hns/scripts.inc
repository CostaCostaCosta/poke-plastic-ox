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
	.string "A route is a road, and a road goes\n"
	.string "somewhere. This one goes east to a\l"
	.string "sea town... or west to nowhere.\p"
	.string "The maps stopped agreeing with\n"
	.string "each other, so I stopped asking.$"

Route29_Text_Youngster:
	.string "I ran west as far as I could and\n"
	.string "fell into a town full of HOENN\n"
	.string "accents.\p"
	.string "Nobody there thought it was weird!\n"
	.string "Should I be worried?$"

Route29_Text_Boy:
	.string "My grandpa says this used to dead-\n"
	.string "end at NEW BARK TOWN.\p"
	.string "Now the road just... keeps going,\n"
	.string "and nobody remembers NEW BARK.$"

Route29_Text_Tuscany:
	.string "I keep a diary of the days, but\n"
	.string "the days out here don't line up\n"
	.string "with the ones back home.\p"
	.string "Is today Tuesday? It feels like a\n"
	.string "Tuesday from another region.$"

Route29_Text_Girl:
	.string "A CHERRYGROVE elder told me a\n"
	.string "HOENN route empties into his coast.\p"
	.string "He said his grandfather would have\n"
	.string "fainted. Then he offered me tea.$"

Route29_Text_SignEast:
	.string "ROUTE 29\n"
	.string "CHERRYGROVE CITY ~ THE ROAD THAT\n"
	.string "FORGOT WHERE IT STARTED$"

Route29_Text_SignWest:
	.string "ROUTE 29 - New Bark ~ impossible\n"
	.string "directions ahead$"
