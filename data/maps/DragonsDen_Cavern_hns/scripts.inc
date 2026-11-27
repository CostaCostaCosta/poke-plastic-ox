DragonsDen_Cavern_hns_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PoxDragonsDen_OnTransition
	.byte 0

@ Post-game Dragon's Den: RAYQUAZA on the shrine plaza.
@ FLAG_POX_DEN_RAYQUAZA_ARRIVED  the arrival scene has played (it plays once)
@ FLAG_POX_CAUGHT_RAYQUAZA       caught; it never returns
@ The object is hidden by FLAG_TEMP_1, which this script sets on every entry
@ until RAYQUAZA has arrived and again once it is caught. VAR_TEMP_1 disarms
@ the three plaza triggers once the scene has played.
PoxDragonsDen_OnTransition:
	call_if_unset FLAG_POX_DEN_RAYQUAZA_ARRIVED, PoxDragonsDen_HideRayquaza
	call_if_set FLAG_POX_CAUGHT_RAYQUAZA, PoxDragonsDen_HideRayquaza
	call_if_set FLAG_POX_DEN_RAYQUAZA_ARRIVED, PoxDragonsDen_DisarmArrival
	end

PoxDragonsDen_HideRayquaza:
	setflag FLAG_TEMP_1
	return

PoxDragonsDen_DisarmArrival:
	setvar VAR_TEMP_1, 1
	return

@ First step onto the shrine plaza: the cavern shakes, something roars far
@ overhead, the screen whites out, and RAYQUAZA is there, uncoiling.
PoxDragonsDen_RayquazaArrives::
	lockall
	setvar VAR_TEMP_1, 1
	fadeoutbgm 1
	applymovement LOCALID_PLAYER, Common_Movement_FaceDown
	waitmovement 0
	delay 30
	playse SE_M_EARTHQUAKE
	setvar VAR_0x8004, 1  @ vertical pan
	setvar VAR_0x8005, 1  @ horizontal pan
	setvar VAR_0x8006, 10 @ num shakes
	setvar VAR_0x8007, 4  @ shake delay
	special ShakeCamera
	waitstate
	waitse
	applymovement LOCALID_PLAYER, Common_Movement_ExclamationMark
	waitmovement 0
	applymovement LOCALID_PLAYER, Common_Movement_FaceUp
	waitmovement 0
	playmoncry SPECIES_RAYQUAZA, CRY_MODE_ENCOUNTER
	delay 50
	waitmoncry
	applymovement LOCALID_PLAYER, Common_Movement_FaceDown
	waitmovement 0
	special SpawnCameraObject
	applymovement LOCALID_CAMERA, PoxDragonsDen_Movement_CameraToPlaza
	waitmovement 0
	playse SE_THUNDER
	fadescreenspeed FADE_TO_WHITE, 0
	clearflag FLAG_TEMP_1
	addobject LOCALID_DRAGONS_DEN_RAYQUAZA
	applymovement LOCALID_DRAGONS_DEN_RAYQUAZA, PoxDragonsDen_Movement_RayquazaHover
	waitmovement 0
	delay 20
	fadescreenspeed FADE_FROM_WHITE, 4
	applymovement LOCALID_DRAGONS_DEN_RAYQUAZA, PoxDragonsDen_Movement_RayquazaLand
	waitmovement 0
	waitse
	playmoncry SPECIES_RAYQUAZA, CRY_MODE_ENCOUNTER
	setvar VAR_0x8004, 1
	setvar VAR_0x8005, 2
	setvar VAR_0x8006, 8
	setvar VAR_0x8007, 5
	special ShakeCamera
	waitstate
	waitmoncry
	applymovement LOCALID_DRAGONS_DEN_RAYQUAZA, PoxDragonsDen_Movement_RayquazaCoil
	waitmovement 0
	msgbox PoxDragonsDen_Text_RayquazaArrived, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_CAMERA, PoxDragonsDen_Movement_CameraBack
	waitmovement 0
	special RemoveCameraObject
	setflag FLAG_POX_DEN_RAYQUAZA_ARRIVED
	fadeinbgm 1
	releaseall
	end

@ An ordinary wild battle: no guaranteed capture. Only a catch removes it;
@ fainting it, fleeing or losing leaves RAYQUAZA on the plaza.
PoxDragonsDen_Rayquaza::
	lockall
	fadeoutbgm 1
	applymovement LOCALID_DRAGONS_DEN_RAYQUAZA, PoxDragonsDen_Movement_RayquazaRise
	waitmovement 0
	waitse
	playmoncry SPECIES_RAYQUAZA, CRY_MODE_ENCOUNTER
	setvar VAR_0x8004, 1
	setvar VAR_0x8005, 2
	setvar VAR_0x8006, 8
	setvar VAR_0x8007, 3
	special ShakeCamera
	waitstate
	waitmoncry
	playse SE_THUNDER
	fadescreenspeed FADE_TO_WHITE, 0
	fadescreenspeed FADE_FROM_WHITE, 2
	@ Lv.70, or the party's highest level when that is higher.
	setwildbattle SPECIES_RAYQUAZA, 70
	special PoxRaiseWildMonToPartyLevel
	special BattleSetup_StartLegendaryBattle
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, PoxDragonsDen_RayquazaCaught
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, PoxDragonsDen_RayquazaFainted
	applymovement LOCALID_DRAGONS_DEN_RAYQUAZA, PoxDragonsDen_Movement_RayquazaCoil
	waitmovement 0
	releaseall
	end

PoxDragonsDen_RayquazaFainted:
	applymovement LOCALID_DRAGONS_DEN_RAYQUAZA, PoxDragonsDen_Movement_RayquazaCoil
	waitmovement 0
	msgbox PoxDragonsDen_Text_RayquazaUnbowed, MSGBOX_DEFAULT
	releaseall
	end

PoxDragonsDen_RayquazaCaught:
	setflag FLAG_POX_CAUGHT_RAYQUAZA
	fadescreenswapbuffers FADE_TO_BLACK
	removeobject LOCALID_DRAGONS_DEN_RAYQUAZA
	fadescreenswapbuffers FADE_FROM_BLACK
	msgbox PoxDragonsDen_Text_DenQuiet, MSGBOX_DEFAULT
	releaseall
	end

@ RAYQUAZA has unusual movement frames (sAnimTable_Rayquaza):
@ walk_in_place_up = flying, _right = stretched out, _left = coiled, mouth
@ open, _fast_left = coiled, awake, _down = coiled, asleep.
PoxDragonsDen_Movement_RayquazaHover:
	walk_in_place_up
	step_end

PoxDragonsDen_Movement_RayquazaLand:
	delay_16
	delay_16
	walk_in_place_right
	delay_16
	delay_16
	walk_in_place_left
	delay_16
	step_end

PoxDragonsDen_Movement_RayquazaRise:
	walk_in_place_fast_left
	delay_16
	walk_in_place_right
	delay_16
	walk_in_place_left
	delay_8
	step_end

PoxDragonsDen_Movement_RayquazaCoil:
	walk_in_place_fast_left
	delay_16
	step_end

PoxDragonsDen_Movement_CameraToPlaza:
	walk_slow_down
	walk_slow_down
	step_end

PoxDragonsDen_Movement_CameraBack:
	walk_slow_up
	walk_slow_up
	step_end

PoxDragonsDen_ItemPPMax::
	finditem ITEM_PP_MAX
	end

PoxDragonsDen_ItemMaxPotion::
	finditem ITEM_MAX_POTION
	end

PoxDragonsDen_ItemDragonFang::
	finditem ITEM_DRAGON_FANG
	end

PoxDragonsDen_Statue::
	msgbox PoxDragonsDen_Text_Statue, MSGBOX_SIGN
	end

PoxDragonsDen_ShrineDoor::
	msgbox PoxDragonsDen_Text_ShrineDoor, MSGBOX_SIGN
	end

PoxDragonsDen_Text_RayquazaArrived:
	.string "RAYQUAZA came down out of the dark\n"
	.string "and settled in front of the shrine!$"

PoxDragonsDen_Text_RayquazaUnbowed:
	.string "RAYQUAZA shook itself and coiled up\n"
	.string "again. It isn't going anywhere.$"

PoxDragonsDen_Text_DenQuiet:
	.string "The water went still.\n"
	.string "The DEN is quiet again.$"

PoxDragonsDen_Text_Statue:
	.string "A dragon carved from one stone.\n"
	.string "The water has worn its claws smooth.$"

PoxDragonsDen_Text_ShrineDoor:
	.string "The shrine door is barred from\n"
	.string "the inside.$"
