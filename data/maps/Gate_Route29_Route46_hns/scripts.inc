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
	.string "This gate connects ROUTE 29 to the\n"
	.string "lower end of ROUTE 46.$"

Gate_Route29_Route46_Text_Youngster:
	.string "The mountain path starts just past\n"
	.string "the north door.$"
