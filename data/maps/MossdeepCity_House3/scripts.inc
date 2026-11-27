MossdeepCity_House3_MapScripts::
	.byte 0

MossdeepCity_House3_EventScript_SuperRodFisherman::
	lock
	faceplayer
	goto_if_set FLAG_RECEIVED_SUPER_ROD, MossdeepCity_House3_EventScript_ReceivedSuperRod
	msgbox MossdeepCity_House3_Text_YouWantSuperRod, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, MossdeepCity_House3_EventScript_DeclineSuperRod
	msgbox MossdeepCity_House3_Text_SuperRodIsSuper, MSGBOX_DEFAULT
	giveitem ITEM_SUPER_ROD
	goto_if_eq VAR_RESULT, FALSE, Common_EventScript_ShowBagIsFull
	setflag FLAG_RECEIVED_SUPER_ROD
	msgbox MossdeepCity_House3_Text_TryDroppingRodInWater, MSGBOX_DEFAULT
	release
	end

MossdeepCity_House3_EventScript_ReceivedSuperRod::
	msgbox MossdeepCity_House3_Text_GoAfterSeafloorPokemon, MSGBOX_DEFAULT
	release
	end

MossdeepCity_House3_EventScript_DeclineSuperRod::
	msgbox MossdeepCity_House3_Text_DontYouLikeToFish, MSGBOX_DEFAULT
	release
	end

MossdeepCity_House3_Text_YouWantSuperRod:
	.string "You crossed the sound with a\nstarter rod? I have a SUPER ROD\lhere I've outgrown.\pIt drops past the shelf to where\nthe big ones sit. Do you want\lit?$"

MossdeepCity_House3_Text_SuperRodIsSuper:
	.string "Good. Don't let the tide take\nit.$"

MossdeepCity_House3_Text_TryDroppingRodInWater:
	.string "Try it off the east pier at the\nturn of the tide. That's when\lthe deep water comes up to look.$"

MossdeepCity_House3_Text_DontYouLikeToFish:
	.string "No? Suit yourself. It'll keep.$"

MossdeepCity_House3_Text_GoAfterSeafloorPokemon:
	.string "Caught anything off the shelf\nyet? Don't tell me the size.\lEverybody on this island lies\labout the size.$"

