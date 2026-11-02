Gate_Route29_Route46_hns_MapScripts::
	.byte 0

Gate_Route29_Route46_EventScript_Officer::
	lock
	faceplayer
	msgbox Gate_Route29_Route46_Text_Officer, MSGBOX_NPC
	release
	end

Gate_Route29_Route46_EventScript_Youngster::
	lock
	faceplayer
	msgbox Gate_Route29_Route46_Text_Youngster, MSGBOX_NPC
	release
	end

Gate_Route29_Route46_Text_Officer:
	.string "ROUTE 46 is through the north\n"
	.string "door. ROUTE 29 lies south.\p"
	.string "No need to stop at my desk.\n"
	.string "I'm here for directions.$"

Gate_Route29_Route46_Text_Youngster:
	.string "I came down from ROUTE 46.\n"
	.string "My legs are still wobbling!\p"
	.string "I'll rest here a little longer.\n"
	.string "You go on ahead.$"
