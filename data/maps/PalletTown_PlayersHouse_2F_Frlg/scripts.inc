PalletTown_PlayersHouse_2F_Frlg_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, Pox_Bedroom_OnFrame
	.byte 0

PalletTown_PlayersHouse_2F_EventScript_NES::
	msgbox PalletTown_PlayersHouse_2F_Text_PlayedWithNES, MSGBOX_SIGN
	end

PalletTown_PlayersHouse_2F_EventScript_Sign::
	msgbox PalletTown_PlayersHouse_2F_Text_PressLRForHelp, MSGBOX_SIGN
	end

PalletTown_PlayersHouse_2F_Text_PlayedWithNES::
	.string "{PLAYER} played with the NES.\p"
	.string "…Okay!\n"
	.string "It's time to go!$"

PalletTown_PlayersHouse_2F_Text_PressLRForHelp::
	.string "It's a posted notice…\p"
	.string "A: Talk or examine. START: Menu.\n"
	.string "Remember to save your adventure!$"


@ New-game-only truck-like rumble, jolt, and fading aftershocks.
Pox_Bedroom_OnFrame:
    map_script_2 VAR_TEMP_1, 0, Pox_BedroomIntro
    .2byte 0

Pox_BedroomIntro:
    setvar VAR_TEMP_1, 1
    goto_if_unset FLAG_POX_INTRO_QUAKE_PENDING, Pox_End
    lockall
    delay 30
    setvar VAR_0x8004, 2
    setvar VAR_0x8005, 1
    setvar VAR_0x8006, 40
    setvar VAR_0x8007, 3
    special ShakeCamera
    playse SE_TRUCK_MOVE
    waitstate
    setvar VAR_0x8004, 4
    setvar VAR_0x8005, 2
    setvar VAR_0x8006, 24
    setvar VAR_0x8007, 3
    special ShakeCamera
    waitstate
    setvar VAR_0x8004, 1
    setvar VAR_0x8005, 0
    setvar VAR_0x8006, 20
    setvar VAR_0x8007, 4
    special ShakeCamera
    playse SE_TRUCK_STOP
    waitstate
    delay 30
    msgbox Pox_Text_BedroomQuake, MSGBOX_DEFAULT
    clearflag FLAG_POX_INTRO_QUAKE_PENDING
    releaseall
    end

Pox_Text_BedroomQuake::
	.string "The floor jolts beneath your feet!\pOutside, a low rumble rolls\nacross PALLET TOWN...\pThe shaking finally settles.\pPROFESSOR BIRCH said to meet\nhim at OAK's LAB.$"

