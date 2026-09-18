EcruteakCity_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_EcruteakCity_hns
	.byte 0

EcruteakCity_EventScript_Npc1::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_KimonoRoadblock::
	lock
	faceplayer
	msgbox EcruteakCity_Text_KimonoRoadblock, MSGBOX_NPC
	release
	end

EcruteakCity_Text_KimonoRoadblock:
	.string "Please help MORTY at the BURNED\nTOWER, then earn his GYM BADGE.\pAfter that, you may pass east.$"

EcruteakCity_EventScript_Npc2::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc3::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc4::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc5::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc5_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc6::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc6_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc7::
	lock
	faceplayer
	msgbox EcruteakCity_EventScript_Npc7_Text, MSGBOX_NPC
	release
	end

EcruteakCity_EventScript_Npc1_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

EcruteakCity_EventScript_Npc2_Text:
	.string "The BURNED TOWER remembers the fire. The fire remembers nothing.$"

EcruteakCity_EventScript_Npc3_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

EcruteakCity_EventScript_Npc4_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

EcruteakCity_EventScript_Npc5_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

EcruteakCity_EventScript_Npc6_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

EcruteakCity_EventScript_Npc7_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"
