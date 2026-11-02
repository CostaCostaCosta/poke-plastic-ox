Route2_ViridianForest_SouthEntrance_Frlg_MapScripts::
	.byte 0

Route2_ViridianForest_SouthEntrance_EventScript_Woman1::
	msgbox Route2_ViridianForest_SouthEntrance_Text_ForestIsMaze, MSGBOX_NPC
	end

Route2_ViridianForest_SouthEntrance_EventScript_Woman2::
	msgbox Route2_ViridianForest_SouthEntrance_Text_RattataHasWickedBite, MSGBOX_NPC
	end

Route2_ViridianForest_SouthEntrance_EventScript_Guard::
	msgbox Route2_ViridianForest_SouthEntrance_Text_Guard, MSGBOX_NPC
	end

Route2_ViridianForest_SouthEntrance_Text_ForestIsMaze::
	.string "I tried counting the turns in\n"
	.string "ILEX FOREST. I lost count!\p"
	.string "I'll rest my feet here before\n"
	.string "I give that path another try.$"

Route2_ViridianForest_SouthEntrance_Text_RattataHasWickedBite::
	.string "A RATTATA nipped my bag strap\n"
	.string "when I set it in the grass.\p"
	.string "Now I keep my lunch packed\n"
	.string "right at the bottom!$"

Route2_ViridianForest_SouthEntrance_Text_Guard::
	.string "The north door leads into\n"
	.string "ILEX FOREST.\p"
	.string "The south door is ROUTE 2.\n"
	.string "Keep the carpet clear, please.$"
