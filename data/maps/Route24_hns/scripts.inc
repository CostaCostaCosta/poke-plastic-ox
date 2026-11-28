Route24_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxRegion_Arrival_Route24_hns
	.byte 0

@ The beaten grunt is gone for good: PoxRegion_Arrival_Route24_hns calls this
@ whenever his trainer flag is set (plastic_ox/alpha/region_v7.py).
Route24_EventScript_HideRocket::
	setflag FLAG_TEMP_11
	return

Route24_EventScript_Npc1::
	trainerbattle_single TRAINER_PLASTIC_OX_ROUTE24_ROCKET, Route24_RocketChallenge_Text, Route24_RocketDefeat_Text, Route24_EventScript_RocketLeaves
	msgbox Route24_EventScript_Npc1_Text, MSGBOX_AUTOCLOSE
	end

@ After the battle he heads south for RUSTBORO and leaves the route.
Route24_EventScript_RocketLeaves::
	msgbox Route24_EventScript_Npc1_Text, MSGBOX_DEFAULT
	closemessage
	getplayerxy VAR_0x8004, VAR_0x8005
	getobjectxy LOCALID_ROUTE24_GRUNT, CURRENT_POSITION, VAR_0x8006, VAR_0x8007
	goto_if_ne VAR_0x8004, VAR_0x8006, Route24_EventScript_RocketWalkSouth
	goto_if_lt VAR_0x8005, VAR_0x8007, Route24_EventScript_RocketWalkSouth
	applymovement LOCALID_ROUTE24_GRUNT, Route24_Movement_RocketSidestepSouth
	waitmovement 0
	goto Route24_EventScript_RocketGone

Route24_EventScript_RocketWalkSouth::
	applymovement LOCALID_ROUTE24_GRUNT, Route24_Movement_RocketWalkSouth
	waitmovement 0
Route24_EventScript_RocketGone::
	removeobject LOCALID_ROUTE24_GRUNT
	release
	end

Route24_Movement_RocketSidestepSouth:
	walk_left
Route24_Movement_RocketWalkSouth:
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
	walk_fast_down
	step_end

Route24_EventScript_Npc2::
	lock
	faceplayer
	msgbox Route24_EventScript_Npc2_Text, MSGBOX_NPC
	release
	end

Route24_EventScript_Npc3::
	lock
	faceplayer
	msgbox Route24_EventScript_Npc3_Text, MSGBOX_NPC
	release
	end

Route24_EventScript_Npc4::
	lock
	faceplayer
	msgbox Route24_EventScript_Npc4_Text, MSGBOX_NPC
	release
	end

Route24_EventScript_Npc1_Text:
	.string "Forget the cave. I'm heading back\nto RUSTBORO. I know where THAT is.\pDon't tell the BOSS you saw me!$"

Route24_RocketChallenge_Text:
	.string "The BOSS sent me to a cave,\nand I ended up on this bridge!\pYou won't tell him, will you?\nThen let's battle!$"

Route24_RocketDefeat_Text:
	.string "Great. Now I'm lost and beaten.$"

Route24_EventScript_Npc2_Text:
	.string "I walk out here after work.\nIt gets the dust off my boots.\pA good battle does more for me\nthan sitting around at home.$"

Route24_EventScript_Npc3_Text:
	.string "RUSTBORO is just south of here.\nThe cottage lies farther north.\pI only meant to take a short\nwalk. I say that every time!$"

Route24_EventScript_Npc4_Text:
	.string "I brought lunch and some bait.\nThey're in separate tins.\pLast time I mixed them up.\nI checked twice today.$"
