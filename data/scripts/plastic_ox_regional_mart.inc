PoxRegionalMart::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart PoxRegionalMart_Stock
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end
	.align 2
PoxRegionalMart_Stock:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_SUPER_POTION
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_REVIVE
	.2byte ITEM_FULL_HEAL
	.2byte ITEM_REPEL
	.2byte ITEM_LEFTOVERS
	.2byte ITEM_NONE
