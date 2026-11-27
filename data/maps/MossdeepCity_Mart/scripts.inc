MossdeepCity_Mart_MapScripts::
	.byte 0

MossdeepCity_Mart_EventScript_Clerk::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart MossdeepCity_Mart_Pokemart
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
MossdeepCity_Mart_Pokemart:
	.2byte ITEM_ULTRA_BALL
	.2byte ITEM_NET_BALL
	.2byte ITEM_DIVE_BALL
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_FULL_HEAL
	.2byte ITEM_REVIVE
	.2byte ITEM_MAX_REPEL
	.2byte ITEM_MOON_STONE
	.2byte ITEM_WATER_STONE
	.2byte ITEM_LEFTOVERS
	pokemartlistend

MossdeepCity_Mart_EventScript_Woman::
	msgbox MossdeepCity_Mart_Text_ReviveIsFantastic, MSGBOX_NPC
	end

MossdeepCity_Mart_EventScript_Boy::
	msgbox MossdeepCity_Mart_Text_MaxRepelLastsLongest, MSGBOX_NPC
	end

MossdeepCity_Mart_EventScript_Sailor::
	msgbox MossdeepCity_Mart_Text_NetAndDiveBallsRare, MSGBOX_NPC
	end

MossdeepCity_Mart_Text_ReviveIsFantastic:
	.string "Everything on this island comes\nover by boat, so everything\lcosts a boat's worth more.\pI buy the REVIVES anyway.$"

MossdeepCity_Mart_Text_MaxRepelLastsLongest:
	.string "MAX REPEL lasts the longest. I\ntimed it on the path round the\lSPACE CENTER.\pTwice, to be sure.$"

MossdeepCity_Mart_Text_NetAndDiveBallsRare:
	.string "NET BALLS and DIVE BALLS are\nmade here on MOSSDEEP.\pThe NET ones are for anything\nthat swims or crawls. I keep a\lfew for whatever comes up with\lthe catch.$"

