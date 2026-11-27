CinnabarIsland_PokemonLab_ResearchRoom_Frlg_MapScripts::
	.byte 0

CinnabarIsland_PokemonLab_ResearchRoom_EventScript_MetronomeTutor::
	goto EventScript_MetronomeTutor
	end

CinnabarIsland_PokemonLab_ResearchRoom_EventScript_Scientist::
	msgbox CinnabarIsland_PokemonLab_ResearchRoom_Text_EeveeCanEvolveIntroThreeMons, MSGBOX_NPC
	end

CinnabarIsland_PokemonLab_ResearchRoom_EventScript_Computer::
	msgbox CinnabarIsland_PokemonLab_ResearchRoom_Text_LegendaryBirdEmail, MSGBOX_SIGN
	end

CinnabarIsland_PokemonLab_ResearchRoom_EventScript_AmberPipe::
	msgbox CinnabarIsland_PokemonLab_ResearchRoom_Text_AnAmberPipe, MSGBOX_SIGN
	end

CinnabarIsland_PokemonLab_ResearchRoom_Text_EeveeCanEvolveIntroThreeMons::
	.string "They kept EEVEE here once, for\nthe way it changes with its\lsurroundings.\pOne went to LAVENDER with the\nfounder. I heard another ended\lup at a launch site, of all\lplaces.$"

CinnabarIsland_PokemonLab_ResearchRoom_Text_LegendaryBirdEmail::
	.string "A printed message is pinned up.\pFrom: FIELD TEAM\pFishing boats east of here report\nice on their nets. At this latitude.\pWe would like a boat and a week.\pPencilled underneath:\nNo boat. Ask again in spring.$"

CinnabarIsland_PokemonLab_ResearchRoom_Text_AnAmberPipe::
	.string "An amber pipe!$"

