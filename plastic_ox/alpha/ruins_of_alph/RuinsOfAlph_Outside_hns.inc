RuinsOfAlph_Outside_hns_MapScripts::
	.byte 0

PoxRuins_Student::
	msgbox PoxRuins_Text_Student, MSGBOX_NPC
	end

PoxRuins_Text_Student:
	.string "I'm measuring the chambers.\p"
	.string "Each one has a back wall with a\n"
	.string "hollow about the size of a roof\p"
	.string "tile. This one's rough inside,\n"
	.string "like the stone was split.$"

PoxRuins_Surveyor::
	msgbox PoxRuins_Text_Surveyor, MSGBOX_NPC
	end

PoxRuins_Text_Surveyor:
	.string "The south terraces are over the\n"
	.string "pond. No bridge yet.\p"
	.string "We float the crates across on a\n"
	.string "LAPRAS and SURF after them.$"

PoxRuins_Digger::
	msgbox PoxRuins_Text_Digger, MSGBOX_NPC
	end

PoxRuins_Text_Digger:
	.string "That crawlway behind me comes out\n"
	.string "by the west chamber.\p"
	.string "Mind your head. I didn't.$"

PoxRuins_SiteSign::
	msgbox PoxRuins_Text_SiteSign, MSGBOX_SIGN
	end

PoxRuins_Text_SiteSign:
	.string "RUINS OF ALPH\n"
	.string "Survey in progress. Keep to the\l"
	.string "marked paths.$"

PoxRuins_LabSign::
	msgbox PoxRuins_Text_LabSign, MSGBOX_SIGN
	end

PoxRuins_Text_LabSign:
	.string "RUINS RESEARCH CENTER\n"
	.string "All staff are in the field.$"

PoxRuins_NorthChamberSign::
	msgbox PoxRuins_Text_NorthChamberSign, MSGBOX_SIGN
	end

PoxRuins_Text_NorthChamberSign:
	.string "NORTH CHAMBER\n"
	.string "Surveyed. Back wall unopened.$"

PoxRuins_RopedStair::
	msgbox PoxRuins_Text_RopedStair, MSGBOX_SIGN
	end

PoxRuins_Text_RopedStair:
	.string "A rope is tied across the stair.\n"
	.string "The tag on it reads UNSAFE FLOOR.$"

PoxRuins_EastGatehouse::
	msgbox PoxRuins_Text_EastGatehouse, MSGBOX_SIGN
	end

PoxRuins_Text_EastGatehouse:
	.string "The shutter is down. A notice\n"
	.string "says the road east is washed out.$"
