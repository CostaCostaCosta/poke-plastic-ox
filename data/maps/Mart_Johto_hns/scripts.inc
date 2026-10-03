Mart_Johto_hns_MapScripts::
	.byte 0

Mart_Johto_hns_EventScript_Clerk::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart Mart_Johto_hns_Pokemart
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
Mart_Johto_hns_Pokemart:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_REPEL
	pokemartlistend

Mart_Johto_hns_EventScript_Youngster::
	lock
	faceplayer
	msgbox Mart_Johto_hns_Text_Youngster, MSGBOX_DEFAULT
	release
	end

Mart_Johto_hns_Text_Youngster:
	.string "The clerk says the delivery trucks\n"
	.string "don't need roads anymore.\p"
	.string "How does THAT work?$"
