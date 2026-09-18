Route24_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_Route24_hns
	.byte 0

Route24_EventScript_Npc1::
	lock
	faceplayer
	msgbox Route24_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

Route24_EventScript_Npc2::
	lock
	faceplayer
	msgbox Route24_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

Route24_EventScript_Npc3::
	lock
	faceplayer
	msgbox Route24_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

Route24_EventScript_Npc4::
	lock
	faceplayer
	msgbox Route24_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

Route24_EventScript_Npc1_Text:
	.string "I was told to go to a cave,\nbut I got lost out here.\pDon't tell the BOSS you saw me!$"

Route24_EventScript_Npc2_Text:
	.string "I walk out here after work.\nIt gets the dust off my boots.\pA good battle does more for me\nthan sitting around at home.$"

Route24_EventScript_Npc3_Text:
	.string "RUSTBORO is just south of here.\nThe cottage lies farther north.\pI only meant to take a short\nwalk. I say that every time!$"

Route24_EventScript_Npc4_Text:
	.string "I brought lunch and some bait.\nThey're in separate tins.\pLast time I mixed them up.\nI checked twice today.$"
