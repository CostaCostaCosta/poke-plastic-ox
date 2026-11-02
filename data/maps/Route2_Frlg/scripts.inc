Route2_Frlg_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_Route2_Frlg
	.byte 0

Route2_EventScript_Ben::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE2_BEN, Route2_Text_BenSeen, Route2_Text_BenDefeated
	msgbox Route2_Text_BenAfter, MSGBOX_AUTOCLOSE
	end

Route2_EventScript_Wade::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE2_WADE, Route2_Text_WadeSeen, Route2_Text_WadeDefeated
	msgbox Route2_Text_WadeAfter, MSGBOX_AUTOCLOSE
	end

Route2_EventScript_RouteSign::
	msgbox Route2_Text_RouteSign, MSGBOX_SIGN
	end

Route2_EventScript_DiglettsCaveSign::
	msgbox Route2_Text_DiglettsCave, MSGBOX_SIGN
	end

Route2_Text_RouteSign::
	.string "ROUTE 2\n"
	.string "CHERRYGROVE - RUSTBORO$"

Route2_Text_DiglettsCave::
	.string "DARK CAVE$"

Route2_Text_BenSeen:
	.string "Coming up from CHERRYGROVE?\n"
	.string "Let's battle on the south trail!$"

Route2_Text_BenDefeated:
	.string "You made that look easy!$"

Route2_Text_BenAfter:
	.string "My team and I train here every\n"
	.string "day. See you on the trail!$"

Route2_Text_WadeSeen:
	.string "The north trail gets tougher!\n"
	.string "Let's see how far you've come!$"

Route2_Text_WadeDefeated:
	.string "You came a long way!$"

Route2_Text_WadeAfter:
	.string "I started with a bug net.\n"
	.string "Now I train all kinds of POKéMON.$"
