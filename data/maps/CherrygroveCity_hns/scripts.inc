CherrygroveCity_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_CherrygroveCity_hns
	.byte 0

CherrygroveCity_EventScript_GuideGent::
	lock
	faceplayer
	msgbox CherrygroveCity_Text_GuideGent, MSGBOX_NPC
	release
	end

CherrygroveCity_EventScript_Fisherman::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_GOOD_ROD, CherrygroveCity_EventScript_FishermanAlreadyGaveRod
	msgbox CherrygroveCity_Text_Fisherman, MSGBOX_NPC
	giveitem ITEM_GOOD_ROD
	goto_if_eq VAR_RESULT, FALSE, CherrygroveCity_EventScript_FishermanBagFull
	setflag FLAG_RECEIVED_GOOD_ROD
	msgbox CherrygroveCity_Text_ReceivedGoodRod, MSGBOX_DEFAULT
	release
	end
CherrygroveCity_EventScript_FishermanBagFull::
	msgbox CherrygroveCity_Text_BagFull, MSGBOX_DEFAULT
	release
	end
CherrygroveCity_EventScript_FishermanAlreadyGaveRod::
	msgbox CherrygroveCity_Text_FishermanAfter, MSGBOX_NPC
	release
	end

CherrygroveCity_EventScript_Boy::
	lock
	faceplayer
	msgbox CherrygroveCity_Text_Boy, MSGBOX_NPC
	release
	end

CherrygroveCity_EventScript_Lass::
	lock
	faceplayer
	msgbox CherrygroveCity_Text_Lass, MSGBOX_NPC
	release
	end

CherrygroveCity_EventScript_Sign::
	msgbox CherrygroveCity_Text_Sign, MSGBOX_SIGN
	end

CherrygroveCity_Text_GuideGent:
	.string "I'm known as the town's guide, so\n"
	.string "ask me anything!\p"
	.string "...Except what region this is.\n"
	.string "The answer changes depending on\n"
	.string "which road you came in on.\p"
	.string "A HOENN route now empties right\n"
	.string "into my coast. My grandfather\n"
	.string "would have fainted.\p"
	.string "Me? I've decided to enjoy the\n"
	.string "extra foot traffic.$"

CherrygroveCity_Text_Fisherman:
	.string "The tide brings in CORSOLA now.\n"
	.string "CORSOLA! In JOHTO waters!\p"
	.string "My grandkids think I'm making it\n"
	.string "up. The CORAL doesn't lie.\p"
	.string "Take this GOOD ROD and see what\n"
	.string "you can catch!$"

CherrygroveCity_Text_ReceivedGoodRod:
	.string "{PLAYER} received the GOOD ROD!$"

CherrygroveCity_Text_BagFull:
	.string "Make room in your KEY ITEMS pocket,\n"
	.string "then come back for the GOOD ROD.$"

CherrygroveCity_Text_FishermanAfter:
	.string "Cast that GOOD ROD wherever the\n"
	.string "water looks promising!$"

CherrygroveCity_Text_Boy:
	.string "A road appeared north of town and\n"
	.string "it goes UPHILL into mountains\n"
	.string "that weren't there.\p"
	.string "I'm gonna bike it one day.$"

CherrygroveCity_Text_Lass:
	.string "This used to be the smallest town\n"
	.string "you could sail to.\p"
	.string "Now it's a crossroads. Two whole\n"
	.string "regions' worth of roads end at\n"
	.string "our little beach.$"

CherrygroveCity_Text_Sign:
	.string "CHERRYGROVE CITY - The Town of\n"
	.string "Fiery, Now-Confusing Sunsets$"
