DarkCave_SouthSide_hns_MapScripts::
	.byte 0

DarkCave1_EventScript_RockSmashKeyHiker::
	lock
	faceplayer
	checkitem ITEM_ROCK_SMASH_KEY
	goto_if_eq VAR_RESULT, TRUE, DarkCave1_EventScript_AlreadyHasRockSmashKey
	msgbox DarkCave1_Text_RockSmashKeyIntro, MSGBOX_DEFAULT
	giveitem ITEM_ROCK_SMASH_KEY
	goto_if_eq VAR_RESULT, FALSE, DarkCave1_EventScript_RockSmashKeyPocketFull
	msgbox DarkCave1_Text_ReceivedRockSmashKey, MSGBOX_DEFAULT
	release
	end

DarkCave1_EventScript_AlreadyHasRockSmashKey::
	msgbox DarkCave1_Text_RockSmashKeyReminder, MSGBOX_DEFAULT
	release
	end

DarkCave1_EventScript_RockSmashKeyPocketFull::
	msgbox DarkCave1_Text_RockSmashKeyPocketFull, MSGBOX_DEFAULT
	release
	end

DarkCave1_Text_RockSmashKeyIntro:
	.string "That cracked rock blocks the way?\nTake this ROCK SMASH KEY!$"

DarkCave1_Text_ReceivedRockSmashKey:
	.string "Now you can smash cracked rocks\nwithout a POKéMON's help.$"

DarkCave1_Text_RockSmashKeyReminder:
	.string "Use the ROCK SMASH KEY on cracked\nrocks to clear your path.$"

DarkCave1_Text_RockSmashKeyPocketFull:
	.string "Your KEY ITEMS pocket is full.\nMake room and come back.$"

DarkCave1_EventScript_ItemPotion::
	finditem ITEM_POTION
	end

DarkCave1_EventScript_ItemRevive::
	finditem ITEM_REVIVE
	end

DarkCave1_EventScript_ItemMaxRevive::
	finditem ITEM_MAX_REVIVE
	end

DarkCave1_EventScript_ItemElixir::
	finditem ITEM_ELIXIR
	end
