MtMoon_Cave_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_MtMoon_Cave_hns
	.byte 0

MtMoon_Cave_EventScript_Npc1::
	lock
	faceplayer
	msgbox MtMoon_Cave_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

MtMoon_Cave_EventScript_Npc2::
	lock
	faceplayer
	msgbox MtMoon_Cave_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

MtMoon_Cave_EventScript_Npc3::
	lock
	faceplayer
	msgbox MtMoon_Cave_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

MtMoon_Cave_EventScript_Sign2::
	msgbox MtMoon_Cave_EventScript_Sign2_Text, MSGBOX_SIGN
	end

MtMoon_Cave_EventScript_Npc1_Text:
	.string "...This cave wasn't here yesterday.\nDon't slow me down.$"

MtMoon_Cave_EventScript_Npc2_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

MtMoon_Cave_EventScript_Npc3_Text:
	.string "Roads keep ending somewhere they\ndidn't used to.$"

MtMoon_Cave_EventScript_Sign2_Text:
	.string "MT.MOON\nSomewhere inside, the sky is underground.$"
