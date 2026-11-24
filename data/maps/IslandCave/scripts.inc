IslandCave_MapScripts::
	map_script MAP_SCRIPT_ON_RESUME, IslandCave_OnResume
	map_script MAP_SCRIPT_ON_LOAD, IslandCave_OnLoad
	map_script MAP_SCRIPT_ON_TRANSITION, IslandCave_OnTransition
	.byte 0

IslandCave_OnResume:
	call_if_set FLAG_SYS_CTRL_OBJ_DELETE, IslandCave_EventScript_TryRemoveRegice
	end

IslandCave_EventScript_TryRemoveRegice::
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_ne VAR_RESULT, B_OUTCOME_CAUGHT, Common_EventScript_NopReturn
	removeobject VAR_LAST_TALKED
	return

@ Plastic Ox: the inner chamber opens only while the player carries the
@ ANCIENT ICE TABLET. No braille, Sealed Chamber or step puzzle.
IslandCave_OnLoad:
	checkitem ITEM_ANCIENT_ICE_TABLET
	call_if_eq VAR_RESULT, FALSE, IslandCave_EventScript_HideRegiEntrance
	end

IslandCave_EventScript_HideRegiEntrance::
	setmetatile 7, 19, METATILE_Cave_EntranceCover, TRUE
	setmetatile 8, 19, METATILE_Cave_EntranceCover, TRUE
	setmetatile 9, 19, METATILE_Cave_EntranceCover, TRUE
	setmetatile 7, 20, METATILE_Cave_SealedChamberBraille_Mid, TRUE
	setmetatile 8, 20, METATILE_Cave_SealedChamberBraille_Mid, TRUE
	setmetatile 9, 20, METATILE_Cave_SealedChamberBraille_Mid, TRUE
	return

IslandCave_OnTransition:
	setflag FLAG_LANDMARK_ISLAND_CAVE
	call_if_unset FLAG_DEFEATED_REGICE, IslandCave_EventScript_ShowRegice
	end

IslandCave_EventScript_ShowRegice::
	clearflag FLAG_HIDE_REGICE
	return

IslandCave_EventScript_CaveEntranceMiddle::
IslandCave_EventScript_CaveEntranceSide::
	lockall
	checkitem ITEM_ANCIENT_ICE_TABLET
	goto_if_eq VAR_RESULT, TRUE, IslandCave_EventScript_SealOpen
	msgbox IslandCave_Text_Sealed, MSGBOX_DEFAULT
	releaseall
	end

IslandCave_EventScript_SealOpen::
	msgbox IslandCave_Text_SealOpen, MSGBOX_DEFAULT
	releaseall
	end

@ Still referenced by the vanilla braille step puzzle in field_control_avatar.c;
@ Plastic Ox never starts that puzzle, so it only needs to exist.
IslandCave_EventScript_OpenRegiEntrance::
	end

IslandCave_EventScript_Regice::
	goto PoxTournament_Regice

IslandCave_EventScript_DefeatedRegice::
	setflag FLAG_DEFEATED_REGICE
	goto Common_EventScript_RemoveStaticPokemon
	end

IslandCave_EventScript_RanFromRegice::
	setvar VAR_0x8004, SPECIES_REGICE
	goto Common_EventScript_LegendaryFlewAway
	end

IslandCave_Text_Sealed:
	.string "A slab of frozen stone seals the\n"
	.string "far wall. Frost rims a hollow\p"
	.string "shaped like a tablet.$"

IslandCave_Text_SealOpen:
	.string "The ANCIENT ICE TABLET is cold\n"
	.string "even through the BAG. The frost\p"
	.string "has drawn back from the passage.$"
