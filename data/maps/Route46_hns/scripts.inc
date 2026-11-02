Route46_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_Route46_hns
	.byte 0

Route46_EventScript_Ted::
	lock
	faceplayer
	msgbox Route46_Text_Ted, MSGBOX_NPC
	release
	end

Route46_EventScript_Erin::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE46_ERIN, Route46_Text_Erin, Route46_Text_Erin_Defeat
	msgbox Route46_Text_Erin_After, MSGBOX_AUTOCLOSE
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
	.string "This trail ends at the ledges\n"
	.string "if you're coming from below.\p"
	.string "That's fine by me. A short walk\n"
	.string "still counts as a hike!$"

Route46_Text_Erin:
	.string "I packed lunch for the hike.\n"
	.string "My POKéMON packed a battle!$"

Route46_Text_Erin_Defeat:
	.string "Time for a lunch break!$"

Route46_Text_Erin_After:
	.string "I spread my lunch on a rock.\n"
	.string "The wind took the napkin!$"

Route46_Text_Bailey:
	.string "I came down from the mountains.\n"
	.string "My boots hardly slowed me down.\p"
	.string "Going back up those ledges?\n"
	.string "Not on these legs!$"

Route46_Text_Sign:
	.string "ROUTE 46\n"
	.string "Mountain foothills\p"
	.string "Ledges allow descent only.\n"
	.string "No uphill passage.$"
