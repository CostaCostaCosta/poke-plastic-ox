EventScript_PocketWatch::
	lockall
	msgbox PocketWatch_Text_SetTime, MSGBOX_DEFAULT
	fadescreen FADE_TO_BLACK
	special StartWallClock
	msgbox PocketWatch_Text_SetWeekday, MSGBOX_DEFAULT
	multichoice 16, 0, MULTI_POCKET_WATCH_WEEKDAYS, TRUE
	special Special_SetPocketWatchWeekday
	msgbox PocketWatch_Text_Finished, MSGBOX_DEFAULT
	releaseall
	end

PocketWatch_Text_SetTime::
	.string "Turn the hands to set the time.$"

PocketWatch_Text_SetWeekday::
	.string "Which day of the week is it?$"

PocketWatch_Text_Finished::
	.string "The POCKET WATCH is set.$"

EventScript_TrainingKit::
	lockall
	getpartysize
	goto_if_eq VAR_RESULT, 0, TrainingKit_NoPokemon
	special ChoosePartyMon
	goto_if_ge VAR_0x8004, PARTY_SIZE, TrainingKit_Close
	specialvar VAR_RESULT, ScriptGetPartyMonSpecies
	goto_if_eq VAR_RESULT, SPECIES_EGG, TrainingKit_Egg
TrainingKit_ActionMenu::
	dynmultipush TrainingKit_Text_Nature, 0
	dynmultipush TrainingKit_Text_EVs, 1
	dynmultipush TrainingKit_Text_ChooseAnother, 2
	dynmultipush TrainingKit_Text_Close, 3
	dynmultistack 0, 0, FALSE, 4, FALSE, 0, NULL
	switch VAR_RESULT
	case 0, TrainingKit_NatureMenu
	case 1, TrainingKit_EVStatMenu
	case 2, EventScript_TrainingKit
	goto TrainingKit_Close

TrainingKit_NatureMenu::
	dynmultipush Debug_EventScript_ChangeNature_Text_Hardy, 0
	dynmultipush Debug_EventScript_ChangeNature_Text_Lonely, 1
	dynmultipush Debug_EventScript_ChangeNature_Text_Brave, 2
	dynmultipush Debug_EventScript_ChangeNature_Text_Adamant, 3
	dynmultipush Debug_EventScript_ChangeNature_Text_Naughty, 4
	dynmultipush Debug_EventScript_ChangeNature_Text_Bold, 5
	dynmultipush Debug_EventScript_ChangeNature_Text_Docile, 6
	dynmultipush Debug_EventScript_ChangeNature_Text_Relaxed, 7
	dynmultipush Debug_EventScript_ChangeNature_Text_Impish, 8
	dynmultipush Debug_EventScript_ChangeNature_Text_Lax, 9
	dynmultipush Debug_EventScript_ChangeNature_Text_Timid, 10
	dynmultipush Debug_EventScript_ChangeNature_Text_Hasty, 11
	dynmultipush Debug_EventScript_ChangeNature_Text_Serious, 12
	dynmultipush Debug_EventScript_ChangeNature_Text_Jolly, 13
	dynmultipush Debug_EventScript_ChangeNature_Text_Naive, 14
	dynmultipush Debug_EventScript_ChangeNature_Text_Modest, 15
	dynmultipush Debug_EventScript_ChangeNature_Text_Mild, 16
	dynmultipush Debug_EventScript_ChangeNature_Text_Quiet, 17
	dynmultipush Debug_EventScript_ChangeNature_Text_Bashful, 18
	dynmultipush Debug_EventScript_ChangeNature_Text_Rash, 19
	dynmultipush Debug_EventScript_ChangeNature_Text_Calm, 20
	dynmultipush Debug_EventScript_ChangeNature_Text_Gentle, 21
	dynmultipush Debug_EventScript_ChangeNature_Text_Sassy, 22
	dynmultipush Debug_EventScript_ChangeNature_Text_Careful, 23
	dynmultipush Debug_EventScript_ChangeNature_Text_Quirky, 24
	dynmultistack 0, 0, TRUE, 7, FALSE, 0, NULL
	goto_if_eq VAR_RESULT, MULTI_B_PRESSED, TrainingKit_ActionMenu
	special SetHiddenNature
	msgbox TrainingKit_Text_NatureSet, MSGBOX_DEFAULT
	goto TrainingKit_ActionMenu

TrainingKit_EVStatMenu::
	dynmultipush TrainingKit_Text_HP, 0
	dynmultipush TrainingKit_Text_Attack, 1
	dynmultipush TrainingKit_Text_Defense, 2
	dynmultipush TrainingKit_Text_Speed, 3
	dynmultipush TrainingKit_Text_SpAttack, 4
	dynmultipush TrainingKit_Text_SpDefense, 5
	dynmultipush TrainingKit_Text_Back, 6
	dynmultistack 0, 0, FALSE, 7, FALSE, 0, NULL
	goto_if_ge VAR_RESULT, 6, TrainingKit_ActionMenu
	copyvar VAR_0x8005, VAR_RESULT
TrainingKit_EVValueMenu::
	dynmultipush TrainingKit_Text_EV000, 0
	dynmultipush TrainingKit_Text_EV004, 4
	dynmultipush TrainingKit_Text_EV008, 8
	dynmultipush TrainingKit_Text_EV012, 12
	dynmultipush TrainingKit_Text_EV016, 16
	dynmultipush TrainingKit_Text_EV020, 20
	dynmultipush TrainingKit_Text_EV024, 24
	dynmultipush TrainingKit_Text_EV028, 28
	dynmultipush TrainingKit_Text_EV032, 32
	dynmultipush TrainingKit_Text_EV036, 36
	dynmultipush TrainingKit_Text_EV040, 40
	dynmultipush TrainingKit_Text_EV044, 44
	dynmultipush TrainingKit_Text_EV048, 48
	dynmultipush TrainingKit_Text_EV052, 52
	dynmultipush TrainingKit_Text_EV056, 56
	dynmultipush TrainingKit_Text_EV060, 60
	dynmultipush TrainingKit_Text_EV064, 64
	dynmultipush TrainingKit_Text_EV068, 68
	dynmultipush TrainingKit_Text_EV072, 72
	dynmultipush TrainingKit_Text_EV076, 76
	dynmultipush TrainingKit_Text_EV080, 80
	dynmultipush TrainingKit_Text_EV084, 84
	dynmultipush TrainingKit_Text_EV088, 88
	dynmultipush TrainingKit_Text_EV092, 92
	dynmultipush TrainingKit_Text_EV096, 96
	dynmultipush TrainingKit_Text_EV100, 100
	dynmultipush TrainingKit_Text_EV104, 104
	dynmultipush TrainingKit_Text_EV108, 108
	dynmultipush TrainingKit_Text_EV112, 112
	dynmultipush TrainingKit_Text_EV116, 116
	dynmultipush TrainingKit_Text_EV120, 120
	dynmultipush TrainingKit_Text_EV124, 124
	dynmultipush TrainingKit_Text_EV128, 128
	dynmultipush TrainingKit_Text_EV132, 132
	dynmultipush TrainingKit_Text_EV136, 136
	dynmultipush TrainingKit_Text_EV140, 140
	dynmultipush TrainingKit_Text_EV144, 144
	dynmultipush TrainingKit_Text_EV148, 148
	dynmultipush TrainingKit_Text_EV152, 152
	dynmultipush TrainingKit_Text_EV156, 156
	dynmultipush TrainingKit_Text_EV160, 160
	dynmultipush TrainingKit_Text_EV164, 164
	dynmultipush TrainingKit_Text_EV168, 168
	dynmultipush TrainingKit_Text_EV172, 172
	dynmultipush TrainingKit_Text_EV176, 176
	dynmultipush TrainingKit_Text_EV180, 180
	dynmultipush TrainingKit_Text_EV184, 184
	dynmultipush TrainingKit_Text_EV188, 188
	dynmultipush TrainingKit_Text_EV192, 192
	dynmultipush TrainingKit_Text_EV196, 196
	dynmultipush TrainingKit_Text_EV200, 200
	dynmultipush TrainingKit_Text_EV204, 204
	dynmultipush TrainingKit_Text_EV208, 208
	dynmultipush TrainingKit_Text_EV212, 212
	dynmultipush TrainingKit_Text_EV216, 216
	dynmultipush TrainingKit_Text_EV220, 220
	dynmultipush TrainingKit_Text_EV224, 224
	dynmultipush TrainingKit_Text_EV228, 228
	dynmultipush TrainingKit_Text_EV232, 232
	dynmultipush TrainingKit_Text_EV236, 236
	dynmultipush TrainingKit_Text_EV240, 240
	dynmultipush TrainingKit_Text_EV244, 244
	dynmultipush TrainingKit_Text_EV248, 248
	dynmultipush TrainingKit_Text_EV252, 252
	dynmultipush TrainingKit_Text_Back, 253
	dynmultistack 0, 0, FALSE, 7, FALSE, 0, NULL
	goto_if_eq VAR_RESULT, 253, TrainingKit_EVStatMenu
	goto_if_eq VAR_RESULT, MULTI_B_PRESSED, TrainingKit_EVStatMenu
	copyvar VAR_0x8006, VAR_RESULT
	special SetTrainingKitEVs
	msgbox TrainingKit_Text_EVsSet, MSGBOX_DEFAULT
	goto TrainingKit_EVStatMenu

TrainingKit_Egg::
	msgbox TrainingKit_Text_Egg, MSGBOX_DEFAULT
	goto EventScript_TrainingKit
TrainingKit_NoPokemon::
	msgbox TrainingKit_Text_NoPokemon, MSGBOX_DEFAULT
TrainingKit_Close::
	releaseall
	end

TrainingKit_Text_Nature:
	.string "Set nature$"
TrainingKit_Text_EVs:
	.string "Set EVs$"
TrainingKit_Text_ChooseAnother:
	.string "Choose another$"
TrainingKit_Text_Close:
	.string "Close$"
TrainingKit_Text_HP:
	.string "HP$"
TrainingKit_Text_Attack:
	.string "Attack$"
TrainingKit_Text_Defense:
	.string "Defense$"
TrainingKit_Text_Speed:
	.string "Speed$"
TrainingKit_Text_SpAttack:
	.string "Sp. Atk$"
TrainingKit_Text_SpDefense:
	.string "Sp. Def$"
TrainingKit_Text_EV000:
	.string "0 EVs$"
TrainingKit_Text_EV004:
	.string "4 EVs$"
TrainingKit_Text_EV008:
	.string "8 EVs$"
TrainingKit_Text_EV012:
	.string "12 EVs$"
TrainingKit_Text_EV016:
	.string "16 EVs$"
TrainingKit_Text_EV020:
	.string "20 EVs$"
TrainingKit_Text_EV024:
	.string "24 EVs$"
TrainingKit_Text_EV028:
	.string "28 EVs$"
TrainingKit_Text_EV032:
	.string "32 EVs$"
TrainingKit_Text_EV036:
	.string "36 EVs$"
TrainingKit_Text_EV040:
	.string "40 EVs$"
TrainingKit_Text_EV044:
	.string "44 EVs$"
TrainingKit_Text_EV048:
	.string "48 EVs$"
TrainingKit_Text_EV052:
	.string "52 EVs$"
TrainingKit_Text_EV056:
	.string "56 EVs$"
TrainingKit_Text_EV060:
	.string "60 EVs$"
TrainingKit_Text_EV064:
	.string "64 EVs$"
TrainingKit_Text_EV068:
	.string "68 EVs$"
TrainingKit_Text_EV072:
	.string "72 EVs$"
TrainingKit_Text_EV076:
	.string "76 EVs$"
TrainingKit_Text_EV080:
	.string "80 EVs$"
TrainingKit_Text_EV084:
	.string "84 EVs$"
TrainingKit_Text_EV088:
	.string "88 EVs$"
TrainingKit_Text_EV092:
	.string "92 EVs$"
TrainingKit_Text_EV096:
	.string "96 EVs$"
TrainingKit_Text_EV100:
	.string "100 EVs$"
TrainingKit_Text_EV104:
	.string "104 EVs$"
TrainingKit_Text_EV108:
	.string "108 EVs$"
TrainingKit_Text_EV112:
	.string "112 EVs$"
TrainingKit_Text_EV116:
	.string "116 EVs$"
TrainingKit_Text_EV120:
	.string "120 EVs$"
TrainingKit_Text_EV124:
	.string "124 EVs$"
TrainingKit_Text_EV128:
	.string "128 EVs$"
TrainingKit_Text_EV132:
	.string "132 EVs$"
TrainingKit_Text_EV136:
	.string "136 EVs$"
TrainingKit_Text_EV140:
	.string "140 EVs$"
TrainingKit_Text_EV144:
	.string "144 EVs$"
TrainingKit_Text_EV148:
	.string "148 EVs$"
TrainingKit_Text_EV152:
	.string "152 EVs$"
TrainingKit_Text_EV156:
	.string "156 EVs$"
TrainingKit_Text_EV160:
	.string "160 EVs$"
TrainingKit_Text_EV164:
	.string "164 EVs$"
TrainingKit_Text_EV168:
	.string "168 EVs$"
TrainingKit_Text_EV172:
	.string "172 EVs$"
TrainingKit_Text_EV176:
	.string "176 EVs$"
TrainingKit_Text_EV180:
	.string "180 EVs$"
TrainingKit_Text_EV184:
	.string "184 EVs$"
TrainingKit_Text_EV188:
	.string "188 EVs$"
TrainingKit_Text_EV192:
	.string "192 EVs$"
TrainingKit_Text_EV196:
	.string "196 EVs$"
TrainingKit_Text_EV200:
	.string "200 EVs$"
TrainingKit_Text_EV204:
	.string "204 EVs$"
TrainingKit_Text_EV208:
	.string "208 EVs$"
TrainingKit_Text_EV212:
	.string "212 EVs$"
TrainingKit_Text_EV216:
	.string "216 EVs$"
TrainingKit_Text_EV220:
	.string "220 EVs$"
TrainingKit_Text_EV224:
	.string "224 EVs$"
TrainingKit_Text_EV228:
	.string "228 EVs$"
TrainingKit_Text_EV232:
	.string "232 EVs$"
TrainingKit_Text_EV236:
	.string "236 EVs$"
TrainingKit_Text_EV240:
	.string "240 EVs$"
TrainingKit_Text_EV244:
	.string "244 EVs$"
TrainingKit_Text_EV248:
	.string "248 EVs$"
TrainingKit_Text_EV252:
	.string "252 EVs$"
TrainingKit_Text_Back:
	.string "Back$"
TrainingKit_Text_NatureSet:
	.string "The POKéMON's nature was set.$"
TrainingKit_Text_EVsSet:
	.string "Its EVs were set within the 510-point limit.$"
TrainingKit_Text_Egg:
	.string "The TRAINING KIT can't be used on an EGG.$"
TrainingKit_Text_NoPokemon:
	.string "There are no POKéMON in the party.$"
