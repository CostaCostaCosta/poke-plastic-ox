CinnabarIsland_Mart_Frlg_MapScripts::
	.byte 0

CinnabarIsland_Mart_EventScript_Woman::
	msgbox CinnabarIsland_Mart_Text_DontTheyHaveXAttack, MSGBOX_NPC
	end

CinnabarIsland_Mart_EventScript_Scientist::
	msgbox CinnabarIsland_Mart_Text_ExtraItemsNeverHurt, MSGBOX_NPC
	end

CinnabarIsland_Mart_EventScript_Clerk::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	pokemart CinnabarIsland_Mart_Items
	msgbox gText_PleaseComeAgain
	release
	end

	.align 2
CinnabarIsland_Mart_Items::
	.2byte ITEM_ULTRA_BALL
	.2byte ITEM_GREAT_BALL
	.2byte ITEM_HYPER_POTION
	.2byte ITEM_REVIVE
	.2byte ITEM_FULL_HEAL
	.2byte ITEM_ESCAPE_ROPE
	.2byte ITEM_MAX_REPEL
	.2byte ITEM_LEFTOVERS
	.2byte ITEM_NONE
	release
	end

CinnabarIsland_Mart_Text_DontTheyHaveXAttack::
	.string "The shelves fill up when a boat\ngets in, and not before.\pBuy the REVIVES while you're\nlooking at them.$"

CinnabarIsland_Mart_Text_ExtraItemsNeverHurt::
	.string "Two ESCAPE ROPES. I'm going back\ninto the old house for my\lnotebooks, and I am not walking\lout the long way.$"

