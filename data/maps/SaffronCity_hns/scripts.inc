SaffronCity_hns_MapScripts::
	.byte 0

SaffronCity_EventScript_Npc1::
	lock
	faceplayer
	msgbox SaffronCity_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

SaffronCity_EventScript_Npc2::
	lock
	faceplayer
	msgbox SaffronCity_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

SaffronCity_EventScript_Npc3::
	lock
	faceplayer
	msgbox SaffronCity_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

SaffronCity_EventScript_Npc4::
	lock
	faceplayer
	msgbox SaffronCity_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

SaffronCity_EventScript_Npc5::
	lock
	faceplayer
	msgbox SaffronCity_EventScript_Npc5_Text, MSGBOX_NPC
	release
	end

SaffronCity_EventScript_Npc6::
	lock
	faceplayer
	msgbox SaffronCity_EventScript_Npc6_Text, MSGBOX_NPC
	release
	end

SaffronCity_EventScript_Npc7::
	lock
	faceplayer
	msgbox SaffronCity_EventScript_Npc7_Text, MSGBOX_NPC
	release
	end

SaffronCity_EventScript_Npc8::
	lock
	faceplayer
	msgbox SaffronCity_EventScript_Npc8_Text, MSGBOX_NPC
	release
	end

SaffronCity_EventScript_Npc9::
	lock
	faceplayer
	msgbox SaffronCity_EventScript_Npc9_Text, MSGBOX_NPC
	release
	end

SaffronCity_EventScript_Npc1_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

SaffronCity_EventScript_Npc2_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

SaffronCity_EventScript_Npc3_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

SaffronCity_EventScript_Npc4_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

SaffronCity_EventScript_Npc5_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

SaffronCity_EventScript_Npc6_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

SaffronCity_EventScript_Npc7_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

SaffronCity_EventScript_Npc8_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

SaffronCity_EventScript_Npc9_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"
SaffronCity_EventScript_P28_4::
	warp MAP_ROUTE5_HNS, 24, 36
	waitstate
	end
