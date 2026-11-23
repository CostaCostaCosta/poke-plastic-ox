AncientTomb_MapScripts::
	map_script MAP_SCRIPT_ON_RESUME, AncientTomb_OnResume
	map_script MAP_SCRIPT_ON_LOAD, AncientTomb_OnLoad
	map_script MAP_SCRIPT_ON_TRANSITION, AncientTomb_OnTransition
	.byte 0

AncientTomb_OnResume:
	call_if_set FLAG_SYS_CTRL_OBJ_DELETE, AncientTomb_EventScript_TryRemoveRegisteel
	end

AncientTomb_EventScript_TryRemoveRegisteel::
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_ne VAR_RESULT, B_OUTCOME_CAUGHT, Common_EventScript_NopReturn
	removeobject VAR_LAST_TALKED
	return

@ Plastic Ox: the inner chamber opens only while the player carries the
@ ANCIENT STEEL TABLET. No braille, Sealed Chamber or step puzzle.
AncientTomb_OnLoad:
	checkitem ITEM_ANCIENT_STEEL_TABLET
	call_if_eq VAR_RESULT, FALSE, AncientTomb_EventScript_HideRegiEntrance
	end

AncientTomb_EventScript_HideRegiEntrance::
	setmetatile 7, 19, METATILE_Cave_EntranceCover, TRUE
	setmetatile 8, 19, METATILE_Cave_EntranceCover, TRUE
	setmetatile 9, 19, METATILE_Cave_EntranceCover, TRUE
	setmetatile 7, 20, METATILE_Cave_SealedChamberBraille_Mid, TRUE
	setmetatile 8, 20, METATILE_Cave_SealedChamberBraille_Mid, TRUE
	setmetatile 9, 20, METATILE_Cave_SealedChamberBraille_Mid, TRUE
	return

AncientTomb_OnTransition:
	setflag FLAG_LANDMARK_ANCIENT_TOMB
	call_if_unset FLAG_DEFEATED_REGISTEEL, AncientTomb_EventScript_ShowRegisteel
	end

AncientTomb_EventScript_ShowRegisteel::
	clearflag FLAG_HIDE_REGISTEEL
	return

AncientTomb_EventScript_CaveEntranceMiddle::
AncientTomb_EventScript_CaveEntranceSide::
	lockall
	checkitem ITEM_ANCIENT_STEEL_TABLET
	goto_if_eq VAR_RESULT, TRUE, AncientTomb_EventScript_SealOpen
	msgbox AncientTomb_Text_Sealed, MSGBOX_DEFAULT
	releaseall
	end

AncientTomb_EventScript_SealOpen::
	msgbox AncientTomb_Text_SealOpen, MSGBOX_DEFAULT
	releaseall
	end

AncientTomb_EventScript_Registeel::
	goto PoxTournament_Registeel

AncientTomb_EventScript_DefeatedRegisteel::
	setflag FLAG_DEFEATED_REGISTEEL
	goto Common_EventScript_RemoveStaticPokemon
	end

AncientTomb_EventScript_RanFromRegisteel::
	setvar VAR_0x8004, SPECIES_REGISTEEL
	goto Common_EventScript_LegendaryFlewAway
	end

AncientTomb_Text_Sealed:
	.string "A dark metal plate seals the far\n"
	.string "wall. At its center is a polished\p"
	.string "recess the size of a tablet.$"

AncientTomb_Text_SealOpen:
	.string "The ANCIENT STEEL TABLET rings\n"
	.string "faintly in the BAG. The metal\p"
	.string "plate has slid aside.$"
