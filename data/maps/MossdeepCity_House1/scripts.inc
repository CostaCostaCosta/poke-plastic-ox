MossdeepCity_House1_MapScripts::
	.byte 0

MossdeepCity_House1_EventScript_BlackBelt::
	lock
	faceplayer
	bufferleadmonspeciesname STR_VAR_1
	msgbox MossdeepCity_House1_Text_HmmYourPokemon, MSGBOX_DEFAULT
	specialvar VAR_RESULT, GetPokeblockNameByMonNature
	goto_if_eq VAR_RESULT, 0, MossdeepCity_House1_EventScript_NeutralNature
	msgbox MossdeepCity_House1_Text_ItLikesXPokeblocks, MSGBOX_DEFAULT
	release
	end

MossdeepCity_House1_EventScript_NeutralNature::
	msgbox MossdeepCity_House1_Text_DoesntLikeOrDislikePokeblocks, MSGBOX_DEFAULT
	release
	end

MossdeepCity_House1_EventScript_Woman::
	msgbox MossdeepCity_House1_Text_HusbandCanTellPokeblockMonLikes, MSGBOX_NPC
	end

MossdeepCity_House1_Text_HmmYourPokemon:
	.string "Hold still. Your {STR_VAR_1}…$"

MossdeepCity_House1_Text_ItLikesXPokeblocks:
	.string "It likes {STR_VAR_1}S.\nI'd bet the boat on it.\pI cook for the launch crews.\nI know a picky eater on sight.$"

MossdeepCity_House1_Text_DoesntLikeOrDislikePokeblocks:
	.string "It would eat anything you put in\nfront of it. Easy to feed. I\llike that in a POKéMON.$"

MossdeepCity_House1_Text_HusbandCanTellPokeblockMonLikes:
	.string "My husband runs the SPACE CENTER\ncanteen. He reads appetites the\lway the old sailors read\lweather.$"

