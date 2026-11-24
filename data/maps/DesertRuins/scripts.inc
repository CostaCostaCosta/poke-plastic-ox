DesertRuins_MapScripts::
	map_script MAP_SCRIPT_ON_RESUME, DesertRuins_OnResume
	map_script MAP_SCRIPT_ON_LOAD, DesertRuins_OnLoad
	map_script MAP_SCRIPT_ON_TRANSITION, DesertRuins_OnTransition
	.byte 0

DesertRuins_OnResume:
	call_if_set FLAG_SYS_CTRL_OBJ_DELETE, DesertRuins_EventScript_TryRemoveRegirock
	end

DesertRuins_EventScript_TryRemoveRegirock::
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_ne VAR_RESULT, B_OUTCOME_CAUGHT, Common_EventScript_NopReturn
	removeobject VAR_LAST_TALKED
	return

@ Plastic Ox: the inner chamber opens only while the player carries the
@ ANCIENT ROCK TABLET. No braille, Sealed Chamber or step puzzle.
DesertRuins_OnLoad:
	checkitem ITEM_ANCIENT_ROCK_TABLET
	call_if_eq VAR_RESULT, FALSE, DesertRuins_EventScript_HideRegiEntrance
	end

DesertRuins_EventScript_HideRegiEntrance::
	setmetatile 7, 19, METATILE_Cave_EntranceCover, TRUE
	setmetatile 8, 19, METATILE_Cave_EntranceCover, TRUE
	setmetatile 9, 19, METATILE_Cave_EntranceCover, TRUE
	setmetatile 7, 20, METATILE_Cave_SealedChamberBraille_Mid, TRUE
	setmetatile 8, 20, METATILE_Cave_SealedChamberBraille_Mid, TRUE
	setmetatile 9, 20, METATILE_Cave_SealedChamberBraille_Mid, TRUE
	return

DesertRuins_OnTransition:
	setflag FLAG_LANDMARK_DESERT_RUINS
	call_if_unset FLAG_DEFEATED_REGIROCK, DesertRuins_EventScript_ShowRegirock
	end

DesertRuins_EventScript_ShowRegirock::
	clearflag FLAG_HIDE_REGIROCK
	return

DesertRuins_EventScript_CaveEntranceMiddle::
DesertRuins_EventScript_CaveEntranceSide::
	lockall
	checkitem ITEM_ANCIENT_ROCK_TABLET
	goto_if_eq VAR_RESULT, TRUE, DesertRuins_EventScript_SealOpen
	msgbox DesertRuins_Text_Sealed, MSGBOX_DEFAULT
	releaseall
	end

DesertRuins_EventScript_SealOpen::
	msgbox DesertRuins_Text_SealOpen, MSGBOX_DEFAULT
	releaseall
	end

DesertRuins_EventScript_Regirock::
	goto PoxTournament_Regirock

DesertRuins_EventScript_DefeatedRegirock::
	setflag FLAG_DEFEATED_REGIROCK
	goto Common_EventScript_RemoveStaticPokemon
	end

DesertRuins_EventScript_RanFromRegirock::
	setvar VAR_0x8004, SPECIES_REGIROCK
	goto Common_EventScript_LegendaryFlewAway
	end

DesertRuins_Text_Sealed:
	.string "Weathered stone seals the far\n"
	.string "wall. A tablet-shaped hollow is\p"
	.string "cut into it, rough as split\n"
	.string "boulder.$"

DesertRuins_Text_SealOpen:
	.string "The ANCIENT ROCK TABLET is heavy\n"
	.string "in your BAG. Grit has fallen\p"
	.string "away from an open passage.$"
