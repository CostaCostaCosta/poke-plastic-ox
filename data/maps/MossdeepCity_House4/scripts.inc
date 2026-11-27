MossdeepCity_House4_MapScripts::
	.byte 0

MossdeepCity_House4_EventScript_Woman::
	lock
	faceplayer
	goto_if_set FLAG_SYS_GAME_CLEAR, MossdeepCity_House4_EventScript_CanBattleAtSecretBases
	msgbox MossdeepCity_House4_Text_BrotherLikesToFindBases, MSGBOX_DEFAULT
	release
	end

MossdeepCity_House4_EventScript_CanBattleAtSecretBases::
	msgbox MossdeepCity_House4_Text_BrotherLikesToVisitBasesAndBattle, MSGBOX_DEFAULT
	release
	end

MossdeepCity_House4_EventScript_NinjaBoy::
	lock
	faceplayer
	special CheckPlayerHasSecretBase
	goto_if_eq VAR_RESULT, FALSE, MossdeepCity_House4_EventScript_NoSecretBase
	special GetSecretBaseNearbyMapName
	msgbox MossdeepCity_House4_Text_YouMadeSecretBaseNearX, MSGBOX_DEFAULT
	release
	end

MossdeepCity_House4_EventScript_NoSecretBase::
	msgbox MossdeepCity_House4_Text_MakeSecretBase, MSGBOX_DEFAULT
	release
	end

MossdeepCity_House4_EventScript_Skitty::
	lock
	faceplayer
	waitse
	playmoncry SPECIES_SKITTY, CRY_MODE_NORMAL
	msgbox MossdeepCity_House4_Text_Skitty, MSGBOX_DEFAULT
	waitmoncry
	release
	end

MossdeepCity_House4_Text_BrotherLikesToFindBases:
	.string "My little brother finds hideouts\nin the bushes. He never says\lwhose they are.$"

MossdeepCity_House4_Text_BrotherLikesToVisitBasesAndBattle:
	.string "My brother says the hideouts all\nhave people in them now, and\levery one of them wants a\lbattle.\pHe comes home sunburnt and\nhappy.$"

MossdeepCity_House4_Text_YouMadeSecretBaseNearX:
	.string "Was that your hideout near\n{STR_VAR_1}? I sat in it.\pI didn't touch anything.\nMuch.$"

MossdeepCity_House4_Text_MakeSecretBase:
	.string "You should make a hideout\nsomewhere. A tree, a cave, a\lbush. I'll find it. I always do.$"

MossdeepCity_House4_Text_Skitty:
	.string "SKITTY: Miyaan?$"

