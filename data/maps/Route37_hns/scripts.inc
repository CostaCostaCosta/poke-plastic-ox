Route37_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_Route37_hns
	.byte 0

Route37_EventScript_Npc1::
	lock
	faceplayer
	msgbox Route37_EventScript_Npc1_Text, MSGBOX_NPC
	release
	end

Route37_EventScript_Npc2::
	lock
	faceplayer
	msgbox Route37_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

Route37_EventScript_Npc3::
	lock
	faceplayer
	msgbox Route37_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

Route37_EventScript_Npc4::
	lock
	faceplayer
	msgbox Route37_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

Route37_EventScript_Npc1_Text:
	.string "ANN: My sister keeps time\nwhile our bugs practice their\psteps.$"

Route37_EventScript_Npc2_Text:
	.string "ANNE: We can hear the theater\nmusic from here when the wind\pturns north.$"

Route37_EventScript_Npc3_Text:
	.string "Ecruteak sages say old trees\nremember every traveler who\prested beneath them.$"

Route37_EventScript_Npc4_Text:
	.string "The orchard keeper leaves ripe\nSITRUS BERRIES for passing\ptrainers.\pTake some, and let the next\ncrop ripen for tomorrow.$"

Route37_EventScript_Ann::
	trainerbattle_single TRAINER_PLASTIC_OX_JOHTO_ANN_ANNE, Route37_EventScript_Ann_Intro, Route37_EventScript_Ann_Defeat
	msgbox Route37_EventScript_Ann_After, MSGBOX_AUTOCLOSE
	end
Route37_EventScript_Ann_Intro:
	.string "ANN: We raise our Pokemon\ntogether. Ready to meet the\pwhole family?$"
Route37_EventScript_Ann_Defeat:
	.string "Our rhythm slipped!$"
Route37_EventScript_Ann_After:
	.string "ANN: My sister practices the\nsteps. I listen for the beat.\pEcruteak's dancers make it\nlook easy!$"

Route37_EventScript_Anne::
	trainerbattle_single TRAINER_PLASTIC_OX_JOHTO_ANN_ANNE, Route37_EventScript_Anne_Intro, Route37_EventScript_Anne_Defeat
	msgbox Route37_EventScript_Anne_After, MSGBOX_AUTOCLOSE
	end
Route37_EventScript_Anne_Intro:
	.string "ANNE: One team, two sisters!\nLet's see how well we work\ptogether.$"
Route37_EventScript_Anne_Defeat:
	.string "We need more practice!$"
Route37_EventScript_Anne_After:
	.string "ANNE: We lost together, so\nwe'll train together.\pThe theater is our next stop.$"

Route37_EventScript_Greg::
	trainerbattle_single TRAINER_PLASTIC_OX_JOHTO_GREG, Route37_EventScript_Greg_Intro, Route37_EventScript_Greg_Defeat
	msgbox Route37_EventScript_Greg_After, MSGBOX_AUTOCLOSE
	end
Route37_EventScript_Greg_Intro:
	.string "The wind carries whispers from\nEcruteak. What does it say\pabout your team?$"
Route37_EventScript_Greg_Defeat:
	.string "A surprising forecast!$"
Route37_EventScript_Greg_After:
	.string "The tower bells can be heard\ndown this road.\pI like to meditate between\ntheir chimes.$"

Route37_EventScript_CitySign::
	msgbox Route37_Text_CitySign, MSGBOX_SIGN
	end
Route37_Text_CitySign:
	.string "ECRUTEAK CITY - NORTH\pFollow the stone road through\nthe city arch.$"
